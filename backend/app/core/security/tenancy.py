"""
Tenant Isolation Module

This module provides tenant context management and isolation for multi-tenant applications.
"""

from contextvars import ContextVar
from uuid import UUID
from typing import Optional
from fastapi import HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import json
from ..monitoring import log_security_event

logger = logging.getLogger(__name__)

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
        await log_security_event(
            event_type="tenant_context_set",
            tenant_id=self.tenant_id
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        tenant_context.reset(self.token)
        if exc_type:
            await log_security_event(
                event_type="tenant_context_error",
                tenant_id=self.tenant_id,
                error_type=str(exc_type.__name__),
                error_message=str(exc_val)
            )

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from request."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details in a structured way
        request_headers = dict(request.headers)
        # Remove sensitive information from headers before logging
        if 'authorization' in request_headers:
            request_headers['authorization'] = '[REDACTED]'

        logger.info("Processing request",
                   extra={
                       'request_path': str(request.url.path),
                       'request_method': request.method,
                       'headers': request_headers,
                       'client_host': request.client.host if request.client else None
                   })

        # Bypass tenant enforcement for public endpoints
        public_paths = ["/api/v1/healthz", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths:
            logger.debug("Bypassing tenant check for public path", 
                        extra={'path': request.url.path})
            return await call_next(request)

        tenant_id = request.headers.get("X-Tenant-ID")

        if not tenant_id:
            logger.warning("Missing tenant ID in request",
                         extra={'path': request.url.path})
            raise HTTPException(
                status_code=400,
                detail="X-Tenant-ID header is required"
            )

        try:
            tenant_uuid = UUID(tenant_id)
            await log_security_event(
                event_type="tenant_request",
                tenant_id=tenant_uuid,
                path=str(request.url.path),
                method=request.method
            )
        except ValueError:
            logger.error("Invalid tenant ID format",
                        extra={'tenant_id': tenant_id})
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