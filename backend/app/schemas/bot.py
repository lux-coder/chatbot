from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ChatbotInstanceBase(BaseModel):
    name: str
    style: str
    language: str
    icon: Optional[str] = None

class ChatbotInstanceCreate(ChatbotInstanceBase):
    pass

class ChatbotInstanceResponse(ChatbotInstanceBase):
    id: UUID
    user_id: UUID
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
