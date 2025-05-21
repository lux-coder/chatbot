"""
Chat Service Module

This module implements the core chat functionality, handling message processing,
conversation management, and integration with AI models.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
import asyncio
from fastapi import HTTPException

from app.repositories.chat import ChatRepository
from app.models.chat import Message, Conversation
from app.core.config import Settings
from app.core.monitoring import log_chat_event
from app.services.ai import AIService, AIServiceError, ModelType
from app.core.security import PIIHandler
from app.core.exceptions import TenantMismatchError

class ChatService:
    """
    Core chat service handling message processing, history management, and feedback.
    
    Attributes:
        chat_repository: Repository for chat-related database operations
        ai_service: Service for AI model interactions
        settings: Application settings
        pii_handler: Handler for PII detection and masking
    """
    
    def __init__(
        self,
        chat_repository: ChatRepository,
        ai_service: AIService,
        settings: Settings
    ):
        self.chat_repository = chat_repository
        self.ai_service = ai_service
        self.settings = settings
        self.pii_handler = PIIHandler()
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    async def _get_or_create_conversation(
        self,
        user_id: UUID,
        tenant_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """
        Get an existing conversation or create a new one.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            conversation_id: Optional ID of existing conversation
            
        Returns:
            Conversation object
            
        Raises:
            TenantMismatchError: If conversation exists but belongs to different tenant
            HTTPException: If conversation not found or other errors occur
        """
        try:
            if conversation_id:
                conversation = await self.chat_repository.get_conversation(conversation_id)
                if not conversation:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Conversation {conversation_id} not found"
                    )
                
                # Verify tenant ownership
                if conversation.tenant_id != tenant_id:
                    await log_chat_event(
                        event_type="security_violation",
                        user_id=user_id,
                        tenant_id=tenant_id,
                        conversation_id=conversation_id,
                        details="Tenant mismatch in conversation access"
                    )
                    raise TenantMismatchError(
                        f"Conversation {conversation_id} does not belong to tenant {tenant_id}"
                    )
                return conversation
                
            return await self.chat_repository.create_conversation(
                user_id=user_id,
                tenant_id=tenant_id
            )
        except Exception as e:
            await log_chat_event(
                event_type="conversation_error",
                user_id=user_id,
                tenant_id=tenant_id,
                error_type=str(type(e).__name__),
                error_message=str(e)
            )
            raise

    async def _get_conversation_context(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and format recent messages as context for the AI model.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of previous messages to include
            
        Returns:
            List of formatted messages for context
        """
        messages = await self.chat_repository.get_messages(
            conversation_id=conversation_id,
            limit=limit
        )
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    async def process_message(
        self,
        user_id: UUID,
        tenant_id: UUID,
        message: str,
        conversation_id: Optional[UUID] = None,
        model_type: ModelType = ModelType.OPENAI
    ) -> Dict[str, Any]:
        """
        Process a user message and generate an AI response.
        
        Args:
            user_id: ID of the user sending the message
            tenant_id: ID of the tenant
            message: Content of the user's message
            conversation_id: Optional ID of existing conversation
            model_type: Type of AI model to use
            
        Returns:
            Dict containing conversation ID, AI response, and timestamp
            
        Raises:
            HTTPException: For various error conditions
            TenantMismatchError: If conversation belongs to different tenant
        """
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                user_id, tenant_id, conversation_id
            )
            
            # Get conversation context
            context = await self._get_conversation_context(conversation.id)
            
            # Detect and mask PII in user message
            masked_message = await self.pii_handler.process_text(message)
            
            # Process through AI service with retries
            for attempt in range(self.max_retries):
                try:
                    ai_response = await self.ai_service.generate_response(
                        message=masked_message,
                        context=context,
                        model_type=model_type
                    )
                    break
                except AIServiceError as e:
                    if attempt == self.max_retries - 1:
                        raise HTTPException(
                            status_code=503,
                            detail="AI service temporarily unavailable"
                        )
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
            
            # Detect and mask any PII in AI response
            masked_ai_response = await self.pii_handler.process_text(ai_response)
            
            # Store messages
            user_message = await self.chat_repository.create_message(
                conversation_id=conversation.id,
                content=masked_message,
                role="user",
                user_id=user_id
            )
            
            ai_message = await self.chat_repository.create_message(
                conversation_id=conversation.id,
                content=masked_ai_response,
                role="assistant"
            )
            
            # Log successful event
            await log_chat_event(
                event_type="message_processed",
                user_id=user_id,
                tenant_id=tenant_id,
                conversation_id=conversation.id,
                model_type=model_type.value
            )
            
            return {
                "conversation_id": conversation.id,
                "message": ai_message.content,
                "created_at": ai_message.created_at
            }
            
        except Exception as e:
            # Log error event
            await log_chat_event(
                event_type="message_processing_error",
                user_id=user_id,
                tenant_id=tenant_id,
                conversation_id=conversation_id if conversation_id else None,
                error_type=str(type(e).__name__),
                error_message=str(e)
            )
            raise 