from uuid import UUID
from typing import List, Optional
from app.repositories.bot import ChatbotInstanceRepository
from app.core.security.tenancy import TenantContextManager
from app.models.bot import ChatbotInstance

class ChatbotInstanceService:
    def __init__(self):
        self.repo = ChatbotInstanceRepository()

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
