# Chat Service Implementation Plan

## 1. Service Structure ✅
```python
# backend/app/services/chat.py

from typing import Optional, List, Dict
from uuid import UUID
from app.repositories.chat import ChatRepository
from app.models.chat import Message, Conversation
from app.services.ai import AIService
from app.core.config import Settings
from app.core.monitoring import log_chat_event
from app.core.security import PIIHandler
from app.core.exceptions import TenantMismatchError
```

## 2. Implementation Steps

### Step 1: Core Chat Service Class ✅
```python
class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository,
        ai_service: AIService,
        settings: Settings
    ):
        self.chat_repository = chat_repository
        self.ai_service = ai_service
        self.settings = settings
        self.pii_handler = PIIHandler()
        self.max_retries = 3
        self.retry_delay = 1  # seconds
```

### Step 2: Message Processing Methods ✅
1. `async def process_message()` ✅
   - Handle incoming user message
   - Validate input
   - Get conversation context
   - Call AI service with retries
   - Apply PII detection and masking
   - Store response
   - Return formatted response

2. `async def get_conversation_context()` ✅
   - Retrieve recent messages
   - Format context for AI model
   - Apply context window limits

### Step 3: History Management Methods ✅
1. `async def get_chat_history()` ✅
   - Retrieve paginated conversation history
   - Filter by user/tenant
   - Format for response

2. `async def create_conversation()` ✅
   - Initialize new conversation
   - Set metadata (user, tenant, timestamp)
   - Validate tenant ownership

### Step 4: Feedback Handling ⏳
1. `async def store_feedback()`
   - Validate feedback
   - Store in database
   - Trigger analytics event

## 3. Security Enhancements ✅

### PII Protection
```python
class PIIHandler:
    """
    Unified interface for PII detection and masking.
    """
    
    def __init__(self):
        self.detector = PIIDetector()
        self.masker = DataMasker()

    async def process_text(self, text: str) -> str:
        # Detect PII using both regex and NLP
        regex_matches = await self.detector.detect_regex_pii(text)
        ner_matches = await self.detector.detect_ner_pii(text)
        
        # Combine and mask all PII
        all_matches = regex_matches + ner_matches
        return await self.masker.mask_text(text, all_matches)
```

### Tenant Isolation
```python
async def _get_or_create_conversation(
    self,
    user_id: UUID,
    tenant_id: UUID,
    conversation_id: Optional[UUID] = None
) -> Conversation:
    if conversation_id:
        conversation = await self.chat_repository.get_conversation(conversation_id)
        if conversation.tenant_id != tenant_id:
            raise TenantMismatchError(
                f"Conversation {conversation_id} does not belong to tenant {tenant_id}"
            )
    return await self.chat_repository.create_conversation(
        user_id=user_id,
        tenant_id=tenant_id
    )
```

### Error Handling & Retries
```python
# AI Service retries with exponential backoff
for attempt in range(self.max_retries):
    try:
        ai_response = await self.ai_service.generate_response(
            message=masked_message,
            context=context,
            model_type=model_type
        )
        break
    except AIServiceError as e:
        if attempt == self.max_retries - 1:
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable"
            )
        await asyncio.sleep(self.retry_delay * (attempt + 1))
```

## 4. Implementation Status

1. **Basic Setup** ✅
   - [x] Create ChatService class
   - [x] Implement dependency injection
   - [x] Set up basic logging

2. **Core Message Processing** ✅
   - [x] Implement process_message
   - [x] Add conversation context handling
   - [x] Connect to repository layer
   - [x] Add PII protection
   - [x] Add retry mechanism

3. **History Management** ✅
   - [x] Implement get_chat_history
   - [x] Add pagination
   - [x] Add tenant filtering

4. **Feedback System** ⏳
   - [ ] Implement feedback storage
   - [ ] Add feedback validation
   - [ ] Connect to analytics

5. **Security Features** ✅
   - [x] PII detection and masking
   - [x] Tenant isolation
   - [x] Input validation
   - [x] Error handling
   - [x] Audit logging

6. **Testing** ⏳
   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] Load testing

## Next Steps
1. Complete the feedback system implementation
2. Write comprehensive test suite
3. Add performance optimizations if needed
4. Document API endpoints and error codes 