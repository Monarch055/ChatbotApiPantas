from typing import Dict, Any, Optional, Tuple, List
from app.repositories import faq_repository
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class FAQService:
    """Service for handling FAQ-based conversations using Supabase"""
    
    def __init__(self):
        self.faq_repository = faq_repository
    
    async def get_all_faq_context(self) -> str:
        """Get all FAQ content for AI context"""
        try:
            faq_content = await self.faq_repository.get_all_faq_content()
            
            # Add additional context about the support system
            context = f"""
You are a helpful customer support AI assistant. Here is the complete FAQ knowledge base:

{faq_content}

Additional Support Information:
- WhatsApp Support: {settings.WHATSAPP_NUMBER}
- Support Hours: Monday-Friday 9:00 AM - 6:00 PM (GMT+7), Saturday 9:00 AM - 2:00 PM (GMT+7)
- Emergency support: 24/7

 Instructions:
 1. Use the FAQ knowledge base to answer user questions accurately
 2. If you cannot find a relevant answer in the FAQ or the request is not related to government processes/services, POLITELY DECLINE and direct the user to official support
 3. If the user seems unsatisfied or needs complex help, suggest contacting WhatsApp support
 4. Always be friendly, professional, and concise
 5. When suggesting WhatsApp contact, provide the number and support hours

 Formatting rules:
 - Respond in plain text only
 - Do not use Markdown or rich formatting (no **bold**, _italic_, code blocks, links, or emojis)
 - If listing steps, use simple numbered lists like: 1. ..., 2. ..., 3. ...
"""
            return context
            
        except Exception as e:
            logger.error(f"Error getting FAQ context: {e}")
            return "I'm having trouble accessing the knowledge base. Please contact support."
    
    async def search_relevant_faq(self, query: str) -> List[Dict[str, Any]]:
        """Search for relevant FAQ content based on user query"""
        try:
            return await self.faq_repository.search_faq_content(query)
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return []
    
    async def get_faq_list(self) -> str:
        """
        Get a plain-text numbered list of all FAQs for direct display to users.
        Returns formatted string ready for chatbot response.
        """
        try:
            # Get all FAQs from repository
            faqs = await self.faq_repository.get_all_faqs()
            
            if not faqs or len(faqs) == 0:
                return ""
            
            # Format as numbered list
            faq_lines = []
            for idx, faq in enumerate(faqs, start=1):
                # Extract question or title
                question = faq.get('question', faq.get('title', 'N/A'))
                faq_lines.append(f"{idx}. {question}")
            
            return "\n".join(faq_lines)
            
        except Exception as e:
            logger.error(f"Error getting FAQ list: {e}")
            return ""

# Create service instance
faq_service = FAQService()