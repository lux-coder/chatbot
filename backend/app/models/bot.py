from tortoise import fields
from datetime import datetime
from app.models.base import TenantModel
from app.models.user import User

class ChatbotInstance(TenantModel):
    """Model storing user-defined chatbot settings."""

    user = fields.ForeignKeyField('models.User', related_name='chatbots')
    name = fields.CharField(max_length=255)
    style = fields.CharField(max_length=255)
    language = fields.CharField(max_length=50)
    icon = fields.CharField(max_length=255, null=True)
    is_published = fields.BooleanField(default=False)
    published_at = fields.DatetimeField(null=True)

    class Meta:
        table = "chatbot_instances"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ChatbotInstance(id={self.id}, user={self.user_id})"

    async def publish(self) -> None:
        """Mark the chatbot instance as published."""
        self.is_published = True
        self.published_at = datetime.utcnow()
        await self.save(update_fields=["is_published", "published_at"])
