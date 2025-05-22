from tortoise import fields
from uuid import UUID
from typing import Optional
from app.models.base import BaseModel

class Tenant(BaseModel):
    """
    Tenant model for multi-tenant support.
    
    This model represents a tenant in the system. Each tenant is a separate
    organization or entity that has its own users and data.
    
    Attributes:
        name: Name of the tenant (optional for now as per requirements)
        settings: JSON field for tenant-specific settings
        is_active: Whether the tenant is active
    """
    
    name = fields.CharField(max_length=255, null=True)
    settings = fields.JSONField(default=dict)
    
    class Meta:
        table = "tenants"
    
    def __str__(self) -> str:
        return f"Tenant(id={self.id}, name={self.name})"
    
    @classmethod
    async def get_active_tenant(cls, tenant_id: UUID) -> Optional["Tenant"]:
        """Get an active tenant by ID."""
        return await cls.get_or_none(id=tenant_id, is_active=True) 