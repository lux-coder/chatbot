from uuid import UUID
from typing import List, Optional, Dict, Any
from app.repositories.bot import ChatbotInstanceRepository
from app.repositories.chat import ChatRepository
from app.core.security.tenancy import TenantContextManager
from app.models.bot import ChatbotInstance

class ChatbotInstanceService:
    def __init__(self):
        self.repo = ChatbotInstanceRepository()
        self.chat_repo = ChatRepository()

    async def create_instance(
        self,
        user_id: UUID,
        tenant_id: UUID,
        name: str,
        style: str,
        language: str,
        icon: Optional[str] = None,
    ) -> ChatbotInstance:
        async with TenantContextManager(tenant_id):
            return await self.repo.create_instance(
                user_id=user_id,
                name=name,
                style=style,
                language=language,
                icon=icon,
            )

    async def list_instances(self, user_id: UUID, tenant_id: UUID) -> List[ChatbotInstance]:
        async with TenantContextManager(tenant_id):
            return await self.repo.list_instances(user_id)

    async def delete_instance(self, instance_id: UUID, tenant_id: UUID) -> bool:
        async with TenantContextManager(tenant_id):
            return await self.repo.delete(instance_id)

    async def publish_instance(self, instance_id: UUID, tenant_id: UUID) -> Optional[ChatbotInstance]:
        async with TenantContextManager(tenant_id):
            return await self.repo.publish_instance(instance_id)

    async def get_instance_conversations(
        self, 
        instance_id: UUID,
        tenant_id: UUID,
        user_id: UUID,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a specific bot instance."""
        async with TenantContextManager(tenant_id):
            # First verify the bot instance exists and user has access
            instance = await self.repo.get_by_id(instance_id)
            if not instance:
                raise ValueError(f"Bot instance {instance_id} not found")
                
            if instance.user_id != user_id:
                raise ValueError(f"User {user_id} doesn't have access to bot instance {instance_id}")
            
            # Get conversations
            conversations = await self.chat_repo.get_bot_conversations(
                chatbot_instance_id=instance_id,
                tenant_id=tenant_id,
                offset=offset,
                limit=limit
            )
            
            # Convert to dict for API response
            return [
                {
                    "conversation_id": conv.id,
                    "title": conv.title,
                    "last_message_at": conv.last_message_at,
                    "chatbot_instance_id": conv.chatbot_instance_id
                }
                for conv in conversations
            ]
