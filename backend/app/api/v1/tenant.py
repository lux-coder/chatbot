from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List, Optional

from app.services.auth import get_current_user, UserToken, AuthService
from app.services.tenant import TenantService
from app.api.deps import get_tenant_service
from app.schemas.tenant import TenantInfoResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenant", tags=["tenant"])

# Support both GET and POST methods
@router.get("/info", response_model=TenantInfoResponse)
@router.post("/info", response_model=TenantInfoResponse)
async def get_tenant_info(
    user: UserToken = Depends(get_current_user),
    tenant_service: TenantService = Depends(get_tenant_service),
):
    """
    Returns tenant information for the authenticated user.
    If the tenant doesn't exist, creates it automatically.
    
    This endpoint should be called after authentication to get the correct 
    tenant ID to use in subsequent API calls.
    
    Note: This endpoint doesn't require X-Tenant-ID header as it's used
    to discover the tenant ID.
    
    Supports both GET and POST methods.
    """
    try:
        # Use the user's ID from the token to find or create a tenant
        tenant = await tenant_service.get_or_create_tenant_for_user(user.sub)
        
        # Log successful tenant discovery
        logger.info(f"Tenant discovered for user {user.preferred_username}: {tenant['id']}")
        
        return TenantInfoResponse(
            tenant_id=tenant["id"],
            name=tenant["name"],
            is_active=tenant["is_active"]
        )
    except Exception as e:
        logger.error(f"Error getting tenant info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tenant info: {str(e)}"
        ) 