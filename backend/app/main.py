from fastapi import FastAPI

from backend.app.core.config import settings
from backend.app.api.documents import router as documents_router
from backend.app.api.chat import router as chat_router


# Initialise the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="An AI-powered academic research assistant.",
    version="0.1.0"
)


# Register API routers
app.include_router(
    documents_router,
    prefix=settings.API_V1_PREFIX
)

app.include_router(
    chat_router,
    prefix=settings.API_V1_PREFIX
)


# Health check endpoint
@app.get(
    f"{settings.API_V1_PREFIX}/health",
    tags=["Health"]
)
def health_check():
    """
    Check whether the ResearchMate AI API is running.
    """

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "message": "ResearchMate AI API is running successfully."
    }