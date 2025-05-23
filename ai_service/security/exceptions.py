"""
Exception handling for the AI service.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler for the AI service"""
    error_id = str(request.scope["client"][0])
    logger.error(f"Unhandled exception from {error_id}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred during text generation"}
    )
