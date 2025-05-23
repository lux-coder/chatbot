from uuid import UUID
from typing import Optional, List
from app.models.bot import ChatbotInstance
from app.repositories.base import TenantRepository

class ChatbotInstanceRepository(TenantRepository[ChatbotInstance]):
    """Repository for ChatbotInstance entities."""

    def __init__(self) -> None:
        super().__init__(ChatbotInstance)

    async def create_instance(
        self,
        user_id: UUID,
        name: str,
        style: str,
        language: str,
        icon: Optional[str] = None,
    ) -> ChatbotInstance:
        return await self.create(
            user_id=user_id,
            name=name,
            style=style,
            language=language,
            icon=icon,
        )

    async def list_instances(self, user_id: UUID, offset: int = 0, limit: int = 100) -> List[ChatbotInstance]:
        return await self.list(offset=offset, limit=limit, user_id=user_id)

    async def publish_instance(self, instance_id: UUID) -> Optional[ChatbotInstance]:
        instance = await self.get_by_id(instance_id)
        if instance:
            await instance.publish()
        return instance
