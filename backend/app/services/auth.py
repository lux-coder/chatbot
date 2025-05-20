from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
import os

# Constants (should be moved to config)
KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", "http://keycloak:8080/realms/master")
KEYCLOAK_AUDIENCE = os.getenv("KEYCLOAK_CLIENT_ID", "chatbot-frontend")
KEYCLOAK_JWKS_URL = f"{KEYCLOAK_ISSUER}/protocol/openid-connect/certs"

class UserToken(BaseModel):
    sub: str
    email: str = ""
    preferred_username: str = ""
    roles: List[str] = []
    tenant_id: str = ""

async def get_jwks() -> Dict[str, Any]:
    """Fetch JWKS from Keycloak."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(KEYCLOAK_JWKS_URL)
        resp.raise_for_status()
        return resp.json()

async def get_current_user(request: Request) -> UserToken:
    """Dependency to extract and validate JWT from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        key = next((k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None)
        if not key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: key not found")
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[unverified_header["alg"]],
            audience=KEYCLOAK_AUDIENCE,
            issuer=KEYCLOAK_ISSUER,
        )
        user = UserToken(
            sub=payload.get("sub"),
            email=payload.get("email", ""),
            preferred_username=payload.get("preferred_username", ""),
            roles=payload.get("realm_access", {}).get("roles", []),
            tenant_id=payload.get("tenant_id", "")
        )
        return user
    except (JWTError, Exception) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")

async def get_current_user_roles(user: UserToken = Depends(get_current_user)) -> List[str]:
    """Dependency to get current user's roles from the token."""
    return user.roles

# TODO: Add Keycloak admin API integration for user management if needed 