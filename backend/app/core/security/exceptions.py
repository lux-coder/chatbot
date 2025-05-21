"""
Security Exceptions Module

This module defines custom exceptions used throughout the application for
security-related error handling.
"""

from fastapi import HTTPException, status
from ..monitoring import log_security_event

class SecurityException(HTTPException):
    """Base class for security-related exceptions."""
    
    def __init__(self, status_code: int, detail: str):
        """
        Initialize the exception.
        
        Args:
            status_code: HTTP status code
            detail: Detailed error message
        """
        super().__init__(status_code=status_code, detail=detail)
        # Log security event asynchronously
        # Note: We can't use await here since __init__ can't be async
        log_security_event(
            event_type="security_exception",
            error_type=self.__class__.__name__,
            error_message=detail,
            status_code=status_code
        )

class TenantMismatchError(SecurityException):
    """
    Raised when a resource is accessed by a user from a different tenant.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class AIServiceError(SecurityException):
    """
    Raised when there is an error communicating with the AI service.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )

class ValidationError(SecurityException):
    """
    Raised when input validation fails.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

class ResourceNotFoundError(SecurityException):
    """
    Raised when a requested resource is not found.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class AuthenticationError(SecurityException):
    """
    Raised when authentication fails.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class AuthorizationError(SecurityException):
    """
    Raised when a user is not authorized to perform an action.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class RateLimitError(SecurityException):
    """
    Raised when rate limits are exceeded.
    """
    
    def __init__(self, detail: str):
        """
        Initialize the exception.
        
        Args:
            detail: Detailed error message
        """
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        ) 