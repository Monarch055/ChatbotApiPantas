import openai
import re
import uuid
import logging
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.models.schemas import Message, ChatRequest, ChatResponse
from app.services.faq_service import faq_service
from app.services.embedding_service import embedding_service
from app.repositories import chat_session_repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """Service class for handling AI-powered chat interactions with FAQ knowledge base"""
    
    def __init__(self):
        """Initialize the ChatService with OpenAI client and repositories"""
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.faq_service = faq_service
        self.embedding_service = embedding_service
        self.chat_repository = chat_session_repository
        # Plain text formatting rules with emphasis on completeness
        self.plain_text_rules = (
            "Aturan format PENTING: "
            "1) Jawab HANYA dalam teks biasa (plain text) - tanpa Markdown, tanpa **bold**, _italic_, kode, tautan, atau emoji. "
            "2) Untuk daftar langkah, gunakan format: 1. [langkah pertama]\\n2. [langkah kedua]\\n3. [langkah ketiga] dst. "
            "3) WAJIB menyebutkan SEMUA langkah dari dokumen - jangan potong atau ringkas meskipun panjang. "
            "4) Gunakan kata-kata PERSIS dari dokumen tanpa parafrase."
        )
        # Keywords to detect intent to view full document
        # More aggressive detection to ensure users get complete SOPs
        self.full_doc_keywords = [
            "lengkap", "seluruh", "tampilkan lengkap", "semua langkah", "full doc", "dokumen lengkap",
            "cara", "bagaimana", "langkah", "prosedur", "proses", "sop", "tutorial",
            "gimana", "step", "tahap", "panduan", "petunjuk"
        ]
    
    async def _prepare_messages_with_smart_context(
        self, 
        user_message: str, 
        conversation_history: List[Message], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Prepare messages with smart context using similarity search"""
        messages = []
        
        # Ignore placeholder or empty system prompts
        if system_prompt and system_prompt.strip().lower() in ['string', '', 'none']:
            system_prompt = None
        
        # Always search for similar documents to get RAG context
        relevant_context = await self.embedding_service.get_context_from_similar_docs(
            user_message, max_context_length=2000
        )
        
        # Create enhanced system prompt with relevant context and plain-text formatting rules
        if system_prompt:
            # If user provided a custom system prompt, append RAG context to it
            final_system_prompt = f"""{system_prompt}

{self.plain_text_rules}

{relevant_context}

Instruksi tambahan:
1. Jawab HANYA pertanyaan yang terkait dengan proses/layanan pemerintahan Provinsi Kalimantan Barat
2. Gunakan langkah-langkah yang tercantum dalam dokumen jika tersedia
3. Jika informasi tidak ditemukan di dokumen atau tidak relevan, TOLAK dengan sopan dan arahkan ke WhatsApp support: {settings.WHATSAPP_NUMBER}
4. Jika user membutuhkan bantuan lebih lanjut, sarankan untuk menghubungi support WhatsApp: {settings.WHATSAPP_NUMBER}

Jam Support:
- Senin-Jumat: 09:00-18:00 WIB
- Sabtu: 09:00-14:00 WIB
- Darurat: 24/7
"""
        else:
            # Use default system prompt with RAG context
            final_system_prompt = f"""Anda adalah asisten AI customer support yang membantu dalam bahasa Indonesia. 
Anda memiliki akses ke knowledge base perusahaan dan dapat memberikan panduan teknis.

{self.plain_text_rules}

{relevant_context}

Instruksi PENTING:
1. Jawab HANYA pertanyaan yang terkait dengan proses/layanan pemerintahan Provinsi Kalimantan Barat
2. PRIORITASKAN dan gunakan informasi dari dokumen di atas untuk menjawab pertanyaan user
3. SALIN SEMUA LANGKAH dari dokumen - JANGAN ringkas, JANGAN potong, JANGAN ubah kata-katanya
4. Jika dokumen memiliki 14 langkah, Anda HARUS menyebutkan SEMUA 14 langkah dengan lengkap
5. Gunakan kata-kata PERSIS SAMA dengan yang ada di dokumen
6. Format setiap langkah dengan nomor pada baris terpisah (1. ... \\n2. ... \\n3. ...)
7. Jika informasi tidak ditemukan di dokumen atau tidak relevan, TOLAK dengan sopan dan arahkan ke WhatsApp support: {settings.WHATSAPP_NUMBER}
8. Jawab dalam bahasa Indonesia dengan ramah dan profesional

CATATAN: Untuk SOP atau prosedur panjang, user lebih suka melihat SEMUA detail lengkap daripada ringkasan.

Jam Support:
- Senin-Jumat: 09:00-18:00 WIB
- Sabtu: 09:00-14:00 WIB
- Darurat: 24/7
"""
        
        messages.append({"role": "system", "content": final_system_prompt})
        
        # Add conversation history (limit to last 8 messages to save tokens)
        for msg in conversation_history[-8:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def generate_response(self, chat_request: ChatRequest) -> ChatResponse:
        """Generate AI-powered response using FAQ knowledge base context"""
        try:
            conversation_history = chat_request.conversation_history or []
            
            # Create or get session ID
            session_id = str(uuid.uuid4())  # In a real app, you'd get this from the request or create one

            # Special greeting for initial load messages (do not trigger domain guard)
            initial_triggers = {"start", "/start", "hello", "hi", "halo", "mulai"}
            if (chat_request.message or "").strip().lower() in initial_triggers:
                greeting = (
                    "Halo! Saya asisten dukungan digital Pemprov Kalimantan Barat. Saya dapat membantu pertanyaan "
                    "yang berkaitan dengan proses/layanan pemerintahan dan SOP di lingkungan Pemprov Kalbar.\n\n"
                    "Cara menggunakan:\n"
                    "- Tanyakan topik yang Anda butuhkan (misal: 'SOP Pembuatan Website Baru di AWDI')\n"
                    "- Untuk melihat dokumen lengkap, tambahkan kata 'lengkap' atau gunakan opsi 'return_full_document'\n"
                    f"- Bantuan lebih lanjut: WhatsApp {settings.WHATSAPP_NUMBER}"
                )
                greeting = self._sanitize_plain_text(greeting)
                try:
                    await self.chat_repository.add_message(session_id, "assistant", greeting)
                except Exception as e:
                    logger.warning(f"Failed to store greeting: {e}")
                return ChatResponse(
                    response=greeting,
                    conversation_id=session_id,
                    model_used="system-greeting",
                    tokens_used=0
                )

            # Domain guard: Temporarily disabled due to OpenAI embedding non-determinism
            # The issue: OpenAI embeddings have slight variations each time, causing
            # the same query to sometimes find documents and sometimes not.
            # This was causing valid government queries to be incorrectly refused.
            # 
            # The domain guard will be handled by the RAG context + system prompt instead:
            # - If no relevant docs are found, the AI will naturally say it doesn't know
            # - The system prompt enforces government-only scope
            # - This avoids the false-negative problem while maintaining scope control
            #
            # Original code (disabled):
            # in_scope = await self.embedding_service.has_relevant_docs(chat_request.message, threshold=0.3)
            # if not in_scope:
            #     return refusal_response
            
            logger.info(f"Processing query (domain guard disabled): {chat_request.message[:50]}...")

            # Full document mode: if requested or inferred by keywords, return the top similar document directly
            # This saves tokens and returns the exact document content without AI modification
            if chat_request.return_full_document or self._is_full_doc_intent(chat_request.message):
                logger.info("Full document mode triggered - returning document directly without OpenAI")
                
                # Try up to 3 times with different embeddings to handle OpenAI embedding variance
                similar_docs = []
                for attempt in range(3):
                    similar_docs = await self.embedding_service.search_similar_documents(
                        chat_request.message, 
                        threshold=0.3,
                        limit=1
                    )
                    if similar_docs:
                        logger.info(f"Found document on attempt {attempt + 1}")
                        break
                    logger.warning(f"Attempt {attempt + 1}/3: No documents found, retrying with new embedding...")
                
                if similar_docs:
                    doc = similar_docs[0]
                    # Return the EXACT document content with proper formatting
                    title = doc.get('title', 'Dokumen')
                    content = doc.get('content', '')
                    
                    # Format the document with clear structure
                    full_text = f"{title}:\n\n{content}"
                    
                    # Only apply basic sanitization to fix formatting (preserve all content)
                    full_text = self._sanitize_plain_text(full_text)
                    
                    logger.info(f"Returning full document: {title} ({len(content)} chars, 0 tokens)")
                    
                    try:
                        await self.chat_repository.add_message(session_id, "user", chat_request.message)
                        await self.chat_repository.add_message(session_id, "assistant", full_text)
                    except Exception as e:
                        logger.warning(f"Failed to store full-doc conversation: {e}")
                    
                    return ChatResponse(
                        response=full_text,
                        conversation_id=session_id,
                        model_used="kb-direct",
                        tokens_used=0  # Zero tokens - direct KB retrieval!
                    )

            # Generate AI response with FAQ context
            response = await self._generate_ai_response_with_context(chat_request, session_id)
            
            # Store the conversation in the database (async, don't block response)
            try:
                await self.chat_repository.add_message(session_id, "user", chat_request.message)
                await self.chat_repository.add_message(session_id, "assistant", response.response)
            except Exception as e:
                logger.warning(f"Failed to store conversation: {e}")
                # Don't fail the response if database storage fails
            
            return response
            
        except Exception as e:
            logger.error(f"Unexpected error in chat service: {e}")
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    async def _generate_ai_response_with_context(self, chat_request: ChatRequest, session_id: str) -> ChatResponse:
        """Generate AI response with smart similarity-based context"""
        try:
            # Prepare messages with smart context using similarity search
            messages = await self._prepare_messages_with_smart_context(
                user_message=chat_request.message,
                conversation_history=chat_request.conversation_history,
                system_prompt=chat_request.system_prompt
            )
            
            # Set parameters with defaults from config or request
            temperature = chat_request.temperature or settings.TEMPERATURE
            max_tokens = chat_request.max_tokens or settings.MAX_TOKENS
            
            logger.info(f"Sending request to OpenAI with {len(messages)} messages and smart context")
            
            # Make API call to OpenAI
            response = self.client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response content and sanitize Markdown/rich formatting
            assistant_message = response.choices[0].message.content
            assistant_message = self._sanitize_plain_text(assistant_message)
            tokens_used = response.usage.total_tokens if response.usage else None
            
            logger.info(f"Generated AI response with {tokens_used} tokens")
            
            return ChatResponse(
                response=assistant_message,
                conversation_id=session_id,
                model_used=settings.MODEL_NAME,
                tokens_used=tokens_used
            )
            
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            raise Exception("Rate limit exceeded. Please try again later.")
        
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            raise Exception("Authentication failed. Please check API key.")
        
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI API call: {e}")
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def validate_request(self, chat_request: ChatRequest) -> bool:
        """Validate chat request parameters"""
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise ValueError("Message cannot be empty")
        
        if len(chat_request.message) > 2000:
            raise ValueError("Message is too long (max 2000 characters)")
        
        return True

    def _sanitize_plain_text(self, text: str) -> str:
        """Remove common Markdown/rich-text markers and format numbered lists properly."""
        if not text:
            return text
        
        # Remove Markdown formatting
        text = text.replace("```", "").replace("`", "")
        text = text.replace("**", "").replace("__", "")
        text = text.replace("_", "")
        
        # Clean up excessive whitespace but preserve intentional line breaks
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces within lines
            line = re.sub(r"[ \t]+", " ", line)
            # Trim whitespace from start/end of line
            line = line.strip()
            # Skip completely empty lines but keep them as separators
            if line or (cleaned_lines and cleaned_lines[-1] != ""):
                cleaned_lines.append(line)
        
        # Join lines back together
        text = '\n'.join(cleaned_lines)
        
        # Format numbered lists properly: ensure each numbered item is on its own line
        # Match patterns like "1. " or "1) " followed by content
        text = re.sub(r'(\d+)\.\s+', r'\n\1. ', text)  # Ensure line break before each number
        text = re.sub(r'(\d+)\)\s+', r'\n\1. ', text)  # Convert "1)" to "1."
        
        # Clean up multiple consecutive newlines (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading newline if text starts with a number
        text = text.lstrip('\n')
        
        return text.strip()

    def _is_full_doc_intent(self, message: str) -> bool:
        """Heuristic to detect if user is asking for the full document."""
        m = (message or '').lower()
        return any(k in m for k in self.full_doc_keywords)
    
chat_service = ChatService()