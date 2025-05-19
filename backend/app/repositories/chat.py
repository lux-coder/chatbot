from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.chat import Conversation, Message
from app.repositories.base import TenantRepository
from app.core.tenancy import get_current_tenant


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