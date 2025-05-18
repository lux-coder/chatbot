from celery.app.control import Inspect
from typing import Dict
import redis
from worker.main import app as celery_app
from worker.config import get_settings

settings = get_settings()

def check_celery() -> bool:
    """Check if Celery workers are running and responding"""
    try:
        insp = Inspect(app=celery_app)
        return bool(insp.ping())
    except Exception:
        return False

def check_redis() -> bool:
    """Check Redis connection"""
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

def get_health_status() -> Dict[str, str]:
    """
    Get health status of the worker service
    Returns:
        Dict with status of different components
    """
    celery_healthy = check_celery()
    redis_healthy = check_redis()
    
    status = "healthy" if all([celery_healthy, redis_healthy]) else "unhealthy"
    
    return {
        "status": status,
        "celery": "up" if celery_healthy else "down",
        "redis": "up" if redis_healthy else "down"
    } 