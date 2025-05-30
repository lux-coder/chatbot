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
from app.services.prompt_filter import PromptFilterService, FilterAction
from app.core.security import PIIHandler
from app.core.security.exceptions import TenantMismatchError

class ChatService:
    """
    Core chat service handling message processing, history management, and feedback.
    
    Attributes:
        chat_repository: Repository for chat-related database operations
        ai_service: Service for AI model interactions
        prompt_filter_service: Service for filtering prompts
        settings: Application settings
        pii_handler: Handler for PII detection and masking
    """
    
    def __init__(
        self,
        chat_repository: ChatRepository,
        ai_service: AIService,
        prompt_filter_service: PromptFilterService,
        settings: Settings
    ):
        self.chat_repository = chat_repository
        self.ai_service = ai_service
        self.prompt_filter_service = prompt_filter_service
        self.settings = settings
        self.pii_handler = PIIHandler()
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    async def _get_or_create_conversation(
        self,
        user_id: UUID,
        tenant_id: UUID,
        chatbot_instance_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Conversation:
        """
        Get an existing conversation or create a new one.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            chatbot_instance_id: ID of the bot instance
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
                    
                # Verify bot instance ownership
                if conversation.chatbot_instance_id != chatbot_instance_id:
                    await log_chat_event(
                        event_type="security_violation",
                        user_id=user_id,
                        tenant_id=tenant_id,
                        conversation_id=conversation_id,
                        details="Bot instance mismatch in conversation access"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Conversation {conversation_id} does not belong to bot instance {chatbot_instance_id}"
                    )
                return conversation
                
            return await self.chat_repository.create_conversation(
                user_id=user_id,
                tenant_id=tenant_id,
                chatbot_instance_id=chatbot_instance_id
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
        chatbot_instance_id: UUID,
        message: str,
        conversation_id: Optional[UUID] = None,
        model_type: ModelType = ModelType.OPENAI
    ) -> Dict[str, Any]:
        """
        Process a user message and generate an AI response.
        
        Args:
            user_id: ID of the user sending the message
            tenant_id: ID of the tenant
            chatbot_instance_id: ID of the bot instance
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
            # Apply prompt filtering first
            filter_result = await self.prompt_filter_service.filter_prompt(
                content=message,
                user_id=str(user_id),
                tenant_id=str(tenant_id)
            )
            
            # If prompt is blocked, return appropriate response
            if not filter_result.is_allowed:
                await log_chat_event(
                    event_type="message_blocked",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    chatbot_instance_id=chatbot_instance_id,
                    details={
                        "filter_action": filter_result.action,
                        "triggered_filters": filter_result.triggered_filters,
                        "moderation_flagged": filter_result.moderation_flagged
                    }
                )
                
                # Create a system message to store the blocked attempt
                conversation = await self._get_or_create_conversation(
                    user_id, tenant_id, chatbot_instance_id, conversation_id
                )
                
                # Store the original user message (for audit purposes)
                await self.chat_repository.create_message(
                    conversation_id=conversation.id,
                    content=message,
                    role="user",
                    user_id=user_id,
                    metadata={"blocked": True, "filter_result": filter_result.model_dump()}
                )
                
                # Store the system response
                system_message = await self.chat_repository.create_message(
                    conversation_id=conversation.id,
                    content=filter_result.message or "🚫 Your message was blocked by our content filter.",
                    role="system",
                    metadata={"filter_block": True}
                )
                
                return {
                    "message_id": system_message.id,
                    "conversation_id": conversation.id,
                    "content": system_message.content,
                    "role": system_message.role,
                    "timestamp": system_message.timestamp,
                    "metadata": system_message.metadata,
                }
            
            # Use filtered content if sanitization occurred
            processed_message = filter_result.filtered_content or message
            
            # Log sanitization if it occurred
            if filter_result.action == FilterAction.SANITIZE:
                await log_chat_event(
                    event_type="message_sanitized",
                    user_id=user_id,
                    tenant_id=tenant_id,
                    chatbot_instance_id=chatbot_instance_id,
                    details={
                        "triggered_filters": filter_result.triggered_filters
                    }
                )
            
            # Get or create conversation
            conversation = await self._get_or_create_conversation(
                user_id, tenant_id, chatbot_instance_id, conversation_id
            )
            
            # Get conversation context
            context = await self._get_conversation_context(conversation.id)
            
            # Detect and mask PII in processed message
            masked_message = await self.pii_handler.process_text(processed_message)
            
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
            user_message_metadata = {}
            if filter_result.action == FilterAction.SANITIZE:
                user_message_metadata.update({
                    "sanitized": True,
                    "sanitization_message": filter_result.message,
                    "triggered_filters": filter_result.triggered_filters
                })
            
            user_message = await self.chat_repository.create_message(
                conversation_id=conversation.id,
                content=masked_message,
                role="user",
                user_id=user_id,
                metadata=user_message_metadata if user_message_metadata else None
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
                model_type=model_type.value,
                details={
                    "filter_applied": filter_result.action != FilterAction.ALLOW,
                    "sanitized": filter_result.action == FilterAction.SANITIZE
                }
            )
            
            # Prepare response with sanitization warning if applicable
            response_content = ai_message.content
            response_metadata = ai_message.metadata or {}
            
            if filter_result.action == FilterAction.SANITIZE and filter_result.message:
                response_metadata["sanitization_warning"] = filter_result.message
            
            return {
                "message_id": ai_message.id,
                "conversation_id": conversation.id,
                "content": response_content,
                "role": ai_message.role,
                "timestamp": ai_message.timestamp,
                "metadata": response_metadata,
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

    async def get_chat_history(
        self,
        user_id: UUID,
        tenant_id: UUID,
        conversation_id: UUID,
    ) -> Dict[str, Any]:
        """Return structured chat history for a conversation."""
        try:
            conversation = await self.chat_repository.get_conversation(conversation_id)
            if not conversation or conversation.tenant_id != tenant_id or conversation.user_id != user_id:
                raise HTTPException(status_code=404, detail="Conversation not found")

            messages = await self.chat_repository.get_messages(conversation_id)
            history = [
                {
                    "message_id": msg.id,
                    "content": msg.content,
                    "role": msg.role,
                    "timestamp": msg.timestamp,
                    "metadata": msg.metadata,
                }
                for msg in messages
            ]
            return {
                "conversation_id": conversation.id,
                "title": conversation.title,
                "last_message_at": conversation.last_message_at,
                "messages": history,
            }
        except Exception as e:
            await log_chat_event(
                event_type="history_error",
                user_id=user_id,
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                error_type=str(type(e).__name__),
                error_message=str(e),
            )
            raise

    async def store_feedback(
        self,
        message_id: UUID,
        user_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Persist feedback for a message."""
        try:
            feedback = await self.chat_repository.create_feedback(
                message_id=message_id,
                user_id=user_id,
                rating=rating,
                comment=comment,
            )
            await log_chat_event(
                event_type="feedback_received",
                user_id=user_id,
                message_id=message_id,
                rating=rating,
            )
            return {
                "feedback_id": feedback.id,
                "message_id": feedback.message_id,
                "rating": feedback.rating,
                "comment": feedback.comment,
                "created_at": feedback.created_at,
            }
        except Exception as e:
            await log_chat_event(
                event_type="feedback_error",
                user_id=user_id,
                message_id=message_id,
                error_type=str(type(e).__name__),
                error_message=str(e),
            )
            raise

    async def get_bot_conversations(
        self,
        user_id: UUID,
        tenant_id: UUID,
        chatbot_instance_id: UUID,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all conversations for a specific bot instance.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            chatbot_instance_id: ID of the bot instance
            offset: Pagination offset
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation details
        """
        try:
            conversations = await self.chat_repository.get_bot_conversations(
                chatbot_instance_id=chatbot_instance_id,
                tenant_id=tenant_id,
                offset=offset,
                limit=limit
            )
            
            # Filter to ensure user only sees their own conversations
            user_conversations = [c for c in conversations if c.user_id == user_id]
            
            return [
                {
                    "conversation_id": conv.id,
                    "title": conv.title,
                    "last_message_at": conv.last_message_at,
                    "chatbot_instance_id": conv.chatbot_instance_id
                }
                for conv in user_conversations
            ]
        except Exception as e:
            await log_chat_event(
                event_type="bot_conversations_error",
                user_id=user_id,
                tenant_id=tenant_id,
                chatbot_instance_id=chatbot_instance_id,
                error_type=str(type(e).__name__),
                error_message=str(e)
            )
            raise
