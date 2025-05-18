from typing import Dict
from fastapi import APIRouter, Depends
from tortoise import connections
import redis
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

async def check_database() -> bool:
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return True
    except Exception:
        return False

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

@router.get("/healthz", response_model=Dict[str, str])
async def health_check():
    """
    Health check endpoint that verifies:
    - API is responsive
    - Database connection is working
    - Redis connection is working
    """
    db_healthy = await check_database()
    redis_healthy = await check_redis()
    
    status = "healthy" if db_healthy and redis_healthy else "unhealthy"
    
    return {
        "status": status,
        "database": "up" if db_healthy else "down",
        "redis": "up" if redis_healthy else "down"
    } 