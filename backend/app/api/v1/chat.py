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
from app.services.auth import get_current_user, get_current_user_roles, UserToken, AuthService
from app.core.security.tenancy import require_tenant
from app.services.chat import ChatService
from app.api.deps import get_chat_service
from app.core.security.exceptions import TenantMismatchError, AIServiceError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: ChatMessageRequest,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Submit a user message and receive an AI response.
    """
    try:
        # Create AuthService to ensure user exists in database
        auth_service = AuthService()
        db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to synchronize user data"
            )
        
        # Process message with the synchronized user ID
        response = await chat_service.process_message(
            user_id=UUID(user.sub),  # Use Keycloak ID directly
            tenant_id=tenant_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatMessageResponse(**response)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TenantMismatchError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {str(e)}"
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        logger.error(
            f"Unhandled error in send_message: {str(type(e).__name__)}, Message: {str(e)}\nTraceback:\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    conversation_id: UUID,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    roles: List[str] = Depends(get_current_user_roles),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Retrieve chat history for the authenticated user/tenant.
    """
    try:
        # Create AuthService to ensure user exists in database
        auth_service = AuthService()
        db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to synchronize user data"
            )
            
        history = await chat_service.get_chat_history(
            user_id=UUID(user.sub),  # Use Keycloak ID directly
            tenant_id=tenant_id,
            conversation_id=conversation_id
        )
        return ChatHistoryResponse(**history)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    roles: List[str] = Depends(get_current_user_roles),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Submit feedback on an AI response.
    """
    try:
        # Create AuthService to ensure user exists in database
        auth_service = AuthService()
        db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to synchronize user data"
            )
            
        feedback = await chat_service.store_feedback(
            message_id=request.message_id,
            user_id=UUID(user.sub),  # Use Keycloak ID directly
            rating=request.rating,
            comment=request.comment
        )
        return FeedbackResponse(**feedback)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store feedback"
        ) 