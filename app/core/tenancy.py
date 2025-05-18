from contextvars import ContextVar
from uuid import UUID
from typing import Optional
from fastapi import HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Context variable to store the current tenant ID
tenant_context: ContextVar[UUID] = ContextVar('tenant_id')

def get_current_tenant() -> UUID:
    """Get the current tenant ID from context."""
    try:
        return tenant_context.get()
    except LookupError:
        raise HTTPException(
            status_code=500,
            detail="Tenant context not set"
        )

class TenantContextManager:
    """Context manager for handling tenant context."""
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.token = None

    async def __aenter__(self):
        self.token = tenant_context.set(self.tenant_id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        tenant_context.reset(self.token)

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from request."""
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id:
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID header is required"
            )
        
        try:
            tenant_uuid = UUID(tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid tenant ID format"
            )
        
        async with TenantContextManager(tenant_uuid):
            response = await call_next(request)
            return response

# Dependency for FastAPI routes
async def require_tenant(tenant_id: str = Depends(get_current_tenant)) -> UUID:
    """Dependency to ensure tenant context is set."""
    return tenant_id 