from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from app.repositories.document_repository import document_repository
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# --- Pydantic Models ---

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: str = Field(..., min_length=1, description="Document content")
    document_type: str = Field(default="guide", description="Type of document (e.g., sop, guide, manual)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None

class BulkDocumentCreate(BaseModel):
    documents: List[DocumentCreate]

# --- Background Tasks ---

async def generate_and_update_embedding(doc_id: int, text: str):
    """Generate embedding and update the document in the background."""
    try:
        embedding = await embedding_service.generate_embedding(text)
        await document_repository.update_document(doc_id, embedding=embedding)
        logger.info(f"Successfully generated and updated embedding for document {doc_id}")
    except Exception as e:
        logger.error(f"Background task failed for document {doc_id}: {e}")

# --- API Endpoints ---

@router.post("/", status_code=status.HTTP_202_ACCEPTED, summary="Create a new document")
async def create_document(document: DocumentCreate, background_tasks: BackgroundTasks):
    """
    Create a new document. Embedding generation will run in the background.
    """
    try:
        doc_id = await document_repository.create_document(
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            tags=document.tags
        )
        if not doc_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create document")
        
        background_tasks.add_task(generate_and_update_embedding, doc_id, f"{document.title} {document.content}")
        
        return {"message": "Document creation accepted. Embedding will be generated in the background.", "document_id": doc_id}
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the document")

@router.post("/bulk", status_code=status.HTTP_202_ACCEPTED, summary="Create multiple documents")
async def create_documents_bulk(bulk: BulkDocumentCreate, background_tasks: BackgroundTasks):
    """
    Create multiple documents in one request. Embeddings will be generated in the background.
    """
    created_ids = []
    for doc in bulk.documents:
        try:
            doc_id = await document_repository.create_document(
                title=doc.title,
                content=doc.content,
                document_type=doc.document_type,
                tags=doc.tags
            )
            if doc_id:
                created_ids.append(doc_id)
                background_tasks.add_task(generate_and_update_embedding, doc_id, f"{doc.title} {doc.content}")
        except Exception as e:
            logger.error(f"Error creating document '{doc.title}' in bulk: {e}")
            # Continue with other documents
    
    return {"message": f"Accepted {len(created_ids)} documents for creation. Embeddings will be generated in the background.", "document_ids": created_ids}

@router.put("/{document_id}", status_code=status.HTTP_202_ACCEPTED, summary="Update a document")
async def update_document(document_id: int, document: DocumentUpdate, background_tasks: BackgroundTasks):
    """
    Update an existing document. If content is updated, the embedding will be regenerated in the background.
    """
    existing_doc = await document_repository.get_document(document_id)
    if not existing_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    
    success = await document_repository.update_document(
        document_id=document_id,
        title=document.title,
        content=document.content,
        document_type=document.document_type,
        tags=document.tags
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update document")
    
    if document.content:
        background_tasks.add_task(generate_and_update_embedding, document_id, f"{document.title or existing_doc['title']} {document.content}")
    
    return {"message": "Document update accepted. Embedding will be regenerated if content was changed.", "document_id": document_id}

@router.delete("/{document_id}", status_code=status.HTTP_200_OK, summary="Delete a document")
async def delete_document(document_id: int, hard_delete: bool = False):
    """
    Delete a document. By default, this is a soft delete (marks as inactive).
    """
    success = await document_repository.delete_document(document_id, soft_delete=not hard_delete)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    
    return {"message": f"Document {document_id} {'permanently deleted' if hard_delete else 'deactivated'}"}

@router.get("/{document_id}", summary="Get a document by ID")
async def get_document(document_id: int):
    """
    Retrieve a specific document by its ID.
    """
    document = await document_repository.get_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found")
    
    return {
        "id": document["id"],
        "title": document["title"],
        "content": document["content"],
        "document_type": document["document_type"],
        "tags": document["tags"],
        "has_embedding": document["content_embedding"] is not None,
        "created_at": document["created_at"]
    }

@router.get("/", summary="List all documents")
async def list_documents(document_type: Optional[str] = None, tag: Optional[str] = None, limit: int = 100, offset: int = 0):
    """
    List documents with optional filtering by type or tag.
    """
    tags = [tag] if tag else None
    documents = await document_repository.list_documents(
        document_type=document_type,
        tags=tags,
        limit=limit,
        offset=offset
    )
    return [
        {
            "id": doc["id"],
            "title": doc["title"],
            "document_type": doc["document_type"],
            "tags": doc["tags"],
            "has_embedding": doc["content_embedding"] is not None,
            "created_at": doc["created_at"]
        }
        for doc in documents
    ]

@router.post("/embeddings/regenerate", status_code=status.HTTP_202_ACCEPTED, summary="Regenerate embeddings")
async def trigger_regenerate_embeddings(background_tasks: BackgroundTasks):
    """
    Trigger a background task to regenerate embeddings for all documents that are missing them.
    """
    # This is a simplified approach. A more robust solution would use a proper job queue.
    documents = await document_repository.get_documents_without_embeddings()
    count = 0
    for doc in documents:
        background_tasks.add_task(generate_and_update_embedding, doc['id'], f"{doc['title']} {doc['content']}")
        count += 1
    
    return {"message": f"Accepted {count} documents for embedding regeneration in the background."}