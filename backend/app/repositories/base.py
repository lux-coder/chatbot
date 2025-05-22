from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from uuid import UUID
from tortoise import Model
from tortoise.expressions import Q
from app.core.security.tenancy import get_current_tenant
from app.models.base import TenantModel

ModelType = TypeVar("ModelType", bound=Model)

class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        return await self.model.get_or_none(id=id, is_active=True)

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """List records with pagination and filters."""
        query = self.model.filter(is_active=True, **filters)
        return await query.offset(offset).limit(limit)

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        obj = await self.get_by_id(id)
        if obj:
            await obj.update_from_dict(kwargs).save()
        return obj

    async def delete(self, id: UUID) -> bool:
        """Soft delete a record by ID."""
        obj = await self.get_by_id(id)
        if obj:
            await obj.soft_delete()
            return True
        return False

    async def count(self, **filters) -> int:
        """Count records with filters."""
        return await self.model.filter(is_active=True, **filters).count()


class TenantRepository(BaseRepository[ModelType]):
    """Repository class for tenant-aware models."""

    async def create(self, **kwargs) -> ModelType:
        """Create a new record with tenant ID."""
        tenant_id = get_current_tenant()
        return await super().create(tenant_id=tenant_id, **kwargs)

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a record by ID within tenant context."""
        tenant_id = get_current_tenant()
        return await self.model.get_or_none(
            id=id,
            tenant_id=tenant_id,
            is_active=True
        )

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        **kwargs
    ) -> List[ModelType]:
        """List records within tenant context."""
        tenant_id = get_current_tenant()
        return await self.model.filter(
            tenant_id=tenant_id,
            is_active=True,
            **kwargs
        ).offset(offset).limit(limit)

    async def count(self, **filters) -> int:
        """Count records within tenant context."""
        tenant_id = get_current_tenant()
        return await self.model.filter(
            tenant_id=tenant_id,
            is_active=True,
            **filters
        ).count() 