from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, constr
from typing import Annotated, Optional, Dict, Any


class ChatMessageRequest(BaseModel):
    message: Annotated[str, constr(min_length=1, max_length=4096)]
    chatbot_instance_id: UUID = Field(
        ..., description="ID of the bot instance this conversation belongs to"
    )
    conversation_id: Optional[UUID] = Field(
        None, description="If provided, appends to existing conversation; otherwise, starts new."
    )
    metadata: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    message_id: UUID
    conversation_id: UUID
    chatbot_instance_id: UUID
    content: str
    role: str  # 'assistant', 'user', 'system'
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatHistoryMessage(BaseModel):
    message_id: UUID
    content: str
    role: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatHistoryResponse(BaseModel):
    conversation_id: UUID
    chatbot_instance_id: UUID
    title: str
    messages: List[ChatHistoryMessage]
    last_message_at: datetime

class BotConversationResponse(BaseModel):
    conversation_id: UUID
    chatbot_instance_id: UUID
    title: str
    last_message_at: datetime
    
class BotConversationsListResponse(BaseModel):
    conversations: List[BotConversationResponse]
    total: int

class FeedbackRequest(BaseModel):
    message_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1024)

class FeedbackResponse(BaseModel):
    feedback_id: UUID
    message_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime 