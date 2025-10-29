from .chat import router as chat_router
from .health import router as health_router
from .documents import router as documents_router

__all__ = ["chat_router", "health_router", "documents_router"]