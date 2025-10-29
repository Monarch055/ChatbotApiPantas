from typing import List, Optional, Dict, Any
from app.db import get_supabase_client
import logging
import uuid

logger = logging.getLogger(__name__)

class ChatSessionRepository:
    """Repository for chat sessions and messages"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new chat session"""
        try:
            session_id = str(uuid.uuid4())
            response = self.client.table("chat_sessions").insert({
                "id": session_id,
                "user_id": user_id,
                "stage": "active"
            }).execute()
            
            if response.data:
                return session_id
            else:
                logger.error("Failed to create session")
                return session_id  # Return generated ID even if insert failed
                
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return str(uuid.uuid4())  # Return a new ID as fallback
    
    async def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to a chat session"""
        try:
            response = self.client.table("chat_messages").insert({
                "session_id": session_id,
                "role": role,
                "content": content
            }).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error adding message to session {session_id}: {e}")
            return False
    
    async def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        try:
            response = self.client.table("chat_messages").select("*").eq("session_id", session_id).order("created_at").execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching messages for session {session_id}: {e}")
            return []
    
    async def update_session_helpful(self, session_id: str, helpful: bool) -> bool:
        """Update whether the session was helpful"""
        try:
            response = self.client.table("chat_sessions").update({
                "helpful": helpful
            }).eq("id", session_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error updating session helpful status: {e}")
            return False
    
    async def mark_session_escalated(self, session_id: str) -> bool:
        """Mark session as escalated to human support"""
        try:
            response = self.client.table("chat_sessions").update({
                "escalated": True,
                "escalated_at": "now()"
            }).eq("id", session_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error marking session as escalated: {e}")
            return False

# Create repository instance
chat_session_repository = ChatSessionRepository()