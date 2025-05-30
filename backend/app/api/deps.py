"""
Dependencies Module

This module provides FastAPI dependency injection functions for services and repositories.
"""

from typing import AsyncGenerator, Callable, Awaitable
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.chat import ChatRepository
from app.services.chat import ChatService
from app.services.ai import AIService
from app.services.tenant import TenantService
from app.services.bot import ChatbotInstanceService
from app.services.prompt_filter import PromptFilterService

async def get_chat_repository() -> AsyncGenerator[ChatRepository, None]:
    """
    Dependency provider for ChatRepository.
    """
    repository = ChatRepository()  # Repository should handle its own DB connection
    try:
        yield repository
    finally:
        await repository.close()  # Ensure cleanup of any resources

async def get_ai_service(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[AIService, None]:
    """
    Dependency provider for AIService.
    
    Creates an AIService instance with proper configuration and cleanup.
    """
    service = AIService(settings)
    try:
        yield service
    finally:
        await service.client.aclose()

async def get_prompt_filter_service(
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[PromptFilterService, None]:
    """
    Dependency provider for PromptFilterService.
    
    Creates a PromptFilterService instance with proper configuration and cleanup.
    """
    service = PromptFilterService(settings)
    try:
        yield service
    finally:
        await service.close()

async def get_chat_service(
    chat_repository: ChatRepository = Depends(get_chat_repository),
    ai_service: AIService = Depends(get_ai_service),
    prompt_filter_service: PromptFilterService = Depends(get_prompt_filter_service),
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[ChatService, None]:
    """
    Dependency provider for ChatService.
    """
    service = ChatService(
        chat_repository=chat_repository,
        ai_service=ai_service,
        prompt_filter_service=prompt_filter_service,
        settings=settings
    )
    try:
        yield service
    finally:
        # Any cleanup needed for the chat service
        pass

def get_tenant_service() -> TenantService:
    """Dependency for getting a TenantService instance."""
    return TenantService()

def get_bot_service() -> ChatbotInstanceService:
    """Dependency for ChatbotInstanceService."""
    return ChatbotInstanceService()
