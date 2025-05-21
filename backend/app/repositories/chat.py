from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.chat import Conversation, Message, Feedback
from app.repositories.base import TenantRepository
from app.core.tenancy import get_current_tenant, TenantContextManager


class ConversationRepository(TenantRepository[Conversation]):
    """Repository for managing Conversation entities."""

    def __init__(self):
        super().__init__(Conversation)

    async def create_conversation(
        self,
        user_id: UUID,
        title: str
    ) -> Conversation:
        """Create a new conversation."""
        return await self.create(
            user_id=user_id,
            title=title
        )

    async def get_user_conversations(
        self,
        user_id: UUID,
        offset: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get conversations for a specific user."""
        return await self.list(
            offset=offset,
            limit=limit,
            user_id=user_id
        )

    async def get_conversation_with_messages(
        self,
        conversation_id: UUID,
        message_limit: int = 50
    ) -> Optional[Conversation]:
        """Get a conversation with its messages."""
        conversation = await self.get_by_id(conversation_id)
        if conversation:
            # Prefetch related messages
            await conversation.fetch_related("messages")
        return conversation

    async def search_conversations(
        self,
        user_id: UUID,
        search_term: str,
        offset: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Search conversations by title."""
        return await self.list(
            offset=offset,
            limit=limit,
            user_id=user_id,
            title__icontains=search_term
        )


class MessageRepository(TenantRepository[Message]):
    """Repository for managing Message entities."""

    def __init__(self):
        super().__init__(Message)

    async def create_message(
        self,
        conversation_id: UUID,
        content: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Create a new message in a conversation."""
        return await self.create(
            conversation_id=conversation_id,
            content=content,
            role=role,
            metadata=metadata
        )

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_timestamp: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages from a conversation with pagination."""
        filters = {"conversation_id": conversation_id}
        if before_timestamp:
            filters["timestamp__lt"] = before_timestamp
        
        return await self.list(
            limit=limit,
            **filters
        )

    async def get_latest_message(
        self,
        conversation_id: UUID
    ) -> Optional[Message]:
        """Get the latest message from a conversation."""
        messages = await self.model.filter(
            conversation_id=conversation_id,
            tenant_id=get_current_tenant(),
            is_active=True
        ).order_by("-timestamp").limit(1)
        return messages[0] if messages else None

    async def count_messages(
        self,
        conversation_id: UUID,
        role: Optional[str] = None
    ) -> int:
        """Count messages in a conversation, optionally filtered by role."""
        filters = {"conversation_id": conversation_id}
        if role:
            filters["role"] = role
        return await self.count(**filters)


class FeedbackRepository(TenantRepository[Feedback]):
    """Repository for managing Feedback entities."""

    def __init__(self):
        super().__init__(Feedback)

    async def create_feedback(
        self,
        message_id: UUID,
        user_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Create feedback for a message."""
        return await self.create(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )


class ChatRepository:
    """High level repository combining conversation and message operations."""

    def __init__(self) -> None:
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()
        self.feedback_repo = FeedbackRepository()

    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Retrieve a conversation by its ID."""
        return await self.conversation_repo.get_by_id(conversation_id)

    async def create_conversation(
        self,
        user_id: UUID,
        tenant_id: UUID,
        title: str = "New Conversation",
    ) -> Conversation:
        """Create a new conversation for a tenant."""
        async with TenantContextManager(tenant_id):
            return await self.conversation_repo.create_conversation(
                user_id=user_id,
                title=title,
            )

    async def get_messages(
        self,
        conversation_id: UUID,
        limit: int = 50,
        before_timestamp: Optional[datetime] = None,
    ) -> List[Message]:
        """Retrieve messages for a conversation."""
        return await self.message_repo.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit,
            before_timestamp=before_timestamp,
        )

    async def create_message(
        self,
        conversation_id: UUID,
        content: str,
        role: str,
        user_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """Create a message in a conversation."""
        # user_id parameter is accepted for interface compatibility
        return await self.message_repo.create_message(
            conversation_id=conversation_id,
            content=content,
            role=role,
            metadata=metadata,
        )

    async def create_feedback(
        self,
        message_id: UUID,
        user_id: UUID,
        rating: int,
        comment: Optional[str] = None,
    ) -> Feedback:
        """Store feedback for a message."""
        return await self.feedback_repo.create_feedback(
            message_id=message_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )

    async def close(self) -> None:
        """Placeholder for compatibility with dependency lifecycle."""
        return None
