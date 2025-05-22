from typing import Optional
from uuid import UUID
from app.repositories.tenant import TenantRepository
from app.core.monitoring import log_security_event
from app.core.security.exceptions import TenantMismatchError
import logging

logger = logging.getLogger(__name__)

class TenantService:
    """Service for managing tenants."""

    def __init__(self):
        self.tenant_repo = TenantRepository()

    async def create_tenant(
        self,
        name: Optional[str] = None,
        settings: Optional[dict] = None
    ) -> UUID:
        """
        Create a new tenant.
        
        Args:
            name: Optional name of the tenant
            settings: Optional tenant-specific settings
            
        Returns:
            UUID of the created tenant
        """
        try:
            tenant = await self.tenant_repo.create_tenant(
                name=name,
                settings=settings
            )
            
            # Log tenant creation
            await log_security_event(
                event_type="TENANT_CREATED",
                tenant_id=str(tenant.id),
                details={
                    "name": name,
                    "success": True
                }
            )
            
            return tenant.id
            
        except Exception as e:
            logger.error(f"Error creating tenant: {str(e)}")
            await log_security_event(
                event_type="TENANT_CREATION_ERROR",
                details={
                    "name": name,
                    "error": str(e)
                },
                severity="ERROR"
            )
            raise

    async def get_tenant(self, tenant_id: UUID) -> Optional[dict]:
        """
        Get tenant details.
        
        Args:
            tenant_id: ID of the tenant
            
        Returns:
            Tenant details if found
        """
        tenant = await self.tenant_repo.get_active_tenant(tenant_id)
        if not tenant:
            return None
            
        return {
            "id": tenant.id,
            "name": tenant.name,
            "settings": tenant.settings,
            "created_at": tenant.created_at,
            "is_active": tenant.is_active
        }

    async def ensure_tenant_exists(self, tenant_id: UUID) -> bool:
        """
        Ensure a tenant exists and is active.
        
        Args:
            tenant_id: ID of the tenant to check
            
        Returns:
            True if tenant exists and is active
            
        Raises:
            TenantMismatchError: If tenant doesn't exist or is inactive
        """
        tenant = await self.tenant_repo.get_active_tenant(tenant_id)
        if not tenant:
            await log_security_event(
                event_type="TENANT_ACCESS_ERROR",
                tenant_id=str(tenant_id),
                details={"error": "Tenant not found or inactive"},
                severity="ERROR"
            )
            raise TenantMismatchError(f"Tenant {tenant_id} not found or inactive")
        return True 