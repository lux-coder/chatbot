import pytest
import pytest_asyncio

from app.services.chat import ChatService
from app.core.config.test_settings import get_test_settings

class DummyAIService:
    async def generate_response(self, *args, **kwargs):
        return "ok"

@pytest_asyncio.fixture
async def chat_service(chat_repository) -> ChatService:
    return ChatService(
        chat_repository=chat_repository,
        ai_service=DummyAIService(),
        settings=get_test_settings(),
    )

@pytest.mark.asyncio
async def test_get_chat_history(chat_service, test_user, test_conversation, test_message, tenant_context_manager):
    async with tenant_context_manager:
        history = await chat_service.get_chat_history(
            user_id=test_user.id,
            tenant_id=test_user.tenant_id,
            conversation_id=test_conversation.id,
        )
        assert history["conversation_id"] == test_conversation.id
        assert len(history["messages"]) == 1
        assert history["messages"][0]["message_id"] == test_message.id

@pytest.mark.asyncio
async def test_store_feedback(chat_service, test_user, test_message, tenant_context_manager):
    async with tenant_context_manager:
        result = await chat_service.store_feedback(
            message_id=test_message.id,
            user_id=test_user.id,
            rating=5,
            comment="Great",
        )
        assert result["rating"] == 5
        assert result["comment"] == "Great"
