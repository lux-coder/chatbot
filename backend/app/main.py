from fastapi import FastAPI
from starlette.middleware import Middleware
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.core.security.tenancy import TenantMiddleware
from app.core.database import initialize_database, close_database_connection
import logging
import sys
from pythonjsonlogger import jsonlogger
from contextlib import asynccontextmanager
from app.api.v1 import chat, tenant  # Add tenant import

# Enhanced logging configuration
logger = logging.getLogger()
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
    json_ensure_ascii=False
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Remove any existing handlers to avoid duplicates
for handler in logger.handlers[:-1]:
    logger.removeHandler(handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Initializing database...")
    await initialize_database()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Closing database connections...")
    await close_database_connection()
    logger.info("Database connections closed")

app = FastAPI(
    title="Secure Chatbot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Register tenant context middleware
app.add_middleware(TenantMiddleware)
# TODO: Add CORS, security, and other middleware here

app.include_router(chat_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(tenant.router, prefix="/api/v1")  # Add tenant router

@app.get("/", tags=["root"])
def root():
    return {"message": "Secure Chatbot API is running."} 