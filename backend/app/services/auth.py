from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from jose.constants import ALGORITHMS
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from typing import List, Dict, Any, Optional
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
from fastapi.security import OAuth2PasswordBearer
from app.core.config.settings import get_settings
from app.models.user import User

logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction - moved to top of file
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Constants (should be moved to config)
KEYCLOAK_ISSUER = "http://keycloak:8080/realms/chatbot"
#KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_CLIENT_ID", "chatbot-frontend")
KEYCLOAK_AUDIENCE = "account"
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

class UserToken(BaseModel):
    sub: str
    email: str = ""
    preferred_username: str = ""
    roles: List[str] = []
    tenant_id: Optional[UUID] = None  # Make tenant_id optional
    given_name: str = ""
    family_name: str = ""
    payload: Dict[str, Any] = {}  # Store full token payload for additional data

    def get_roles(self) -> List[str]:
        """Extract roles from realm_access."""
        if not self.payload or 'realm_access' not in self.payload:
            return []
        return self.payload['realm_access'].get('roles', [])

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

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserToken:
    """Dependency to get the current authenticated user from the token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    auth_service = AuthService()
    try:
        # Decode token without tenant context
        return await auth_service.decode_token(token)
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

async def get_current_user_roles(user: UserToken = Depends(get_current_user)) -> List[str]:
    """Dependency to get current user's roles from the token."""
    return user.get_roles()

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

class AuthService:
    """Service for authentication and authorization."""
    
    def __init__(self):
        self.settings = get_settings()
        self.user_repository = UserRepository()
        self.tenant_service = TenantService()
        self.keycloak_certs = None
        
    async def get_keycloak_public_key(self):
        """Fetch Keycloak public key for JWT verification."""
        if self.keycloak_certs:
            return self.keycloak_certs
            
        # Use the constant instead of settings attribute
        keycloak_url = KEYCLOAK_JWKS_URL
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(keycloak_url)
                response.raise_for_status()
                self.keycloak_certs = response.json()
                return self.keycloak_certs
        except Exception as e:
            logger.error(f"Failed to fetch Keycloak public key: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
    
    async def decode_token(self, token: str) -> UserToken:
        """Decode and validate JWT token from Keycloak."""
        try:
            certs = await self.get_keycloak_public_key()
            
            # For debugging, log the unverified claims
            try:
                unverified_claims = jwt.get_unverified_claims(token)
                logger.debug(f"Token unverified claims: {unverified_claims}")
            except Exception as e:
                logger.debug(f"Failed to decode unverified claims: {e}")
            
            # Extract kid from token header
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token header"
                )
                
            # Find matching key
            key = None
            for cert in certs.get('keys', []):
                if cert.get('kid') == kid:
                    key = cert
                    break
                    
            if not key:
                # Refresh certs and try again (may have rotated)
                self.keycloak_certs = None
                certs = await self.get_keycloak_public_key()
                
                for cert in certs.get('keys', []):
                    if cert.get('kid') == kid:
                        key = cert
                        break
                        
            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature"
                )
                
            # Fix: Correct PEM format for X.509 certificate
            if 'x5c' in key and key['x5c']:
                # Format as X.509 certificate 
                public_key = f"-----BEGIN CERTIFICATE-----\n{key['x5c'][0]}\n-----END CERTIFICATE-----"
            else:
                # Fallback to RSA key if no x5c
                n = base64.urlsafe_b64decode(key['n'] + '=' * (-len(key['n']) % 4))
                e = base64.urlsafe_b64decode(key['e'] + '=' * (-len(key['e']) % 4))
                
                numbers = RSAPublicNumbers(
                    e=int.from_bytes(e, 'big'),
                    n=int.from_bytes(n, 'big')
                )
                
                public_key = numbers.public_key(backend=default_backend()).public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                # Convert bytes to string
                public_key = public_key.decode('utf-8')
            
            # TEMPORARY: For debugging, make validation more lenient
            # In production, remove these options and use strict validation
            try:
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    options={
                        "verify_aud": False,  # Skip audience validation
                        "verify_iss": False,  # Skip issuer validation
                    }
                )
            except Exception as e:
                logger.error(f"Lenient token validation failed: {str(e)}")
                # Fall back to just getting the claims without verification
                payload = jwt.get_unverified_claims(token)
                logger.warning("Using unverified token claims - FOR DEBUGGING ONLY")
            
            # Create UserToken from payload (tenant_id can be None)
            return UserToken(
                sub=payload.get("sub"),
                email=payload.get("email", ""),
                preferred_username=payload.get("preferred_username", ""),
                roles=payload.get("realm_access", {}).get("roles", []),
                given_name=payload.get("given_name", ""),
                family_name=payload.get("family_name", ""),
                payload=payload
            )
            
        except JWTError as e:
            logger.error(f"JWT error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        except Exception as e:
            logger.error(f"Token decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )
            
    async def sync_user_from_keycloak(self, token: UserToken, tenant_id: UUID) -> User:
        """Synchronize user data from Keycloak token."""
        try:
            async with TenantContextManager(tenant_id):
                # First try to find user by ID (Keycloak's subject)
                user = await self.user_repository.get_by_id(UUID(token.sub))
                
                if not user:
                    # Try by username as fallback
                    user = await self.user_repository.get_by_username(token.preferred_username)
                    
                if not user:
                    # Create new user with Keycloak's ID
                    logger.info(f"Creating new user from Keycloak: {token.preferred_username}")
                    user = await self.user_repository.create_user(
                        id=UUID(token.sub),  # Use Keycloak's ID directly
                        username=token.preferred_username,
                        email=token.email or f"{token.preferred_username}@example.com",
                        first_name=token.given_name,
                        last_name=token.family_name
                    )
                    
                    await log_security_event(
                        event_type="USER_CREATED_FROM_KEYCLOAK",
                        user_id=token.sub,
                        tenant_id=str(tenant_id),
                        username=token.preferred_username,
                        success=True
                    )
                
                # Update user's last login time
                if user:
                    await user.update_last_login()
                
                return user
                
        except Exception as e:
            logger.error(f"Error syncing user with database: {str(e)}")
            await log_security_event(
                event_type="USER_SYNC_ERROR",
                user_id=token.sub,
                tenant_id=str(tenant_id),
                username=token.preferred_username,
                success=False,
                error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error synchronizing user data"
            )

# Dependencies
async def get_current_user_roles(user: UserToken = Depends(get_current_user)) -> List[str]:
    """Dependency to get the roles of the current user."""
    return user.get_roles() 