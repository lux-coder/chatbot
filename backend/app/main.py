from fastapi import FastAPI
from starlette.middleware import Middleware
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.core.tenancy import TenantMiddleware
import logging
import sys
from pythonjsonlogger import jsonlogger

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

app = FastAPI(
    title="Secure Chatbot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Register tenant context middleware
app.add_middleware(TenantMiddleware)
# TODO: Add CORS, security, and other middleware here

app.include_router(chat_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")

@app.get("/", tags=["root"])
def root():
    return {"message": "Secure Chatbot API is running."} 