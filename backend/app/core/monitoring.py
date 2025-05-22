"""
Monitoring Module

This module handles logging, metrics collection, and monitoring for the chat application.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID
import structlog
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure structured logger
logger = structlog.get_logger()

async def log_chat_event(
    event_type: str,
    user_id: Optional[UUID] = None,
    tenant_id: Optional[UUID] = None,
    conversation_id: Optional[UUID] = None,
    message_id: Optional[UUID] = None,
    error_message: Optional[str] = None,
    error_type: Optional[str] = None,
    model_type: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    message_type: Optional[str] = None,  # For backward compatibility
    **additional_data: Dict[str, Any]
) -> None:
    """
    Log a chat-related event with structured data.
    
    Args:
        event_type: Type of event (e.g., message_processed, feedback_received)
        user_id: Optional ID of the user involved
        tenant_id: Optional tenant ID
        conversation_id: Optional conversation ID
        message_id: Optional message ID
        error_message: Optional error message
        error_type: Optional error type
        model_type: Optional AI model type used
        processing_time_ms: Optional processing time in milliseconds
        message_type: Optional message type (for backward compatibility)
        additional_data: Any additional data to log
    """
    event_data = {
        "event_type": event_type,
        "severity": "INFO" if not error_message else "ERROR",
        "timestamp": datetime.utcnow().isoformat(),
        **({"user_id": str(user_id)} if user_id else {}),
        **({"tenant_id": str(tenant_id)} if tenant_id else {}),
        **({"conversation_id": str(conversation_id)} if conversation_id else {}),
        **({"message_id": str(message_id)} if message_id else {}),
        **({"error_message": error_message} if error_message else {}),
        **({"error_type": error_type} if error_type else {}),
        **({"model_type": model_type} if model_type else {}),
        **({"processing_time_ms": processing_time_ms} if processing_time_ms else {}),
        **({"message_type": message_type} if message_type else {}),
        **additional_data
    }
    
    if error_message:
        logger.error("chat_event", **event_data)
    else:
        logger.info("chat_event", **event_data)

async def log_security_event(
    event_type: str,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "INFO",
    **kwargs: Any
) -> None:
    """
    Log security-related events with structured logging.
    
    Args:
        event_type: Type of security event (e.g., 'PII_DETECTED', 'AUTH_FAILURE')
        tenant_id: ID of the tenant associated with the event
        user_id: ID of the user associated with the event
        details: Additional event details
        severity: Event severity level (INFO, WARNING, ERROR)
        **kwargs: Additional keyword arguments to be included in the event data
    """
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "severity": severity,
        **(details or {}),
        **kwargs  # Include any additional kwargs in the event data
    }
    
    if severity == "ERROR":
        logger.error("security_event", **event_data)
    elif severity == "WARNING":
        logger.warning("security_event", **event_data)
    else:
        logger.info("security_event", **event_data)

async def log_api_event(
    endpoint: str,
    method: str,
    status_code: int,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    duration_ms: Optional[float] = None
) -> None:
    """
    Log API-related events with structured logging.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        status_code: Response status code
        tenant_id: ID of the tenant making the request
        user_id: ID of the user making the request
        duration_ms: Request duration in milliseconds
    """
    logger.info(
        "api_event",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        tenant_id=tenant_id,
        user_id=user_id,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat()
    )



# TODO: Add Prometheus metrics collection
# TODO: Add structured logging with ELK integration
# TODO: Add audit logging for security events 