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
    tenant_id: str = ""

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
        
        user = UserToken(
            sub=payload.get("sub"),
            email=payload.get("email", ""),
            preferred_username=payload.get("preferred_username", ""),
            roles=payload.get("realm_access", {}).get("roles", []),
            tenant_id=payload.get("tenant_id", "")
        )
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

# TODO: Add Keycloak admin API integration for user management if needed 