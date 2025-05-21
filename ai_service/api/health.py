from typing import Dict
from fastapi import APIRouter
import redis
from ..core.settings import get_settings
import os

router = APIRouter()
settings = get_settings()

async def check_redis() -> bool:
    try:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        return redis_client.ping()
    except Exception:
        return False

async def check_llama_model() -> bool:
    try:
        model_path = os.path.join(settings.MODEL_DIR, "llama.cpp")
        return os.path.exists(model_path)
    except Exception:
        return False

@router.get("/healthz", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint that verifies:
    - API is responsive
    - Redis connection is working
    - Llama model is available
    - OpenAI API key is configured
    """
    redis_healthy = await check_redis()
    llama_healthy = await check_llama_model()
    openai_healthy = bool(settings.OPENAI_API_KEY)
    
    status = "healthy" if all([redis_healthy, llama_healthy, openai_healthy]) else "unhealthy"
    
    return {
        "status": status,
        "redis": "up" if redis_healthy else "down",
        "llama_model": "available" if llama_healthy else "unavailable",
        "openai": "configured" if openai_healthy else "not_configured"
    } 