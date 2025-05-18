from tortoise import Model, fields
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


class BaseModel(Model):
    """Base model class with common fields for all models."""
    
    id: UUID = fields.UUIDField(pk=True, default=uuid4)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    is_active: bool = fields.BooleanField(default=True)

    class Meta:
        abstract = True

    async def soft_delete(self) -> None:
        """Soft delete the record by setting is_active to False."""
        self.is_active = False
        await self.save()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"


class TenantModel(BaseModel):
    """Base model class for multi-tenant models."""
    
    tenant_id: UUID = fields.UUIDField()
    
    class Meta:
        abstract = True

    @classmethod
    async def get_by_id_and_tenant(cls, id: UUID, tenant_id: UUID) -> Optional["TenantModel"]:
        """Get a record by ID and tenant_id."""
        return await cls.get_or_none(id=id, tenant_id=tenant_id, is_active=True)

    @classmethod
    async def filter_by_tenant(cls, tenant_id: UUID, **kwargs) -> list["TenantModel"]:
        """Filter records by tenant_id and additional filters."""
        return await cls.filter(tenant_id=tenant_id, is_active=True, **kwargs) 