import os
import asyncio
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import json
import hashlib
from datetime import datetime

from config import (
    VECTOR_DB_PATH, EMBEDDING_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL,
    NOTES_DIR, SUPPORTED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP, BATCH_SIZE
)
from .document_processor import DocumentProcessor

class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection(
            name="notes",
            metadata={"hnsw:space": "cosine"}
        )
        self.document_processor = DocumentProcessor()
        self.ingestion_status = {"status": "idle", "progress": 0, "message": ""}
        
    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    async def generate_response(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response using Ollama with retrieved documents"""
        try:
            # Prepare context from retrieved documents
            context = "\n\n".join([
                f"Source: {doc['metadata'].get('filename', 'Unknown')}\n{doc['content']}"
                for doc in documents
            ])
            
            # Create prompt
            prompt = f"""Based on the following personal notes and documents, please answer the question. If the information isn't available in the provided context, please say so.

Context from your notes:
{context}

Question: {query}

Answer:"""
            
            # Call Ollama API
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "Sorry, I couldn't generate a response.")
                else:
                    return f"Error: Could not reach Ollama (status: {response.status_code})"
                    
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    async def ingest_documents(self, path: Optional[str] = None, incremental: bool = True):
        """Ingest documents from the specified path"""
        try:
            self.ingestion_status = {"status": "processing", "progress": 0, "message": "Starting ingestion..."}
            
            # Use configured NOTES_DIR if no path specified
            if path is None:
                path = NOTES_DIR
            else:
                path = Path(path)
            
            # Find all supported files
            all_files = []
            for ext in SUPPORTED_EXTENSIONS:
                all_files.extend(list(Path(path).rglob(f"*{ext}")))
            
            if not all_files:
                self.ingestion_status = {"status": "completed", "progress": 100, "message": "No supported files found"}
                return
            
            self.ingestion_status["message"] = f"Found {len(all_files)} files to process"
            
            # Process files in batches
            processed_count = 0
            
            for i in range(0, len(all_files), BATCH_SIZE):
                batch = all_files[i:i + BATCH_SIZE]
                
                for file_path in batch:
                    await self._process_single_file(file_path, incremental)
                    processed_count += 1
                    
                    # Update progress
                    progress = int((processed_count / len(all_files)) * 100)
                    self.ingestion_status = {
                        "status": "processing",
                        "progress": progress,
                        "message": f"Processed {processed_count}/{len(all_files)} files"
                    }
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            self.ingestion_status = {
                "status": "completed",
                "progress": 100,
                "message": f"Successfully processed {processed_count} files"
            }
            
        except Exception as e:
            self.ingestion_status = {
                "status": "error",
                "progress": 0,
                "message": f"Error during ingestion: {str(e)}"
            }
    
    async def _process_single_file(self, file_path: Path, incremental: bool = True):
        """Process a single file and add it to the vector database"""
        try:
            # Generate file hash for incremental processing
            file_hash = self._get_file_hash(file_path)
            
            if incremental:
                # Check if file already processed (by hash)
                existing = self.collection.get(
                    where={"file_hash": file_hash}
                )
                if existing["ids"]:
                    return  # Skip if already processed
            
            # Process document
            chunks = await self.document_processor.process_file(file_path)
            
            if not chunks:
                return
            
            # Generate embeddings
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Prepare metadata
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_hash}_{i}"
                metadata = {
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "processed_at": datetime.now().isoformat(),
                    **chunk.get("metadata", {})
                }
                
                ids.append(chunk_id)
                metadatas.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file based on path and modification time"""
        stat = file_path.stat()
        hash_input = f"{file_path}_{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def get_ingestion_status(self) -> Dict[str, Any]:
        """Get current ingestion status"""
        return self.ingestion_status
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            count_result = self.collection.count()
            
            # Get some sample metadata to understand file types
            sample_result = self.collection.get(limit=100, include=["metadatas"])
            file_types = {}
            unique_files = set()
            
            for metadata in sample_result.get("metadatas", []):
                filename = metadata.get("filename", "")
                if filename:
                    unique_files.add(filename)
                    ext = Path(filename).suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            return {
                "total_chunks": count_result,
                "unique_files": len(unique_files),
                "file_types": file_types,
                "embedding_model": EMBEDDING_MODEL,
                "vector_db_path": VECTOR_DB_PATH
            }
            
        except Exception as e:
            return {"error": str(e)}