from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from services.rag_service import RAGService
from services.chat_service import ChatService
from config import API_HOST, API_PORT

app = FastAPI(
    title="Yak Hole API",
    description="A RAG system for querying personal notes using Ollama",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React Native app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
rag_service = RAGService()
chat_service = ChatService()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[dict] = []

class IngestRequest(BaseModel):
    path: Optional[str] = None
    incremental: bool = True

@app.get("/")
async def root():
    return {"message": "Yak Hole API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "yak-hole"}

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat with your notes using RAG"""
    try:
        # Get relevant documents
        relevant_docs = await rag_service.search_documents(message.message)
        
        # Generate response using Ollama
        response = await rag_service.generate_response(
            query=message.message,
            documents=relevant_docs
        )
        
        # Store chat history
        conversation_id = await chat_service.store_message(
            conversation_id=message.conversation_id,
            user_message=message.message,
            bot_response=response,
            sources=relevant_docs
        )
        
        return ChatResponse(
            response=response,
            conversation_id=conversation_id,
            sources=relevant_docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_documents(request: IngestRequest, background_tasks: BackgroundTasks):
    """Ingest documents into the vector database"""
    try:
        background_tasks.add_task(
            rag_service.ingest_documents,
            path=request.path,
            incremental=request.incremental
        )
        return {"message": "Document ingestion started", "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingest/status")
async def get_ingest_status():
    """Get the status of document ingestion"""
    try:
        status = await rag_service.get_ingestion_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations")
async def get_conversations():
    """Get list of recent conversations"""
    try:
        conversations = await chat_service.get_conversations()
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation by ID"""
    try:
        conversation = await chat_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a specific conversation"""
    try:
        success = await chat_service.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        stats = await rag_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)