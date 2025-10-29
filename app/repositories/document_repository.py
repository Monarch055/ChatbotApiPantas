from typing import List, Dict, Any, Optional
from app.db import get_supabase_client
import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    def __init__(self):
        self.client = get_supabase_client()
    
    async def create_document(
        self, 
        title: str, 
        content: str,
        document_type: str = "guide",
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> Optional[int]:
        """Create a new document with optional embedding"""
        try:
            document_data = {
                "title": title,
                "content": content,
                "document_type": document_type,
                "tags": tags or [],
                "content_embedding": embedding,
                "is_active": True
            }
            
            response = self.client.table("documents").insert(document_data).execute()
            
            if response.data:
                doc_id = response.data[0]["id"]
                logger.info(f"Document created successfully with ID: {doc_id}")
                return doc_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None
    
    async def update_document(
        self,
        document_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        document_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """Update an existing document"""
        try:
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if content is not None:
                update_data["content"] = content
            if document_type is not None:
                update_data["document_type"] = document_type
            if tags is not None:
                update_data["tags"] = tags
            if embedding is not None:
                update_data["content_embedding"] = embedding
            
            if not update_data:
                return False
            
            response = self.client.table("documents").update(update_data).eq("id", document_id).execute()
            
            if response.data:
                logger.info(f"Document {document_id} updated successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False
    
    async def delete_document(self, document_id: int, soft_delete: bool = True) -> bool:
        """Delete a document (soft or hard delete)"""
        try:
            if soft_delete:
                # Soft delete - mark as inactive
                response = self.client.table("documents").update({
                    "is_active": False
                }).eq("id", document_id).execute()
            else:
                # Hard delete - actually remove from database
                response = self.client.table("documents").delete().eq("id", document_id).execute()
            
            if response.data:
                logger.info(f"Document {document_id} {'soft' if soft_delete else 'hard'} deleted successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get a single document by ID"""
        try:
            response = self.client.table("documents").select("*").eq("id", document_id).eq("is_active", True).limit(1).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {e}")
            return None
    
    async def list_documents(
        self, 
        document_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all documents with optional filtering"""
        try:
            query = self.client.table("documents").select("id, title, document_type, tags, created_at, content_embedding").eq("is_active", True)
            
            if document_type:
                query = query.eq("document_type", document_type)
            
            if tags:
                query = query.contains("tags", tags)
            
            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    async def get_documents_without_embeddings(self) -> List[Dict[str, Any]]:
        """Get all documents that don't have embeddings yet"""
        try:
            response = self.client.table("documents").select("id, title, content").eq("is_active", True).is_("content_embedding", "null").execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching documents without embeddings: {e}")
            return []

document_repository = DocumentRepository()
