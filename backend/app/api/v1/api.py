from fastapi import APIRouter
from app.api.v1.endpoints import auth, chat
from app.api.v1 import bot

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    bot.router,
    prefix="/bot",
    tags=["bot"]
) 