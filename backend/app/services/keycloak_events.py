"""
Module for handling Keycloak events and webhooks.
"""

from typing import Dict, Any
from uuid import UUID
import logging
from fastapi import HTTPException, status
from app.repositories.user import UserRepository
from app.core.security.tenancy import TenantContextManager
from app.core.monitoring import log_security_event

logger = logging.getLogger(__name__)

async def handle_keycloak_event(event_type: str, user_data: dict) -> None:
    """
    Handle Keycloak webhook events for user changes.
    
    Args:
        event_type: Type of event (USER_UPDATE, USER_DELETE, etc.)
        user_data: User data from Keycloak event
    """
    if event_type not in ["USER_UPDATE", "USER_DELETE"]:
        logger.debug(f"Ignoring unsupported event type: {event_type}")
        return

    user_repo = UserRepository()
    try:
        async with TenantContextManager(UUID(user_data["tenant_id"])):
            user = await user_repo.get_by_username(user_data["username"])
            
            if not user:
                logger.warning(f"User not found for event {event_type}: {user_data['username']}")
                return
                
            if event_type == "USER_DELETE":
                await user.soft_delete()
                logger.info(f"Soft deleted user: {user_data['username']}")
                
            elif event_type == "USER_UPDATE":
                await user_repo.update_user_profile(
                    user_id=user.id,
                    email=user_data.get("email"),
                    first_name=user_data.get("given_name"),
                    last_name=user_data.get("family_name")
                )
                logger.info(f"Updated user profile: {user_data['username']}")
                
            # Log the event
            await log_security_event(
                event_type=f"KEYCLOAK_{event_type}",
                tenant_id=str(user.tenant_id),
                user_id=str(user.id),
                details={
                    "username": user_data["username"],
                    "success": True
                }
            )
                
    except Exception as e:
        error_msg = f"Error handling Keycloak event: {str(e)}"
        logger.error(error_msg)
        await log_security_event(
            event_type=f"KEYCLOAK_{event_type}_ERROR",
            tenant_id=user_data.get("tenant_id"),
            user_id=user_data.get("sub"),
            details={
                "username": user_data.get("username"),
                "success": False,
                "error": str(e)
            },
            severity="ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        ) 