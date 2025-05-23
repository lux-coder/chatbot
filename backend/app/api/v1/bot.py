from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.bot import (
    ChatbotInstanceCreate,
    ChatbotInstanceResponse,
)
from app.services.auth import get_current_user, UserToken
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
    instance = await service.create_instance(
        user_id=UUID(user.sub),
        tenant_id=tenant_id,
        name=request.name,
        style=request.style,
        language=request.language,
        icon=request.icon,
    )
    return ChatbotInstanceResponse.from_orm(instance)


@router.get("/", response_model=List[ChatbotInstanceResponse])
async def list_chatbot_instances(
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
    instances = await service.list_instances(user_id=UUID(user.sub), tenant_id=tenant_id)
    return [ChatbotInstanceResponse.from_orm(i) for i in instances]


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chatbot_instance(
    instance_id: UUID,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    service: ChatbotInstanceService = Depends(get_bot_service),
):
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
    instance = await service.publish_instance(instance_id, tenant_id)
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Instance not found")
    return ChatbotInstanceResponse.from_orm(instance)
