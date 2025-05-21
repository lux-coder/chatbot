from tortoise import fields
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.base import TenantModel
from app.models.user import User


class Conversation(TenantModel):
    """Conversation model representing a chat session.
    
    Attributes:
        title: Title of the conversation
        user: User who owns the conversation
        created_at: When the conversation was created
        last_message_at: When the last message was sent
        is_active: Whether the conversation is active
    """
    
    title = fields.CharField(max_length=255)
    user = fields.ForeignKeyField('models.User', related_name='conversations')
    last_message_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "conversations"
        ordering = ["-last_message_at"]

    def __str__(self) -> str:
        return f"Conversation(title={self.title}, user={self.user_id})"

    async def get_messages(
        self,
        limit: int = 50,
        before_timestamp: Optional[datetime] = None
    ) -> List["Message"]:
        """Get messages in the conversation with pagination."""
        query = Message.filter(
            conversation_id=self.id,
            is_active=True
        ).order_by("-timestamp")

        if before_timestamp:
            query = query.filter(timestamp__lt=before_timestamp)

        return await query.limit(limit)

    async def add_message(
        self,
        content: str,
        role: str,
        metadata: Optional[dict] = None
    ) -> "Message":
        """Add a new message to the conversation."""
        message = await Message.create(
            conversation=self,
            content=content,
            role=role,
            metadata=metadata,
            tenant_id=self.tenant_id
        )
        self.last_message_at = message.timestamp
        await self.save(update_fields=["last_message_at"])
        return message


class Message(TenantModel):
    """Message model representing a single message in a conversation.
    
    Attributes:
        conversation: The conversation this message belongs to
        content: The message content
        role: The role of the sender (user, assistant, system)
        timestamp: When the message was sent
        metadata: Additional message metadata (e.g., tokens, model used)
    """
    
    conversation = fields.ForeignKeyField(
        'models.Conversation',
        related_name='messages',
        on_delete=fields.CASCADE
    )
    content = fields.TextField()
    role = fields.CharField(max_length=20)  # user, assistant, system
    timestamp = fields.DatetimeField(auto_now_add=True)
    metadata = fields.JSONField(null=True)

    class Meta:
        table = "messages"
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"Message(role={self.role}, conversation={self.conversation_id})"

    @property
    def is_user_message(self) -> bool:
        """Check if the message is from a user."""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if the message is from the assistant."""
        return self.role == "assistant"

    @property
    def is_system_message(self) -> bool:
        """Check if the message is a system message."""
        return self.role == "system"


class Feedback(TenantModel):
    """Feedback on a specific message."""

    message = fields.ForeignKeyField(
        'models.Message',
        related_name='feedback',
        on_delete=fields.CASCADE
    )
    user = fields.ForeignKeyField(
        'models.User',
        related_name='feedback',
        on_delete=fields.CASCADE
    )
    rating = fields.IntField()
    comment = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "feedback"

    def __str__(self) -> str:
        return (
            f"Feedback(message={self.message_id}, user={self.user_id}, "
            f"rating={self.rating})"
        )
