from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    """Individual message model"""
    role: str = Field(..., description="Role of the message sender (user/assistant/system)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Timestamp of the message")

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_history: Optional[List[Message]] = Field(default_factory=list, description="Previous conversation messages")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Response creativity (0-2)")
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000, description="Maximum response length")
    return_full_document: Optional[bool] = Field(default=False, description="If true, return the most relevant document content directly without model generation")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Chatbot response")
    conversation_id: Optional[str] = Field(default=None, description="Conversation identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    model_used: str = Field(..., description="AI model used for the response")
    tokens_used: Optional[int] = Field(default=None, description="Number of tokens consumed")

    # Avoid conflicts with Pydantic's protected namespaces if fields resemble them
    model_config = {
        "protected_namespaces": ()
    }

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="API status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")