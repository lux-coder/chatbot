# Database Layer Implementation Plan

## Overview
This document outlines the step-by-step implementation plan for the database layer using Tortoise ORM, PostgreSQL, and Pydantic models following the project standards and requirements.

## Prerequisites
- PostgreSQL 15+
- Python 3.12+
- Tortoise ORM
- FastAPI
- Pydantic v2

## Implementation Steps

### 1. Database Configuration Setup

1.1. Create Database Configuration
```python
# app/core/config/database.py
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    
    # Per-tenant settings
    SCHEMA_PREFIX: str = "tenant_"
    
    @property
    def postgres_url(self) -> str:
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
```

1.2. Implement Database Initialization
```python
# app/core/database.py
from tortoise import Tortoise
from app.core.config.database import DatabaseSettings

async def initialize_database(settings: DatabaseSettings) -> None:
    await Tortoise.init(
        db_url=settings.postgres_url,
        modules={'models': ['app.models']},
        generate_schemas=True
    )
```

### 2. Base Models Implementation

2.1. Create Base Model Classes
```python
# app/models/base.py
from tortoise import Model, fields
from datetime import datetime

class BaseModel(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        abstract = True

class TenantModel(BaseModel):
    tenant_id = fields.UUIDField()
    
    class Meta:
        abstract = True
```

### 3. Domain Models Implementation

3.1. User Model
```python
# app/models/user.py
from app.models.base import TenantModel
from tortoise import fields

class User(TenantModel):
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_superuser = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)

    class Meta:
        table = "users"
```

3.2. Chat Models
```python
# app/models/chat.py
from app.models.base import TenantModel
from tortoise import fields

class Conversation(TenantModel):
    title = fields.CharField(max_length=255)
    user = fields.ForeignKeyField('models.User', related_name='conversations')
    
    class Meta:
        table = "conversations"

class Message(TenantModel):
    conversation = fields.ForeignKeyField('models.Conversation', related_name='messages')
    content = fields.TextField()
    role = fields.CharField(max_length=20)  # user, assistant, system
    timestamp = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "messages"
```

### 4. Pydantic Models Implementation

4.1. Base Pydantic Models
```python
# app/schemas/base.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class BaseResponseSchema(BaseSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
```

4.2. User Schemas
```python
# app/schemas/user.py
from app.schemas.base import BaseSchema, BaseResponseSchema
from pydantic import EmailStr

class UserCreate(BaseSchema):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseResponseSchema):
    username: str
    email: EmailStr
    is_superuser: bool
```

4.3. Chat Schemas
```python
# app/schemas/chat.py
from app.schemas.base import BaseSchema, BaseResponseSchema
from uuid import UUID

class ConversationCreate(BaseSchema):
    title: str
    user_id: UUID

class ConversationResponse(BaseResponseSchema):
    title: str
    user_id: UUID

class MessageCreate(BaseSchema):
    conversation_id: UUID
    content: str
    role: str

class MessageResponse(BaseResponseSchema):
    conversation_id: UUID
    content: str
    role: str
    timestamp: datetime
```

### 5. Database Migration Setup

5.1. Create Migration System
```python
# app/core/migrations.py
from tortoise import Tortoise, run_async
from aerich import Command

async def init_db(config: dict) -> None:
    command = Command(
        tortoise_config=config,
        app="models",
        location="./migrations"
    )
    await command.init()
    await command.migrate()
```

### 6. Multi-tenancy Implementation

6.1. Create Tenant Context Manager
```python
# app/core/tenancy.py
from contextvars import ContextVar
from uuid import UUID

tenant_context: ContextVar[UUID] = ContextVar('tenant_id')

class TenantContextManager:
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.token = None

    async def __aenter__(self):
        self.token = tenant_context.set(self.tenant_id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        tenant_context.reset(self.token)
```

### 7. Repository Pattern Implementation

7.1. Create Base Repository
```python
# app/repositories/base.py
from typing import TypeVar, Generic, Type
from tortoise import Model
from uuid import UUID

ModelType = TypeVar("ModelType", bound=Model)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, **kwargs) -> ModelType:
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: UUID) -> ModelType:
        return await self.model.get(id=id)

    async def list(self, **kwargs) -> list[ModelType]:
        return await self.model.filter(**kwargs)

    async def update(self, id: UUID, **kwargs) -> ModelType:
        obj = await self.get_by_id(id)
        await obj.update_from_dict(kwargs).save()
        return obj

    async def delete(self, id: UUID) -> None:
        await self.model.filter(id=id).delete()
```

## Testing Strategy

### 1. Unit Tests
- Create test database configuration
- Test all models CRUD operations
- Test schema validations
- Test tenant isolation

### 2. Integration Tests
- Test database migrations
- Test multi-tenancy
- Test repository pattern
- Test relationships between models

## Security Considerations

1. Data Isolation
- Implement row-level security
- Enforce tenant isolation
- Validate tenant context in middleware

2. Input Validation
- Use Pydantic validators
- Implement custom validation rules
- Sanitize all inputs

3. Access Control
- Implement model-level permissions
- Use database roles and grants
- Audit sensitive operations

## Performance Optimization

1. Database Indexes
- Create indexes for frequently queried fields
- Implement composite indexes where needed
- Monitor and optimize query performance

2. Caching Strategy
- Implement Redis caching for frequent queries
- Cache invalidation strategy
- Cache warm-up procedures

## Deployment Considerations

1. Migration Strategy
- Version control for migrations
- Rollback procedures
- Zero-downtime migration plan

2. Backup Strategy
- Regular backup schedule
- Point-in-time recovery
- Backup verification procedures

## Monitoring and Maintenance

1. Health Checks
- Database connection monitoring
- Query performance monitoring
- Connection pool metrics

2. Logging
- SQL query logging
- Error logging
- Performance metrics logging 