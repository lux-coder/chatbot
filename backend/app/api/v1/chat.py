from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from app.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from app.services.auth import get_current_user, get_current_user_roles, UserToken
from app.core.tenancy import require_tenant

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: ChatMessageRequest,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    roles: List[str] = Depends(get_current_user_roles),
):
    """
    Submit a user message and receive an AI response.
    """
    # TODO: Implement chat logic, model selection, DB storage, audit logging
    # Example RBAC check:
    # if "user" not in roles:
    #     raise HTTPException(status_code=403, detail="Insufficient permissions")
    raise NotImplementedError

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    conversation_id: UUID,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    roles: List[str] = Depends(get_current_user_roles),
):
    """
    Retrieve chat history for the authenticated user/tenant.
    """
    # TODO: Implement chat history retrieval
    raise NotImplementedError

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    roles: List[str] = Depends(get_current_user_roles),
):
    """
    Submit feedback on an AI response.
    """
    # TODO: Implement feedback storage and validation
    raise NotImplementedError 