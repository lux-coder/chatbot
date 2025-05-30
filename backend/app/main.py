from fastapi import FastAPI
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.core.security.tenancy import TenantMiddleware
from app.core.middleware import RequestLoggingMiddleware
from app.core.database import initialize_database, close_database_connection
from app.core.logging_config import init_logging, log_info, log_error
import logging
import sys
import os
from contextlib import asynccontextmanager
from app.api.v1 import chat, tenant, bot
import structlog

# Initialize comprehensive logging
init_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events with comprehensive logging"""
    # Startup
    log_info(
        "application_startup_initiated",
        app_name="Secure Chatbot API",
        version="1.0.0",
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    try:
        await initialize_database()
        log_info(
            "database_initialized_successfully",
            database_type="postgresql",
            orm="tortoise"
        )
    except Exception as e:
        log_error(
            "database_initialization_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
    
    log_info("application_startup_completed")
    
    yield
    
    # Shutdown
    log_info("application_shutdown_initiated")
    
    try:
        await close_database_connection()
        log_info("database_connections_closed")
    except Exception as e:
        log_error(
            "database_shutdown_error",
            error=str(e),
            error_type=type(e).__name__
        )
    
    log_info("application_shutdown_completed")

app = FastAPI(
    title="Secure Chatbot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add request logging middleware first (innermost)
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/docs", "/openapi.json", "/redoc", "/favicon.ico", "/api/v1/healthz"]
)

# Register tenant context middleware
app.add_middleware(TenantMiddleware)

# Allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(tenant.router, prefix="/api/v1")
app.include_router(bot.router, prefix="/api/v1")

@app.get("/", tags=["root"])
def root():
    """Root endpoint with logging."""
    log_info(
        "root_endpoint_accessed",
        endpoint="/",
        method="GET"
    )
    return {"message": "Secure Chatbot API is running."}

# Log application configuration on startup
log_info(
    "application_configured",
    middleware_count=len(app.user_middleware),
    routes_count=len(app.routes),
    cors_enabled=True,
    tenant_middleware_enabled=True,
    request_logging_enabled=True
) 