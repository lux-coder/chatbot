"""
Monitoring Module

This module handles logging, metrics collection, and monitoring for the chat application.
Enhanced for Promtail + Loki + Grafana observability stack.
"""

import logging
from typing import Any, Dict, Optional, Union
from uuid import UUID
import structlog
from datetime import datetime
import time
from enum import Enum
from contextlib import contextmanager

# Configure logger for this module
logger = structlog.get_logger(__name__)

class EventSeverity(str, Enum):
    """Event severity levels for consistent logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class EventType(str, Enum):
    """Common event types for better categorization."""
    # Chat events
    MESSAGE_PROCESSED = "message_processed"
    MESSAGE_BLOCKED = "message_blocked"
    MESSAGE_SANITIZED = "message_sanitized"
    FEEDBACK_RECEIVED = "feedback_received"
    
    # Security events
    PII_DETECTED = "pii_detected"
    SECURITY_VIOLATION = "security_violation"
    AUTH_FAILURE = "auth_failure"
    PROMPT_BLOCKED_REGEX = "prompt_blocked_regex"
    PROMPT_BLOCKED_MODERATION = "prompt_blocked_moderation"
    
    # System events
    DATABASE_ERROR = "database_error"
    API_ERROR = "api_error"
    PERFORMANCE_ALERT = "performance_alert"
    
    # Business events
    USER_REGISTERED = "user_registered"
    CONVERSATION_STARTED = "conversation_started"
    BOT_INSTANCE_CREATED = "bot_instance_created"

async def log_chat_event(
    event_type: str,
    user_id: Optional[Union[UUID, str]] = None,
    tenant_id: Optional[Union[UUID, str]] = None,
    conversation_id: Optional[Union[UUID, str]] = None,
    message_id: Optional[Union[UUID, str]] = None,
    chatbot_instance_id: Optional[Union[UUID, str]] = None,
    error_message: Optional[str] = None,
    error_type: Optional[str] = None,
    model_type: Optional[str] = None,
    processing_time_ms: Optional[float] = None,
    message_type: Optional[str] = None,  # For backward compatibility
    severity: str = "INFO",
    **additional_data: Any
) -> None:
    """
    Log a chat-related event with structured data.
    
    Args:
        event_type: Type of event (e.g., message_processed, feedback_received)
        user_id: Optional ID of the user involved
        tenant_id: Optional tenant ID
        conversation_id: Optional conversation ID
        message_id: Optional message ID
        chatbot_instance_id: Optional chatbot instance ID
        error_message: Optional error message
        error_type: Optional error type
        model_type: Optional AI model type used
        processing_time_ms: Optional processing time in milliseconds
        message_type: Optional message type (for backward compatibility)
        severity: Event severity level
        additional_data: Any additional data to log
    """
    event_data = {
        "event_category": "chat",
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    # Add IDs if provided
    if user_id:
        event_data["user_id"] = str(user_id)
    if tenant_id:
        event_data["tenant_id"] = str(tenant_id)
    if conversation_id:
        event_data["conversation_id"] = str(conversation_id)
    if message_id:
        event_data["message_id"] = str(message_id)
    if chatbot_instance_id:
        event_data["chatbot_instance_id"] = str(chatbot_instance_id)
    
    # Add optional fields
    if error_message:
        event_data["error_message"] = error_message
    if error_type:
        event_data["error_type"] = error_type
    if model_type:
        event_data["model_type"] = model_type
    if processing_time_ms is not None:
        event_data["processing_time_ms"] = round(processing_time_ms, 2)
    if message_type:
        event_data["message_type"] = message_type
    
    # Add additional data
    event_data.update(additional_data)
    
    # Log based on severity
    if severity == "ERROR":
        logger.error("chat_event", **event_data)
    elif severity == "WARNING":
        logger.warning("chat_event", **event_data)
    elif severity == "CRITICAL":
        logger.critical("chat_event", **event_data)
    else:
        logger.info("chat_event", **event_data)

async def log_security_event(
    event_type: str,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    severity: str = "INFO",
    alert_level: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Log security-related events with structured logging.
    
    Args:
        event_type: Type of security event (e.g., 'PII_DETECTED', 'AUTH_FAILURE')
        tenant_id: ID of the tenant associated with the event
        user_id: ID of the user associated with the event
        details: Additional event details
        severity: Event severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        alert_level: Security alert level (LOW, MEDIUM, HIGH, CRITICAL)
        **kwargs: Additional keyword arguments to be included in the event data
    """
    event_data = {
        "event_category": "security",
        "event_type": event_type,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tenant_id": tenant_id,
        "user_id": user_id,
        **(details or {}),
        **kwargs  # Include any additional kwargs in the event data
    }
    
    if alert_level:
        event_data["alert_level"] = alert_level
    
    # Log based on severity
    if severity == "ERROR":
        logger.error("security_event", **event_data)
    elif severity == "WARNING":
        logger.warning("security_event", **event_data)
    elif severity == "CRITICAL":
        logger.critical("security_event", **event_data)
    else:
        logger.info("security_event", **event_data)

async def log_api_event(
    endpoint: str,
    method: str,
    status_code: int,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
    duration_ms: Optional[float] = None,
    request_id: Optional[str] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    **kwargs: Any
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
        request_id: Unique request identifier
        client_ip: Client IP address
        user_agent: User agent string
        **kwargs: Additional data to log
    """
    event_data = {
        "event_category": "api",
        "event_type": "api_request",
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **kwargs
    }
    
    if duration_ms is not None:
        event_data["duration_ms"] = round(duration_ms, 2)
    if request_id:
        event_data["request_id"] = request_id
    if client_ip:
        event_data["client_ip"] = client_ip
    if user_agent:
        event_data["user_agent"] = user_agent
    
    # Determine severity based on status code
    if status_code >= 500:
        logger.error("api_event", **event_data)
    elif status_code >= 400:
        logger.warning("api_event", **event_data)
    else:
        logger.info("api_event", **event_data)

async def log_performance_event(
    operation: str,
    duration_ms: float,
    success: bool = True,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    **metadata: Any
) -> None:
    """
    Log performance-related events for monitoring and alerting.
    
    Args:
        operation: Name of the operation being measured
        duration_ms: Duration in milliseconds
        success: Whether the operation was successful
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
        **metadata: Additional metadata about the operation
    """
    event_data = {
        "event_category": "performance",
        "event_type": "operation_completed",
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "success": success,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **metadata
    }
    
    # Log as warning if operation is slow or failed
    if not success or duration_ms > 5000:  # 5 seconds threshold
        logger.warning("performance_event", **event_data)
    else:
        logger.info("performance_event", **event_data)

async def log_business_event(
    event_type: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    **details: Any
) -> None:
    """
    Log business events for analytics and monitoring.
    
    Args:
        event_type: Type of business event
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
        **details: Additional event details
    """
    event_data = {
        "event_category": "business",
        "event_type": event_type,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **details
    }
    
    logger.info("business_event", **event_data)

@contextmanager
def log_operation_time(
    operation: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    **metadata: Any
):
    """
    Context manager to automatically log operation duration.
    
    Args:
        operation: Name of the operation being timed
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
        **metadata: Additional metadata about the operation
    """
    start_time = time.time()
    success = True
    error = None
    
    try:
        yield
    except Exception as e:
        success = False
        error = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        
        # Create a task to log the performance event
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                log_performance_event(
                    operation=operation,
                    duration_ms=duration_ms,
                    success=success,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    error=error,
                    **metadata
                )
            )
        except RuntimeError:
            # No event loop running, log synchronously
            event_data = {
                "event_category": "performance",
                "event_type": "operation_completed",
                "operation": operation,
                "duration_ms": round(duration_ms, 2),
                "success": success,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **metadata
            }
            if error:
                event_data["error"] = error
            
            if not success or duration_ms > 5000:
                logger.warning("performance_event", **event_data)
            else:
                logger.info("performance_event", **event_data)

def log_metric(
    metric_name: str,
    value: Union[int, float],
    labels: Optional[Dict[str, str]] = None,
    **metadata: Any
) -> None:
    """
    Log custom metrics for Grafana dashboards.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        labels: Optional labels for the metric
        **metadata: Additional metadata
    """
    event_data = {
        "event_category": "metric",
        "event_type": "custom_metric",
        "metric_name": metric_name,
        "metric_value": value,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "labels": labels or {},
        **metadata
    }
    
    logger.info("metric_event", **event_data)

# Prometheus metrics helpers (if you want to add Prometheus support later)
def increment_counter(metric_name: str, labels: Optional[Dict[str, str]] = None) -> None:
    """Increment a counter metric."""
    log_metric(metric_name, 1, labels, metric_type="counter")

def set_gauge(metric_name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None) -> None:
    """Set a gauge metric value."""
    log_metric(metric_name, value, labels, metric_type="gauge")

def observe_histogram(metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
    """Observe a histogram metric."""
    log_metric(metric_name, value, labels, metric_type="histogram")

# Initialize monitoring
logger.info(
    "monitoring_module_initialized",
    event_category="system",
    event_type="module_init",
    module="monitoring",
    timestamp=datetime.utcnow().isoformat() + "Z"
) 