from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime


class TenantBase(BaseModel):
    """Base Tenant schema."""
    name: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TenantCreate(TenantBase):
    """Schema for creating a tenant."""
    pass


class TenantInfoResponse(BaseModel):
    """Response schema for tenant info endpoint."""
    tenant_id: UUID
    name: Optional[str] = None
    is_active: bool = True


class TenantDetailResponse(TenantInfoResponse):
    """Detailed tenant response schema."""
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime 