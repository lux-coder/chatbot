"""Security package.

This package provides security-related functionality including:
- PII detection and masking
- Tenant isolation
- Custom exceptions
"""

from .pii import PIIHandler, PIIDetector, DataMasker, PIIPattern
from .tenancy import (
    get_current_tenant,
    TenantContextManager,
    TenantMiddleware,
    require_tenant,
    tenant_context
)
from .exceptions import (
    TenantMismatchError,
    AIServiceError,
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError
)

__all__ = [
    # PII handling
    'PIIHandler',
    'PIIDetector',
    'DataMasker',
    'PIIPattern',
    
    # Tenant isolation
    'get_current_tenant',
    'TenantContextManager',
    'TenantMiddleware',
    'require_tenant',
    'tenant_context',
    
    # Exceptions
    'TenantMismatchError',
    'AIServiceError',
    'ValidationError',
    'ResourceNotFoundError',
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError'
] 