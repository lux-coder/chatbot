"""
Request Logging Middleware

This middleware provides comprehensive request/response logging and metrics
for observability and monitoring with Promtail + Loki + Grafana.

Features:
- Request/response logging
- Performance metrics
- Error tracking
- User/tenant context
- Security monitoring
"""

import time
import uuid
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException
import structlog
from app.core.logging_config import (
    log_request_context,
    log_api_metrics,
    log_security_alert,
    log_performance_metrics
)

logger = structlog.get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request/response logging and metrics.
    """
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            exclude_paths: List of paths to exclude from logging
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/api/v1/healthz"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add comprehensive logging.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            HTTP response
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Extract basic request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        client_ip = self._get_client_ip(request)
        user_agent = headers.get("user-agent", "unknown")
        
        # Extract user and tenant from headers if available
        user_id = None
        tenant_id = headers.get("x-tenant-id")
        
        # Skip logging for excluded paths
        if path in self.exclude_paths:
            response = await call_next(request)
            return response
        
        # Add request ID to request state for use in other parts of the app
        request.state.request_id = request_id
        
        response = None
        error = None
        
        try:
            # Use request context for all logs within this request
            with log_request_context(
                request_id=request_id,
                endpoint=path,
                method=method,
                user_id=user_id,
                tenant_id=tenant_id
            ):
                # Log request start
                logger.info(
                    "request_started",
                    method=method,
                    path=path,
                    query_params=query_params if query_params else None,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    content_length=headers.get("content-length"),
                    content_type=headers.get("content-type")
                )
                
                # Process the request
                response = await call_next(request)
                
                # Calculate processing time
                processing_time = (time.time() - start_time) * 1000
                
                # Extract response information
                status_code = response.status_code
                content_length = response.headers.get("content-length", 0)
                
                # Log successful request completion
                logger.info(
                    "request_completed",
                    status_code=status_code,
                    processing_time_ms=round(processing_time, 2),
                    response_size=content_length
                )
                
                # Log API metrics
                log_api_metrics(
                    endpoint=path,
                    method=method,
                    status_code=status_code,
                    duration_ms=processing_time,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    client_ip=client_ip,
                    user_agent=user_agent
                )
                
                # Log performance metrics for slow requests
                if processing_time > 1000:  # Requests taking more than 1 second
                    log_performance_metrics(
                        operation="slow_request",
                        duration_ms=processing_time,
                        success=status_code < 400,
                        endpoint=path,
                        method=method,
                        status_code=status_code
                    )
                
                # Check for potential security issues
                await self._check_security_alerts(
                    request, response, processing_time, user_id, tenant_id
                )
                
        except HTTPException as e:
            error = e
            status_code = e.status_code
            processing_time = (time.time() - start_time) * 1000
            
            logger.warning(
                "request_http_exception",
                status_code=status_code,
                detail=e.detail,
                processing_time_ms=round(processing_time, 2)
            )
            
            # Log API metrics for HTTP exceptions
            log_api_metrics(
                endpoint=path,
                method=method,
                status_code=status_code,
                duration_ms=processing_time,
                user_id=user_id,
                tenant_id=tenant_id,
                error_type="HTTPException",
                error_detail=e.detail
            )
            
            raise e
            
        except Exception as e:
            error = e
            status_code = 500
            processing_time = (time.time() - start_time) * 1000
            
            logger.error(
                "request_unhandled_exception",
                error=str(e),
                error_type=type(e).__name__,
                processing_time_ms=round(processing_time, 2)
            )
            
            # Log API metrics for unhandled exceptions
            log_api_metrics(
                endpoint=path,
                method=method,
                status_code=status_code,
                duration_ms=processing_time,
                user_id=user_id,
                tenant_id=tenant_id,
                error_type=type(e).__name__,
                error_detail=str(e)
            )
            
            # Log security alert for unexpected errors
            log_security_alert(
                alert_type="UNHANDLED_EXCEPTION",
                severity="HIGH",
                details={
                    "endpoint": path,
                    "method": method,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                user_id=user_id,
                tenant_id=tenant_id
            )
            
            raise e
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request headers.
        
        Args:
            request: The HTTP request
            
        Returns:
            Client IP address
        """
        # Check for forwarded headers (common in load balancer setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP if there are multiple
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_security_alerts(
        self,
        request: Request,
        response: Response,
        processing_time: float,
        user_id: Optional[str],
        tenant_id: Optional[str]
    ) -> None:
        """
        Check for potential security issues and log alerts.
        
        Args:
            request: The HTTP request
            response: The HTTP response
            processing_time: Request processing time in milliseconds
            user_id: Optional user identifier
            tenant_id: Optional tenant identifier
        """
        path = request.url.path
        method = request.method
        status_code = response.status_code
        client_ip = self._get_client_ip(request)
        
        # Check for authentication failures
        if status_code == 401:
            log_security_alert(
                alert_type="AUTHENTICATION_FAILURE",
                severity="MEDIUM",
                details={
                    "endpoint": path,
                    "method": method,
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("user-agent")
                },
                user_id=user_id,
                tenant_id=tenant_id
            )
        
        # Check for authorization failures
        elif status_code == 403:
            log_security_alert(
                alert_type="AUTHORIZATION_FAILURE",
                severity="MEDIUM",
                details={
                    "endpoint": path,
                    "method": method,
                    "client_ip": client_ip
                },
                user_id=user_id,
                tenant_id=tenant_id
            )
        
        # Check for potential brute force attacks (multiple 401s from same IP)
        elif status_code == 429:
            log_security_alert(
                alert_type="RATE_LIMIT_EXCEEDED",
                severity="HIGH",
                details={
                    "endpoint": path,
                    "method": method,
                    "client_ip": client_ip
                },
                user_id=user_id,
                tenant_id=tenant_id
            )
        
        # Check for suspicious request patterns
        if method in ["POST", "PUT", "PATCH", "DELETE"] and not user_id:
            log_security_alert(
                alert_type="UNAUTHENTICATED_WRITE_ATTEMPT",
                severity="MEDIUM",
                details={
                    "endpoint": path,
                    "method": method,
                    "client_ip": client_ip
                },
                user_id=user_id,
                tenant_id=tenant_id
            )
        
        # Check for unusually long processing times (potential DoS)
        if processing_time > 30000:  # 30 seconds
            log_security_alert(
                alert_type="SLOW_REQUEST_DETECTED",
                severity="MEDIUM",
                details={
                    "endpoint": path,
                    "method": method,
                    "processing_time_ms": processing_time,
                    "client_ip": client_ip
                },
                user_id=user_id,
                tenant_id=tenant_id
            ) 