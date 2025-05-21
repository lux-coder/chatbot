import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime

from app.main import app
from app.services.auth import UserToken, get_current_user, get_current_user_roles
from app.api.deps import get_chat_service
from app.core.security.tenancy import require_tenant

class DummyChatService:
    async def process_message(self, user_id, tenant_id, message, conversation_id=None):
        return {
            "message_id": uuid4(),
            "conversation_id": uuid4(),
            "content": "Response",
            "role": "assistant",
            "timestamp": datetime.utcnow(),
            "metadata": None,
        }

@pytest.fixture
def override_dependencies():
    app.dependency_overrides[get_current_user] = lambda: UserToken(sub="user", tenant_id=str(uuid4()))
    app.dependency_overrides[get_current_user_roles] = lambda: ["user"]
    app.dependency_overrides[require_tenant] = lambda: uuid4()

    dummy_service = DummyChatService()
    async def _get_chat_service():
        return dummy_service
    app.dependency_overrides[get_chat_service] = _get_chat_service
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_send_message_endpoint(override_dependencies):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/chat/",
            json={"message": "Hi"},
            headers={"X-Tenant-ID": str(uuid4()), "Authorization": "Bearer token"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["role"] == "assistant"
        assert "message_id" in body
        assert "conversation_id" in body
