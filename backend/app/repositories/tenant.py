from typing import Optional
from uuid import UUID
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository

class TenantRepository(BaseRepository[Tenant]):
    """Repository for managing Tenant entities."""

    def __init__(self):
        super().__init__(Tenant)

    async def create_tenant(
        self,
        name: Optional[str] = None,
        settings: dict = None
    ) -> Tenant:
        """
        Create a new tenant.
        
        Args:
            name: Optional name of the tenant
            settings: Optional tenant-specific settings
        """
        return await self.create(
            name=name,
            settings=settings or {}
        )

    async def get_active_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get an active tenant by ID."""
        return await Tenant.get_active_tenant(tenant_id)

    async def update_tenant_settings(
        self,
        tenant_id: UUID,
        settings: dict
    ) -> Optional[Tenant]:
        """Update tenant settings."""
        tenant = await self.get_by_id(tenant_id)
        if tenant:
            tenant.settings.update(settings)
            await tenant.save(update_fields=["settings"])
        return tenant 