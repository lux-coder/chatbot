"""
Exceptions Module

This module defines custom exceptions used throughout the application.
"""

from fastapi import HTTPException, status

class TenantMismatchError(HTTPException):
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

class AIServiceError(HTTPException):
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

class ValidationError(HTTPException):
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

class ResourceNotFoundError(HTTPException):
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

class AuthenticationError(HTTPException):
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

class AuthorizationError(HTTPException):
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

class RateLimitError(HTTPException):
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