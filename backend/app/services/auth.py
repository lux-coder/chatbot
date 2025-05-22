from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from jose.constants import ALGORITHMS
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
import os
import logging
import base64
from uuid import UUID
from app.repositories.user import UserRepository
from app.core.security.tenancy import TenantContextManager
from app.core.monitoring import log_security_event
from app.services.tenant import TenantService
from app.core.security.exceptions import TenantMismatchError

logger = logging.getLogger(__name__)

# Constants (should be moved to config)
KEYCLOAK_ISSUER = "http://keycloak:8080/realms/chatbot"
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_CLIENT_ID", "chatbot-frontend")
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

class UserToken(BaseModel):
    sub: str
    email: str = ""
    preferred_username: str = ""
    roles: List[str] = []
    tenant_id: UUID  # Required UUID field, no default value
    given_name: str = ""
    family_name: str = ""
    payload: Dict[str, Any] = {}  # Store full token payload for additional data

def decode_value(val: str) -> int:
    """Decode JWT base64 value to integer."""
    decoded = base64.urlsafe_b64decode(val + '=' * (-len(val) % 4))
    return int.from_bytes(decoded, 'big')

def jwk_to_public_key(jwk: dict) -> str:
    """Convert JWK to PEM format."""
    e = decode_value(jwk['e'])
    n = decode_value(jwk['n'])
    
    public_numbers = RSAPublicNumbers(e=e, n=n)
    public_key = public_numbers.public_key(backend=default_backend())
    
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem

async def get_jwks() -> Dict[str, Any]:
    """Fetch JWKS from Keycloak."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(KEYCLOAK_JWKS_URL)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS from {KEYCLOAK_JWKS_URL}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

async def get_current_user(request: Request) -> UserToken:
    """Dependency to extract and validate JWT from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )
    
    # Get tenant ID from header
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required"
        )
    
    try:
        tenant_id = UUID(tenant_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format"
        )
    
    token = auth_header.split(" ", 1)[1]
    try:
        # Decode token without verification first to log claims for debugging
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            logger.debug(f"Token claims for debugging: {unverified_claims}")
        except Exception as e:
            logger.debug(f"Failed to decode unverified claims: {e}")

        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        
        key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
        if not key:
            logger.error(f"No matching key found for kid: {unverified_header.get('kid')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found"
            )
            
        # Convert JWK to PEM format
        public_key = jwk_to_public_key(key)
        
        # Use RSA256 by default if not specified
        alg = unverified_header.get("alg", ALGORITHMS.RS256)
        
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[alg],
            #audience=KEYCLOAK_AUDIENCE,
            audience="account",
            #issuer=KEYCLOAK_ISSUER,
            issuer="http://localhost:8080/realms/chatbot",
        )
        
        # Create initial UserToken with tenant_id from header
        user = UserToken(
            sub=payload.get("sub"),
            email=payload.get("email", ""),
            preferred_username=payload.get("preferred_username", ""),
            roles=payload.get("realm_access", {}).get("roles", []),
            tenant_id=tenant_id,  # Initial tenant_id from header
            given_name=payload.get("given_name", ""),
            family_name=payload.get("family_name", ""),
            payload=payload
        )
        
        # Sync user with database and get final tenant_id
        final_tenant_id = await sync_user_with_db(user)
        
        # Update user token with final tenant_id
        user.tenant_id = final_tenant_id
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTClaimsError as e:
        logger.error(f"JWT claims validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token claims: {str(e)}"
        )
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user_roles(user: UserToken = Depends(get_current_user)) -> List[str]:
    """Dependency to get current user's roles from the token."""
    return user.roles

async def sync_user_with_db(user_token: UserToken) -> UUID:
    """
    Synchronize the Keycloak user with our database.
    Creates the user if they don't exist, updates if they do.
    Also ensures tenant exists.
    
    Args:
        user_token: Validated user token from Keycloak with tenant_id from request header
        
    Returns:
        UUID: The final tenant_id (may be different from input if tenant was created)
    """
    try:
        # First ensure tenant exists
        tenant_service = TenantService()
        tenant_id = user_token.tenant_id
        
        try:
            await tenant_service.ensure_tenant_exists(tenant_id)
        except TenantMismatchError:
            # Tenant doesn't exist, create it
            tenant_id = await tenant_service.create_tenant()
            logger.info(f"Created new tenant: {tenant_id}")
            user_token.tenant_id = tenant_id  # Update token with new tenant ID

        # Now handle user operations within tenant context
        user_repo = UserRepository()
        async with TenantContextManager(tenant_id):
            # Check if user exists
            user = await user_repo.get_by_username(user_token.preferred_username)
            
            # Extract all available user info from token
            user_data = {
                "username": user_token.preferred_username,
                "email": user_token.email,
                "first_name": user_token.given_name,
                "last_name": user_token.family_name,
                "is_superuser": "admin" in user_token.roles
            }
            
            if not user:
                # Create new user with all available info
                user = await user_repo.create_user(**user_data)
                logger.info(f"Created new user from Keycloak: {user_token.preferred_username}")
                
                # Log user creation
                await log_security_event(
                    event_type="USER_CREATED_FROM_KEYCLOAK",
                    tenant_id=str(tenant_id),
                    user_id=str(user.id),
                    details={
                        "username": user_token.preferred_username,
                        "success": True
                    }
                )
            else:
                # Update all user fields that might have changed
                user = await user_repo.update_user_profile(
                    user_id=user.id,
                    **user_data
                )
                logger.debug(f"Updated user profile from Keycloak: {user_token.preferred_username}")
            
            # Update last login timestamp
            await user.update_last_login()
            
            # Return the final tenant_id
            return tenant_id
                
    except Exception as e:
        error_msg = f"Error syncing user with database: {str(e)}"
        logger.error(error_msg)
        
        # Log the error
        await log_security_event(
            event_type="USER_SYNC_ERROR",
            tenant_id=str(tenant_id),
            user_id=user_token.sub,
            details={
                "username": user_token.preferred_username,
                "success": False,
                "error": str(e)
            },
            severity="ERROR"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error synchronizing user data"
        )

# TODO: Add Keycloak admin API integration for user management if needed 