"""
Authentication endpoints including Keycloak webhook handlers.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Request, status
from pydantic import BaseModel
import logging
import hmac
import hashlib
from app.core.config.settings import Settings, get_settings
from app.services.keycloak_events import handle_keycloak_event
from app.core.monitoring import log_security_event
from app.services.auth import get_current_user, UserToken

logger = logging.getLogger(__name__)
router = APIRouter()

class KeycloakEvent(BaseModel):
    """Keycloak event webhook payload."""
    type: str
    time: int
    realmId: str
    clientId: str
    userId: str
    sessionId: str
    ipAddress: str
    details: Dict[str, Any]

def verify_webhook_signature(
    signature: str = Header(..., alias="X-Keycloak-Signature"),
    payload: bytes = None,
    settings: Settings = Depends(get_settings)
) -> bool:
    """Verify the Keycloak webhook signature."""
    if not settings.KEYCLOAK_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    expected_signature = hmac.new(
        settings.KEYCLOAK_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/webhook/keycloak", status_code=status.HTTP_200_OK)
async def keycloak_webhook(
    request: Request,
    event: KeycloakEvent,
    is_valid: bool = Depends(verify_webhook_signature)
):
    """
    Handle Keycloak webhook events.
    
    This endpoint receives events from Keycloak when users are updated, deleted,
    or other relevant events occur. It verifies the webhook signature and
    processes the event accordingly.
    """
    if not is_valid:
        await log_security_event(
            event_type="INVALID_WEBHOOK_SIGNATURE",
            details={"event_type": event.type},
            severity="ERROR"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    try:
        # Extract user data from the event
        user_data = {
            "username": event.details.get("username"),
            "email": event.details.get("email"),
            "sub": event.userId,
            "tenant_id": event.details.get("tenant_id"),
            "given_name": event.details.get("firstName"),
            "family_name": event.details.get("lastName")
        }
        
        # Handle the event
        await handle_keycloak_event(event.type, user_data)
        
        return {"status": "success", "message": f"Processed event: {event.type}"}
        
    except Exception as e:
        logger.error(f"Error processing Keycloak webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: UserToken = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.sub,
        "username": current_user.preferred_username,
        "email": current_user.email,
        "roles": current_user.roles,
        "given_name": current_user.given_name,
        "family_name": current_user.family_name
    } 