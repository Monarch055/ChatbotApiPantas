from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_client: Client = None

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    global _client
    if _client is None:
        try:
            _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    return _client