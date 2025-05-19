import pytest
import pytest_asyncio
from uuid import UUID
from datetime import datetime
from app.models.chat import Conversation, Message
from app.models.user import User
from app.repositories.chat import ConversationRepository, MessageRepository
from app.core.tenancy import tenant_context


@pytest_asyncio.fixture
async def test_conversation(test_user, tenant_context_manager) -> Conversation:
    """Create a test conversation."""
    async with tenant_context_manager:
        conversation = await Conversation.create(
            title="Test Conversation",
            user=test_user,
            tenant_id=test_user.tenant_id
        )
        return conversation


@pytest_asyncio.fixture
async def test_message(test_conversation, tenant_context_manager) -> Message:
    """Create a test message."""
    async with tenant_context_manager:
        message = await Message.create(
            conversation=test_conversation,
            content="Test message content",
            role="user",
            tenant_id=test_conversation.tenant_id
        )
        return message


@pytest.mark.asyncio
class TestConversationModel:
    """Test suite for Conversation model."""

    async def test_create_conversation(self, test_user, tenant_context_manager):
        """Test conversation creation."""
        async with tenant_context_manager:
            conversation = await Conversation.create(
                title="New Conversation",
                user=test_user,
                tenant_id=test_user.tenant_id
            )
            assert conversation.title == "New Conversation"
            assert conversation.user_id == test_user.id
            assert conversation.tenant_id == test_user.tenant_id

    async def test_get_messages(self, test_conversation, test_message, tenant_context_manager):
        """Test getting messages from a conversation."""
        async with tenant_context_manager:
            messages = await test_conversation.get_messages()
            assert len(messages) == 1
            assert messages[0].id == test_message.id
            assert messages[0].content == test_message.content

    async def test_add_message(self, test_conversation, tenant_context_manager):
        """Test adding a message to a conversation."""
        async with tenant_context_manager:
            content = "New test message"
            message = await test_conversation.add_message(
                content=content,
                role="user",
                metadata={"tokens": 10}
            )
            assert message.content == content
            assert message.role == "user"
            assert message.metadata == {"tokens": 10}
            assert message.conversation_id == test_conversation.id


@pytest.mark.asyncio
class TestMessageModel:
    """Test suite for Message model."""

    async def test_create_message(self, test_conversation, tenant_context_manager):
        """Test message creation."""
        async with tenant_context_manager:
            message = await Message.create(
                conversation=test_conversation,
                content="Test message",
                role="user",
                tenant_id=test_conversation.tenant_id
            )
            assert message.content == "Test message"
            assert message.role == "user"
            assert message.conversation_id == test_conversation.id

    async def test_message_properties(self, test_message, tenant_context_manager):
        """Test message role properties."""
        async with tenant_context_manager:
            assert test_message.is_user_message
            assert not test_message.is_assistant_message
            assert not test_message.is_system_message

            # Test assistant message
            test_message.role = "assistant"
            assert not test_message.is_user_message
            assert test_message.is_assistant_message
            assert not test_message.is_system_message

            # Test system message
            test_message.role = "system"
            assert not test_message.is_user_message
            assert not test_message.is_assistant_message
            assert test_message.is_system_message


@pytest.mark.asyncio
class TestConversationRepository:
    """Test suite for ConversationRepository."""

    async def test_create_conversation(self, conversation_repository, test_user, tenant_context_manager):
        """Test conversation creation through repository."""
        async with tenant_context_manager:
            conversation = await conversation_repository.create_conversation(
                user_id=test_user.id,
                title="Repository Test Conversation"
            )
            assert conversation.title == "Repository Test Conversation"
            assert conversation.user_id == test_user.id

    async def test_get_user_conversations(self, conversation_repository, test_user, test_conversation, tenant_context_manager):
        """Test getting user conversations."""
        async with tenant_context_manager:
            conversations = await conversation_repository.get_user_conversations(test_user.id)
            assert len(conversations) == 1
            assert conversations[0].id == test_conversation.id

    async def test_get_conversation_with_messages(self, conversation_repository, test_conversation, test_message, tenant_context_manager):
        """Test getting conversation with messages."""
        async with tenant_context_manager:
            conversation = await conversation_repository.get_conversation_with_messages(test_conversation.id)
            assert conversation.id == test_conversation.id
            assert len(conversation.messages) == 1
            assert conversation.messages[0].id == test_message.id


@pytest.mark.asyncio
class TestMessageRepository:
    """Test suite for MessageRepository."""

    async def test_create_message(self, message_repository, test_conversation, tenant_context_manager):
        """Test message creation through repository."""
        async with tenant_context_manager:
            message = await message_repository.create_message(
                conversation_id=test_conversation.id,
                content="Repository Test Message",
                role="user",
                metadata={"tokens": 15}
            )
            assert message.content == "Repository Test Message"
            assert message.role == "user"
            assert message.metadata == {"tokens": 15}

    async def test_get_conversation_messages(self, message_repository, test_conversation, test_message, tenant_context_manager):
        """Test getting conversation messages."""
        async with tenant_context_manager:
            messages = await message_repository.get_conversation_messages(test_conversation.id)
            assert len(messages) == 1
            assert messages[0].id == test_message.id

    async def test_get_latest_message(self, message_repository, test_conversation, test_message, tenant_context_manager):
        """Test getting latest message."""
        async with tenant_context_manager:
            latest_message = await message_repository.get_latest_message(test_conversation.id)
            assert latest_message.id == test_message.id

    async def test_count_messages(self, message_repository, test_conversation, test_message, tenant_context_manager):
        """Test counting messages."""
        async with tenant_context_manager:
            # Count all messages
            count = await message_repository.count_messages(test_conversation.id)
            assert count == 1

            # Count user messages
            count = await message_repository.count_messages(test_conversation.id, role="user")
            assert count == 1

            # Count assistant messages
            count = await message_repository.count_messages(test_conversation.id, role="assistant")
            assert count == 0 