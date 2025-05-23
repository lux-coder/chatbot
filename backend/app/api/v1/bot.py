from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.bot import (
    ChatbotInstanceCreate,
    ChatbotInstanceResponse,
)
from app.schemas.chat import BotConversationsListResponse, BotConversationResponse
from app.services.auth import get_current_user, UserToken, AuthService
from app.core.security.tenancy import require_tenant
from app.services.bot import ChatbotInstanceService
from app.api.deps import get_bot_service

router = APIRouter(prefix="/bot", tags=["bot"])


@router.post("/", response_model=ChatbotInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_chatbot_instance(
    request: ChatbotInstanceCreate,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    # Create AuthService to ensure user exists in database
    auth_service = AuthService()
    db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize user data"
        )
    
    instance = await service.create_instance(
        user_id=UUID(user.sub),
        tenant_id=tenant_id,
        name=request.name,
        style=request.style,
        language=request.language,
        icon=request.icon,
    )
    return ChatbotInstanceResponse.model_validate(instance)


@router.get("/", response_model=List[ChatbotInstanceResponse])
async def list_chatbot_instances(
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    # Create AuthService to ensure user exists in database
    auth_service = AuthService()
    db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize user data"
        )
        
    instances = await service.list_instances(user_id=UUID(user.sub), tenant_id=tenant_id)
    return [ChatbotInstanceResponse.model_validate(i) for i in instances]


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chatbot_instance(
    instance_id: UUID,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    # Create AuthService to ensure user exists in database
    auth_service = AuthService()
    db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize user data"
        )
        
    deleted = await service.delete_instance(instance_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return None


@router.post("/{instance_id}/publish", response_model=ChatbotInstanceResponse)
async def publish_chatbot_instance(
    instance_id: UUID,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    # Create AuthService to ensure user exists in database
    auth_service = AuthService()
    db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize user data"
        )
        
    instance = await service.publish_instance(instance_id, tenant_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return ChatbotInstanceResponse.model_validate(instance)


@router.get("/{instance_id}/conversations", response_model=BotConversationsListResponse)
async def get_bot_conversations(
    instance_id: UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    """
    Get all conversations for a specific bot instance.
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
            
        conversations = await service.get_instance_conversations(
            instance_id=instance_id,
            tenant_id=tenant_id,
            user_id=UUID(user.sub),
            offset=offset,
            limit=limit
        )
        
        # Convert to response model format
        conversation_responses = [
            BotConversationResponse(**conv) for conv in conversations
        ]
        
        return BotConversationsListResponse(
            conversations=conversation_responses,
            total=len(conversation_responses)  # In a real implementation, would get actual total count
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(e)}"
        )
