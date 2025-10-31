from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.models import ChatRequest, ChatResponse, ErrorResponse
from app.services import chat_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the chatbot",
    description="Send a message to the chatbot and receive a response based on OpenAI GPT model"
)
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the AI assistant
    
    - **message**: The user's message to send to the chatbot
    - **conversation_history**: Optional list of previous messages in the conversation
    - **system_prompt**: Optional custom system prompt to modify chatbot behavior
    - **temperature**: Optional creativity parameter (0.0 to 2.0)
    - **max_tokens**: Optional maximum length of the response
    """
    try:
        chat_service.validate_request(request)
        
        response = await chat_service.generate_response(request)
        
        logger.info(f"Successfully generated chat response")
        return response
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.get(
    "/models",
    summary="Get available AI models",
    description="Get list of available AI models for the chatbot"
)
async def get_models():
    """Get available AI models"""
    return {
        "available_models": [
            {
                "name": "gpt-3.5-turbo",
                "description": "Fast and efficient model for most tasks"
            },
            {
                "name": "gpt-4",
                "description": "More capable model for complex tasks"
            }
        ],
        "current_model": chat_service.client.model if hasattr(chat_service.client, 'model') else "gpt-3.5-turbo"
    }