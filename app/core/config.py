import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:8080"
    ).split(",")
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    
    # Support Configuration
    WHATSAPP_NUMBER: str = os.getenv("WHATSAPP_NUMBER", "+62-812-3456-7890")
    
    # API Metadata
    API_TITLE: str = "Chatbot API"
    API_DESCRIPTION: str = "A RESTful API for chatbot functionality using OpenAI GPT"
    API_VERSION: str = "1.0.0"
    
    def validate_settings(self) -> bool:
        """Validate that required settings are present"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not self.SUPABASE_ANON_KEY:
            raise ValueError("SUPABASE_ANON_KEY is required")
        return True

# Create settings instance
settings = Settings()
settings.validate_settings()