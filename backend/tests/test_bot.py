import pytest
import pytest_asyncio
from uuid import uuid4

from app.models.bot import ChatbotInstance

@pytest_asyncio.fixture
async def bot_instance(bot_repository, test_user, tenant_context_manager):
    async with tenant_context_manager:
        instance = await bot_repository.create_instance(
            user_id=test_user.id,
            name="Test Bot",
            style="fun",
            language="en",
            icon=":)",
        )
        return instance


@pytest.mark.asyncio
class TestChatbotInstanceRepository:
    async def test_create_list_delete_publish(self, bot_repository, bot_instance, test_user, tenant_context_manager):
        async with tenant_context_manager:
            bots = await bot_repository.list_instances(test_user.id)
            assert len(bots) == 1
            assert bots[0].name == "Test Bot"

            await bot_repository.publish_instance(bots[0].id)
            published = await bot_repository.get_by_id(bots[0].id)
            assert published.is_published

            await bot_repository.delete(bots[0].id)
            bots_after = await bot_repository.list_instances(test_user.id)
            assert len(bots_after) == 0
