"""
Logging Configuration Module

This module provides comprehensive logging configuration for the chatbot backend,
optimized for Promtail + Loki + Grafana observability stack.

Features:
- Structured JSON logging
- Request/response tracking
- Performance metrics
- Security event logging
- Consistent labeling for Loki
- Error tracking and alerting
"""

import logging
import logging.config
import structlog
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json
from contextlib import contextmanager

# Global logger instance
logger = structlog.get_logger(__name__)

class LokiJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter optimized for Loki ingestion.
    
    Provides consistent field naming and structure for Loki labels.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with Loki-friendly structure."""
        
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                'filename', 'module', 'lineno', 'funcName', 'created', 
                'msecs', 'relativeCreated', 'thread', 'threadName', 
                'processName', 'process', 'exc_info', 'exc_text', 'stack_info'
            }:
                log_entry[key] = value
        
        # Ensure all values are JSON serializable
        try:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            # Fallback to simple message if JSON serialization fails
            fallback = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "ERROR",
                "logger": "logging_config",
                "message": f"Failed to serialize log entry: {str(e)}",
                "original_message": str(record.getMessage())
            }
            return json.dumps(fallback)

class RequestContextProcessor:
    """
    Processor to add request context to all log entries.
    """
    
    def __init__(self):
        self.request_id = None
        self.user_id = None
        self.tenant_id = None
        self.endpoint = None
    
    def __call__(self, logger, method_name, event_dict):
        """Add request context to event dictionary."""
        
        # Add context if available
        if hasattr(self, 'request_id') and self.request_id:
            event_dict['request_id'] = self.request_id
        if hasattr(self, 'user_id') and self.user_id:
            event_dict['user_id'] = self.user_id
        if hasattr(self, 'tenant_id') and self.tenant_id:
            event_dict['tenant_id'] = self.tenant_id
        if hasattr(self, 'endpoint') and self.endpoint:
            event_dict['endpoint'] = self.endpoint
            
        return event_dict

# Global request context processor instance
request_context = RequestContextProcessor()

def configure_structlog():
    """Configure structlog for consistent structured logging."""
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            request_context,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )

def setup_logging(
    log_level: str = "INFO",
    service_name: str = "chatbot-backend",
    environment: str = "development"
) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Name of the service for labeling
        environment: Environment name (development, staging, production)
    """
    
    # Configure structlog first
    configure_structlog()
    
    # Logging configuration dictionary
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "loki_json": {
                "()": LokiJSONFormatter,
            },
            "console": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "loki_json",
                "stream": sys.stdout,
                "level": log_level
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "loki_json",
                "filename": "/app/logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": log_level
            }
        },
        "loggers": {
            # Application loggers
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "app.services": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "app.api": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            "app.core": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False
            },
            
            # Third-party loggers (less verbose)
            "httpx": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "tortoise": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        },
        "root": {
            "handlers": ["console"],
            "level": log_level
        }
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs("/app/logs", exist_ok=True)
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Set service-wide context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        service=service_name,
        environment=environment,
        version=os.getenv("APP_VERSION", "unknown")
    )
    
    logger.info(
        "logging_configured",
        log_level=log_level,
        service_name=service_name,
        environment=environment,
        handlers=["console", "file"]
    )

@contextmanager
def log_request_context(
    request_id: str,
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
):
    """
    Context manager for adding request context to all logs within the scope.
    
    Args:
        request_id: Unique request identifier
        endpoint: API endpoint being called
        method: HTTP method
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
    """
    
    # Store old context
    old_request_id = getattr(request_context, 'request_id', None)
    old_user_id = getattr(request_context, 'user_id', None)
    old_tenant_id = getattr(request_context, 'tenant_id', None)
    old_endpoint = getattr(request_context, 'endpoint', None)
    
    try:
        # Set new context
        request_context.request_id = request_id
        request_context.user_id = user_id
        request_context.tenant_id = tenant_id
        request_context.endpoint = f"{method} {endpoint}"
        
        # Bind context variables
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            tenant_id=tenant_id
        )
        
        yield
        
    finally:
        # Restore old context
        request_context.request_id = old_request_id
        request_context.user_id = old_user_id
        request_context.tenant_id = old_tenant_id
        request_context.endpoint = old_endpoint
        
        # Clear context variables
        structlog.contextvars.clear_contextvars()

def log_performance_metrics(
    operation: str,
    duration_ms: float,
    success: bool = True,
    **kwargs
) -> None:
    """
    Log performance metrics for operations.
    
    Args:
        operation: Name of the operation being measured
        duration_ms: Duration in milliseconds
        success: Whether the operation was successful
        **kwargs: Additional metadata
    """
    
    logger.info(
        "performance_metric",
        operation=operation,
        duration_ms=round(duration_ms, 2),
        success=success,
        **kwargs
    )

def log_security_alert(
    alert_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> None:
    """
    Log security alerts for monitoring and alerting.
    
    Args:
        alert_type: Type of security alert
        severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
        details: Alert details
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
    """
    
    logger.warning(
        "security_alert",
        alert_type=alert_type,
        severity=severity,
        user_id=user_id,
        tenant_id=tenant_id,
        **details
    )

def log_business_event(
    event_type: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> None:
    """
    Log business events for analytics and monitoring.
    
    Args:
        event_type: Type of business event
        details: Event details
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
    """
    
    logger.info(
        "business_event",
        event_type=event_type,
        user_id=user_id,
        tenant_id=tenant_id,
        **details
    )

def log_api_metrics(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log API metrics for monitoring and alerting.
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user identifier
        tenant_id: Optional tenant identifier
        **kwargs: Additional metadata
    """
    
    logger.info(
        "api_metric",
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        duration_ms=round(duration_ms, 2),
        user_id=user_id,
        tenant_id=tenant_id,
        **kwargs
    )

# Convenience functions for common log levels
def log_error(message: str, **kwargs) -> None:
    """Log error message with context."""
    logger.error(message, **kwargs)

def log_warning(message: str, **kwargs) -> None:
    """Log warning message with context."""
    logger.warning(message, **kwargs)

def log_info(message: str, **kwargs) -> None:
    """Log info message with context."""
    logger.info(message, **kwargs)

def log_debug(message: str, **kwargs) -> None:
    """Log debug message with context."""
    logger.debug(message, **kwargs)

# Initialize logging configuration when module is imported
def init_logging():
    """Initialize logging with default configuration."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    service_name = os.getenv("SERVICE_NAME", "chatbot-backend")
    environment = os.getenv("ENVIRONMENT", "development")
    
    setup_logging(
        log_level=log_level,
        service_name=service_name,
        environment=environment
    ) 