import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import CHAT_HISTORY_PATH, ENABLE_CHAT_STORAGE, MAX_CHAT_HISTORY

class ChatService:
    def __init__(self):
        self.chat_history_path = Path(CHAT_HISTORY_PATH)
        self.chat_history_path.mkdir(exist_ok=True)
        self.conversations_file = self.chat_history_path / "conversations.json"
        self.ensure_conversations_file()
    
    def ensure_conversations_file(self):
        """Ensure conversations file exists"""
        if not self.conversations_file.exists():
            self.conversations_file.write_text(json.dumps({}))
    
    async def store_message(
        self,
        conversation_id: Optional[str],
        user_message: str,
        bot_response: str,
        sources: List[Dict[str, Any]]
    ) -> str:
        """Store a chat message and return conversation ID"""
        if not ENABLE_CHAT_STORAGE:
            return conversation_id or str(uuid.uuid4())
        
        try:
            # Generate conversation ID if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
            
            # Load existing conversations
            conversations = self._load_conversations()
            
            # Create message entry
            message_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "bot_response": bot_response,
                "sources": sources
            }
            
            # Add to conversation
            if conversation_id not in conversations:
                conversations[conversation_id] = {
                    "id": conversation_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "title": self._generate_title(user_message),
                    "messages": []
                }
            
            conversations[conversation_id]["messages"].append(message_entry)
            conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
            
            # Clean up old conversations if needed
            conversations = self._cleanup_old_conversations(conversations)
            
            # Save conversations
            self._save_conversations(conversations)
            
            return conversation_id
            
        except Exception as e:
            print(f"Error storing chat message: {e}")
            return conversation_id or str(uuid.uuid4())
    
    async def get_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of recent conversations"""
        try:
            conversations = self._load_conversations()
            
            # Convert to list and sort by updated_at
            conv_list = list(conversations.values())
            conv_list.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
            
            # Return limited list with summary info
            result = []
            for conv in conv_list[:limit]:
                result.append({
                    "id": conv["id"],
                    "title": conv.get("title", "Untitled"),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                    "message_count": len(conv.get("messages", []))
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation by ID"""
        try:
            conversations = self._load_conversations()
            return conversations.get(conversation_id)
        except Exception as e:
            print(f"Error getting conversation: {e}")
            return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a specific conversation"""
        try:
            conversations = self._load_conversations()
            if conversation_id in conversations:
                del conversations[conversation_id]
                self._save_conversations(conversations)
                return True
            return False
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    async def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        try:
            conversations = self._load_conversations()
            matching_conversations = []
            
            for conv_id, conv in conversations.items():
                # Search in title
                if query.lower() in conv.get("title", "").lower():
                    matching_conversations.append(conv)
                    continue
                
                # Search in messages
                for message in conv.get("messages", []):
                    if (query.lower() in message.get("user_message", "").lower() or
                        query.lower() in message.get("bot_response", "").lower()):
                        matching_conversations.append(conv)
                        break
            
            # Sort by updated_at
            matching_conversations.sort(
                key=lambda x: x.get("updated_at", ""), 
                reverse=True
            )
            
            return matching_conversations
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    def _load_conversations(self) -> Dict[str, Any]:
        """Load conversations from file"""
        try:
            if self.conversations_file.exists():
                content = self.conversations_file.read_text()
                return json.loads(content)
            return {}
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return {}
    
    def _save_conversations(self, conversations: Dict[str, Any]):
        """Save conversations to file"""
        try:
            self.conversations_file.write_text(
                json.dumps(conversations, indent=2, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Error saving conversations: {e}")
    
    def _generate_title(self, user_message: str) -> str:
        """Generate a title from the first user message"""
        # Take first 50 characters and clean up
        title = user_message[:50].strip()
        if len(user_message) > 50:
            title += "..."
        return title
    
    def _cleanup_old_conversations(self, conversations: Dict[str, Any]) -> Dict[str, Any]:
        """Remove old conversations if we exceed MAX_CHAT_HISTORY"""
        if len(conversations) <= MAX_CHAT_HISTORY:
            return conversations
        
        # Sort by updated_at and keep only the most recent ones
        conv_list = [(conv_id, conv) for conv_id, conv in conversations.items()]
        conv_list.sort(key=lambda x: x[1].get("updated_at", ""), reverse=True)
        
        # Keep only MAX_CHAT_HISTORY most recent
        cleaned_conversations = {}
        for conv_id, conv in conv_list[:MAX_CHAT_HISTORY]:
            cleaned_conversations[conv_id] = conv
        
        return cleaned_conversations