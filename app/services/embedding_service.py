import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.db import get_supabase_client
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings for similarity search"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.supabase = get_supabase_client()
        self.embedding_model = "text-embedding-ada-002"
        self.embedding_dimension = 1536
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text using OpenAI"""
        try:
            # Clean and prepare text
            cleaned_text = text.replace("\n", " ").strip()
            
            # Generate embedding
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=cleaned_text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text of length {len(cleaned_text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def search_similar_documents(
        self, 
        query: str, 
        threshold: float = 0.7, 
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for documents similar to the query"""
        try:
            # Generate embedding for the query
            logger.debug(f"search_similar_documents: Generating embedding for query: '{query[:50]}...'")
            query_embedding = await self.generate_embedding(query)
            logger.debug(f"search_similar_documents: Embedding generated, first 5 values: {query_embedding[:5]}")
            
            # Search similar documents using Supabase RPC function
            logger.debug(f"search_similar_documents: Calling RPC with threshold={threshold}, limit={limit}")
            response = self.supabase.rpc(
                'search_similar_content',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            logger.debug(f"search_similar_documents: RPC response - data type: {type(response.data)}, length: {len(response.data) if response.data else 0}")
            
            if response.data:
                logger.info(f"Found {len(response.data)} similar documents for query: {query[:50]}...")
                for i, doc in enumerate(response.data):
                    logger.info(f"  Doc {i+1}: '{doc.get('title')}' - similarity: {doc.get('similarity')}")
                return response.data
            else:
                logger.info(f"No similar documents found for query: {query[:50]}...")
                return []
                
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}", exc_info=True)
            
            # Fallback to full-text search if vector search fails
            logger.info(f"Falling back to full-text search for query: {query}")
            try:
                # Perform full-text search
                response = self.client.table("document_chunks").select("content").text_search(
                    "content", f"'{query}'"
                ).limit(5).execute()
                
                if response.data:
                    context = "\n\n---\n\n".join([item['content'] for item in response.data])
                    logger.info("Fallback full-text search successful")
                    return [{"content": c, "similarity": 0.5} for c in context.split("\n\n---\n\n")]
                else:
                    logger.info("No results from fallback full-text search")
                    return []
            
            except Exception as e:
                logger.error(f"Error in fallback full-text search: {e}")
                return []
    
    async def fallback_text_search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Fallback to PostgreSQL full-text search if vector search fails"""
        try:
            response = self.supabase.table("documents").select(
                "id, title, content, document_type"
            ).text_search(
                "search_content", 
                query, 
                config="indonesian"
            ).eq("is_active", True).limit(limit).execute()
            
            # Format response to match vector search format
            results = []
            for doc in response.data or []:
                results.append({
                    **doc,
                    'similarity': 0.5  # Default similarity score for text search
                })
            
            logger.info(f"Fallback text search found {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Error in fallback text search: {e}")
            return []

    async def has_relevant_docs(self, query: str, threshold: float = 0.6) -> bool:
        """Quick check to determine if there are any relevant documents for a query."""
        try:
            # First try vector similarity search with a low threshold
            logger.info(f"has_relevant_docs: Checking relevance for query: '{query[:50]}...' with threshold={threshold}")
            results = await self.search_similar_documents(query, threshold=threshold, limit=1)
            logger.info(f"has_relevant_docs: Vector search returned {len(results)} results")
            if len(results) > 0:
                logger.info(f"has_relevant_docs: Found relevant doc - '{results[0].get('title')}' with similarity={results[0].get('similarity')}")
                return True
            
            # Fallback: try text search if vector search finds nothing
            logger.warning(f"has_relevant_docs: Vector search found no results, trying text search for: {query[:50]}...")
            text_results = await self.fallback_text_search(query, limit=1)
            logger.info(f"has_relevant_docs: Text search returned {len(text_results)} results")
            if len(text_results) > 0:
                logger.info(f"has_relevant_docs: Found via text search - '{text_results[0].get('title')}'")
                return True
            
            logger.warning(f"has_relevant_docs: NO DOCUMENTS FOUND for query: '{query}'")
            return False
        except Exception as e:
            logger.error(f"has_relevant_docs: Error checking relevant docs: {e}", exc_info=True)
            # Be conservative: if we can't check, allow the query through
            # so it doesn't incorrectly refuse valid questions
            logger.info("has_relevant_docs: Error occurred, being permissive and returning True")
            return True
    
    async def add_document_with_embedding(
        self, 
        title: str, 
        content: str, 
        document_type: str = "sop",
        tags: List[str] = None
    ) -> bool:
        """Add a new document with its embedding"""
        try:
            # Generate embedding
            embedding = await self.generate_embedding(f"{title} {content}")
            
            # Insert document
            response = self.supabase.table("documents").insert({
                "title": title,
                "content": content,
                "document_type": document_type,
                "tags": tags or [],
                "content_embedding": embedding
            }).execute()
            
            if response.data:
                logger.info(f"Successfully added document: {title}")
                return True
            else:
                logger.error(f"Failed to add document: {title}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding document with embedding: {e}")
            return False
    
    async def update_all_embeddings(self) -> int:
        """Update embeddings for all documents that don't have them"""
        try:
            # Get documents without embeddings
            response = self.supabase.table("documents").select(
                "id, title, content"
            ).is_("content_embedding", "null").eq("is_active", True).execute()
            
            if not response.data:
                logger.info("No documents need embedding updates")
                return 0
            
            updated_count = 0
            for doc in response.data:
                try:
                    # Generate embedding
                    embedding = await self.generate_embedding(f"{doc['title']} {doc['content']}")
                    
                    # Update document
                    update_response = self.supabase.table("documents").update({
                        "content_embedding": embedding
                    }).eq("id", doc["id"]).execute()
                    
                    if update_response.data:
                        updated_count += 1
                        logger.info(f"Updated embedding for document: {doc['title']}")
                    
                except Exception as e:
                    logger.error(f"Failed to update embedding for document {doc['id']}: {e}")
                    continue
            
            logger.info(f"Updated embeddings for {updated_count} documents")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            return 0
    
    async def get_context_from_similar_docs(self, query: str, max_context_length: int = 3000) -> str:
        """Get formatted context from similar documents for AI"""
        try:
            # Search for similar documents with a lower threshold
            similar_docs = await self.search_similar_documents(query, threshold=0.3, limit=5)
            
            # If vector search finds nothing, try text search
            if not similar_docs:
                logger.info(f"Vector search found no results, trying text search for context: {query[:50]}...")
                similar_docs = await self.fallback_text_search(query, limit=3)
            
            if not similar_docs:
                return "Tidak ada dokumen yang relevan ditemukan."
            
            # Format context
            context = "Berdasarkan dokumen yang relevan:\n\n"
            current_length = len(context)
            
            for i, doc in enumerate(similar_docs, 1):
                doc_context = f"Dokumen {i}: {doc['title']}\n"
                doc_context += f"Relevansi: {doc.get('similarity', 0.5):.2f}\n"
                doc_context += f"Konten: {doc['content'][:1000]}...\n\n"
                
                # Check if adding this document exceeds max length
                if current_length + len(doc_context) > max_context_length:
                    break
                
                context += doc_context
                current_length += len(doc_context)
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context from similar docs: {e}")
            return "Terjadi kesalahan saat mencari dokumen yang relevan."

# Create service instance
embedding_service = EmbeddingService()