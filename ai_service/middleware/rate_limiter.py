"""
Rate Limiter Middleware

This module provides rate limiting functionality using Redis.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from core.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app):
        """Initialize the middleware"""
        super().__init__(app)
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self.window = settings.RATE_LIMIT_WINDOW
        self.max_calls = settings.RATE_LIMIT_CALLS
    
    async def dispatch(self, request: Request, call_next):
        """Process each request through rate limiting"""
        
        # Skip rate limiting for health check and docs
        if request.url.path in ["/healthz", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        try:
            # Get client identifier (IP address or API key)
            client_id = self._get_client_id(request)
            
            # Check rate limit
            if not await self._check_rate_limit(client_id):
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
        except Exception as e:
            # Log error but don't block requests if Redis is unavailable
            logger.error(f"Rate limiter error: {str(e)}")
        
        # Process the request
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get a unique identifier for the client"""
        # Use API key if available
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key}"
        
        # Fallback to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        return f"ip:{request.client.host}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """
        Check if the client has exceeded their rate limit.
        
        Uses a sliding window implementation with Redis sorted sets.
        """
        try:
            key = f"ratelimit:{client_id}"
            now = await self.redis.time()
            now = now[0]  # Get current timestamp
            
            # Remove old entries
            await self.redis.zremrangebyscore(
                key,
                "-inf",
                now - self.window
            )
            
            # Count recent requests
            recent_calls = await self.redis.zcard(key)
            
            if recent_calls >= self.max_calls:
                return False
            
            # Add current request
            pipeline = self.redis.pipeline()
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, self.window)
            await pipeline.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            # If Redis fails, allow the request
            return True 