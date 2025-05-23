"""
AI Service Module

This module provides integration with the external AI service supporting both
OpenAI and Llama.cpp models.
"""

import json
import hashlib
from datetime import timedelta
import httpx
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel
import redis.asyncio as redis
from app.core.config import Settings
from app.core.monitoring import log_chat_event
import logging

class ModelType(str, Enum):
    """Supported AI model types"""
    OPENAI = "openai"
    LLAMA = "llama"

class AIRequest(BaseModel):
    """Request model for AI service"""
    message: str
    context: List[Dict[str, Any]]
    model_type: ModelType = ModelType.OPENAI  # Default to OpenAI
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class AIResponse(BaseModel):
    """Response model from AI service"""
    content: str
    model_used: str
    tokens_used: int

class AIService:
    """
    Service for interacting with AI models through the external AI service.
    
    This service communicates with the dedicated AI service module that handles
    both OpenAI and Llama.cpp integrations.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the AI service.
        
        Args:
            settings: Application settings containing AI service configuration
        """
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.AI_SERVICE_URL,
            timeout=settings.AI_TIMEOUT_SECONDS
        )
        self.fallback_enabled = settings.AI_FALLBACK_ENABLED
        
        # Initialize Redis connection
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Cache settings
        self.cache_ttl = timedelta(hours=24)  # Cache responses for 24 hours
        self.cache_enabled = True  # Can be disabled for debugging

    def _generate_cache_key(
        self,
        message: str,
        context: List[Dict[str, Any]],
        model_type: ModelType
    ) -> str:
        """
        Generate a unique cache key for a request.
        
        Args:
            message: The user's message
            context: Conversation context
            model_type: Type of model being used
            
        Returns:
            A unique hash string for the request
        """
        # Create a deterministic string representation of the request
        cache_data = {
            "message": message,
            "context": context,
            "model_type": model_type.value
        }
        
        # Generate a hash of the request data
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"ai_response:{hashlib.sha256(cache_string.encode()).hexdigest()}"

    async def _get_cached_response(self, cache_key: str) -> Optional[AIResponse]:
        """
        Try to get a cached response.
        
        Args:
            cache_key: The cache key to look up
            
        Returns:
            Cached AIResponse if found, None otherwise
        """
        if not self.cache_enabled:
            return None
            
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                response_data = json.loads(cached)
                await log_chat_event(
                    event_type="ai_cache_hit",
                    cache_key=cache_key
                )
                return AIResponse(**response_data)
        except Exception as e:
            await log_chat_event(
                event_type="ai_cache_error",
                error_type=str(type(e).__name__),
                error_message=str(e)
            )
        return None

    async def _cache_response(self, cache_key: str, response: AIResponse) -> None:
        """
        Cache an AI response.
        
        Args:
            cache_key: The cache key to store under
            response: The response to cache
        """
        if not self.cache_enabled:
            return
            
        try:
            await self.redis.set(
                cache_key,
                json.dumps(response.model_dump()),
                ex=int(self.cache_ttl.total_seconds())
            )
            await log_chat_event(
                event_type="ai_cache_store",
                cache_key=cache_key
            )
        except Exception as e:
            await log_chat_event(
                event_type="ai_cache_error",
                error_type=str(type(e).__name__),
                error_message=str(e)
            )

    async def generate_response(
        self,
        message: str,
        context: List[Dict[str, Any]],
        model_type: ModelType = ModelType.OPENAI
    ) -> str:
        """
        Generate a response using the specified AI model.
        
        Args:
            message: The user's message
            context: List of previous messages for context
            model_type: Type of model to use (openai or llama)
            
        Returns:
            The generated response text
            
        Raises:
            AIServiceError: If both primary and fallback attempts fail
        """
        # Try to get cached response first
        cache_key = self._generate_cache_key(message, context, model_type)
        cached_response = await self._get_cached_response(cache_key)
        
        if cached_response:
            return cached_response.content
            
        try:
            response = await self._call_ai_service(
                message=message,
                context=context,
                model_type=model_type
            )
            
            # Cache the successful response
            await self._cache_response(cache_key, response)
            
            # Log successful AI call
            await log_chat_event(
                event_type="ai_response_generated",
                model_type=model_type.value,
                tokens_used=response.tokens_used
            )
            
            return response.content
            
        except Exception as e:
            # Log the error
            await log_chat_event(
                event_type="ai_error",
                error_type=str(type(e).__name__),
                error_message=str(e),
                model_type=model_type.value
            )
            
            # Try fallback if enabled and not already using fallback
            if self.fallback_enabled and model_type != ModelType.LLAMA:
                try:
                    # Attempt with Llama as fallback
                    return await self.generate_response(
                        message=message,
                        context=context,
                        model_type=ModelType.LLAMA
                    )
                except Exception as fallback_error:
                    # Log fallback error
                    await log_chat_event(
                        event_type="ai_fallback_error",
                        error_type=str(type(fallback_error).__name__),
                        error_message=str(fallback_error)
                    )
                    raise AIServiceError(
                        "Both primary and fallback AI attempts failed"
                    ) from fallback_error
            
            raise AIServiceError(str(e)) from e

    async def _call_ai_service(
        self,
        message: str,
        context: List[Dict[str, Any]],
        model_type: ModelType
    ) -> AIResponse:
        """
        Make the actual call to the AI service.
        
        Args:
            message: The user's message
            context: List of previous messages for context
            model_type: Type of model to use
            
        Returns:
            AIResponse object containing the generated response
            
        Raises:
            httpx.HTTPError: If the HTTP request fails
            ValidationError: If the response doesn't match expected format
        """
        request = AIRequest(
            message=message,
            context=context if context is not None else [],  # Ensure list
            model_type=model_type.value  # Convert enum to string
        )
        # Debug log outgoing payload
        logging.getLogger(__name__).info(f"Sending to AI service: {request.model_dump()}")
        response = await self.client.post(
            "/api/v1/generate",
            json=request.model_dump()
        )
        if response.status_code != 200:
            logging.getLogger(__name__).error(f"AI service error response: {response.text}")
        response.raise_for_status()
        return AIResponse(**response.json())

class AIServiceError(Exception):
    """Raised when the AI service encounters an error"""
    pass 