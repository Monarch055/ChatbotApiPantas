from typing import List, Optional, Dict, Any
from app.db import get_supabase_client
import logging

logger = logging.getLogger(__name__)

class FAQRepository:
    """Repository for FAQ data access"""
    
    def __init__(self):
        self.client = get_supabase_client()
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all FAQ categories ordered by display_order"""
        try:
            response = self.client.table("faq_categories").select("*").order("display_order").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return []
    
    async def get_subcategories(self, category_id: int) -> List[Dict[str, Any]]:
        """Get subcategories for a specific category"""
        try:
            response = self.client.table("faq_subcategories").select("*").eq("category_id", category_id).order("display_order").execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching subcategories for category {category_id}: {e}")
            return []
    
    async def get_answer(self, category_id: int, subcategory_id: int) -> Optional[str]:
        """Get answer for specific category and subcategory"""
        try:
            response = self.client.table("faq_items").select("answer").eq("category_id", category_id).eq("subcategory_id", subcategory_id).limit(1).execute()
            if response.data:
                return response.data[0]["answer"]
            return None
        except Exception as e:
            logger.error(f"Error fetching answer for category {category_id}, subcategory {subcategory_id}: {e}")
            return None
    
    async def get_all_faq_content(self) -> str:
        """Get all FAQ content as formatted text for AI context"""
        try:
            # Get all categories with their subcategories and answers
            categories_response = self.client.table("faq_categories").select("""
                *,
                faq_subcategories(
                    *,
                    faq_items(answer)
                )
            """).order("display_order").execute()
            
            if not categories_response.data:
                return "No FAQ content available."
            
            formatted_content = "FAQ Knowledge Base:\n\n"
            
            for category in categories_response.data:
                formatted_content += f"Category: {category['name']}\n"
                formatted_content += "=" * 50 + "\n"
                
                subcategories = category.get('faq_subcategories', [])
                for subcategory in subcategories:
                    formatted_content += f"\nSubcategory: {subcategory['name']}\n"
                    formatted_content += "-" * 30 + "\n"
                    
                    faq_items = subcategory.get('faq_items', [])
                    for item in faq_items:
                        formatted_content += f"Answer: {item['answer']}\n\n"
                
                formatted_content += "\n"
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"Error fetching all FAQ content: {e}")
            return "Error loading FAQ content."
    
    async def search_faq_content(self, query: str) -> List[Dict[str, Any]]:
        """Search FAQ content for relevant answers"""
        try:
            # Simple text search across answers
            # Note: For better search, consider using PostgreSQL full-text search or embeddings
            response = self.client.table("faq_items").select("""
                *,
                faq_categories(name),
                faq_subcategories(name)
            """).ilike("answer", f"%{query}%").limit(5).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error searching FAQ content: {e}")
            return []
    
    async def get_all_faqs(self) -> List[Dict[str, Any]]:
        """
        Get all FAQs as a simple list with category and subcategory names.
        Returns list of dicts with 'question' field formatted as "Category - Subcategory"
        """
        try:
            # Get all categories with their subcategories
            response = self.client.table("faq_categories").select("""
                name,
                faq_subcategories(name)
            """).order("display_order").execute()
            
            if not response.data:
                return []
            
            faq_list = []
            for category in response.data:
                category_name = category['name']
                subcategories = category.get('faq_subcategories', [])
                
                for subcategory in subcategories:
                    subcategory_name = subcategory['name']
                    # Format as "Category - Subcategory"
                    faq_list.append({
                        'question': f"{category_name} - {subcategory_name}"
                    })
            
            return faq_list
            
        except Exception as e:
            logger.error(f"Error fetching all FAQs: {e}")
            return []

# Create repository instance
faq_repository = FAQRepository()