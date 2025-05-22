# Tenant and User Integration Fix Plan

## Problem Analysis

Based on the logs and code examination, we've identified these key issues:

1. **Tenant ID Mismatch**: The client is using a tenant ID that doesn't exist in the system
2. **User ID Mismatch**: The user ID from Keycloak JWT doesn't match the user ID in our database
3. **Tenant Context Management**: Issues with tenant context during user creation/verification
4. **User Creation Flow**: Users are created but not properly associated with conversations

## Root Causes

1. **Missing Tenant Discovery Mechanism**: Clients have no way to discover the correct tenant ID
2. **User ID Synchronization Issue**: Our system creates new UUIDs for users rather than using Keycloak's IDs
3. **Tenant Context Switching**: Context switching between tenants during request processing causes confusion
4. **Incomplete User Synchronization**: User objects aren't fully synchronized between Keycloak and our database

## Solution Plan

### 1. Implement Tenant Discovery Endpoint

Create a dedicated endpoint for clients to discover their tenant ID:

```python
@router.get("/tenant", response_model=TenantInfoResponse)
async def get_tenant_info(
    user: UserToken = Depends(get_current_user),
    tenant_service: TenantService = Depends(get_tenant_service),
):
    """
    Returns tenant information for the authenticated user.
    If the tenant doesn't exist, creates it automatically.
    """
    tenant = await tenant_service.get_or_create_tenant_for_user(user.sub)
    return {
        "tenant_id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active
    }
```

### 2. Fix User ID Synchronization

Modify the user creation process to use Keycloak's user ID:

```python
# In app/services/auth.py
async def sync_user_from_keycloak(self, token: UserToken, tenant_id: UUID) -> User:
    """Synchronize user data from Keycloak token."""
    async with TenantContextManager(tenant_id):
        # Use the Keycloak user ID (sub) as our user ID
        user = await self.user_repository.get_by_id(UUID(token.sub))
        
        if not user:
            # Create user with Keycloak's ID
            user = await self.user_repository.create_user(
                id=UUID(token.sub),  # Use Keycloak's ID directly
                username=token.preferred_username,
                email=token.email,
                first_name=token.given_name,
                last_name=token.family_name
            )
            
        # Update user profile if needed
        if user:
            await user.update_last_login()
            
        return user
```

### 3. Update User Repository to Support External IDs

Modify the `create_user` method to accept an explicit ID:

```python
# In app/repositories/user.py
async def create_user(
    self,
    username: str,
    email: str,
    id: Optional[UUID] = None,  # New parameter
    password: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_superuser: bool = False,
) -> User:
    """Create a new user with optional ID and password."""
    user_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "is_superuser": is_superuser,
    }
    
    if id:
        user_data["id"] = id
        
    if password:
        user_data["hashed_password"] = User.hash_password(password)
        
    # Let TenantRepository handle tenant_id from context
    return await self.create(**user_data)
```

### 4. Improve Tenant Management

Create a consistent tenant management approach:

```python
# In app/services/tenant.py
async def get_or_create_tenant_for_user(self, user_id: UUID) -> dict:
    """
    Get or create a tenant for a user.
    In multi-tenant scenarios, would include tenant assignment logic.
    """
    # For now, simple approach: one tenant per user
    tenant_name = f"Tenant for user {user_id}"
    
    # Check if user already has a tenant (simplified - would need mapping table in real app)
    # This would use a user-to-tenant mapping in a real multi-tenant app
    tenant = await self.tenant_repo.get_by_name(tenant_name)
    
    if not tenant:
        tenant = await self.tenant_repo.create_tenant(name=tenant_name)
        
        await log_security_event(
            event_type="TENANT_CREATED_FOR_USER",
            tenant_id=str(tenant.id),
            user_id=str(user_id),
            details={"name": tenant_name}
        )
    
    return tenant
```

### 5. Update Auth Flow in API Routes

Ensure tenant context is properly set and user exists before processing:

```python
# In app/api/v1/chat.py
@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    user: UserToken = Depends(get_current_user),
    tenant_id: UUID = Depends(require_tenant),
    chat_service: ChatService = Depends(get_chat_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Submit a user message and receive an AI response."""
    # Ensure user exists in database with correct ID
    db_user = await auth_service.sync_user_from_keycloak(user, tenant_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synchronize user data"
        )
    
    # Now process the message with verified user
    response = await chat_service.process_message(
        user_id=UUID(user.sub),  # Use Keycloak ID directly
        tenant_id=tenant_id,
        message=request.message,
        conversation_id=request.conversation_id
    )
    
    return ChatMessageResponse(**response)
```

### 6. Improve Error Handling and Debugging

Add more detailed error logging to identify synchronization issues:

```python
# Example improved error handler
try:
    # Existing code
except Exception as e:
    error_id = str(uuid.uuid4())
    logger.error(
        f"Error ID: {error_id} - {type(e).__name__} in user synchronization",
        extra={
            "error_id": error_id,
            "user_id": str(user.sub),
            "tenant_id": str(tenant_id),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"User synchronization error (ID: {error_id})"
    )
```

## Implementation Steps

1. Create the tenant discovery endpoint
2. Update user repository to accept explicit IDs
3. Modify user synchronization to use Keycloak IDs
4. Improve tenant management for user-tenant association
5. Update API routes to ensure proper synchronization
6. Add better error handling and logging
7. Create tests to verify the fixes

## Testing Plan

1. Test tenant discovery endpoint with valid Keycloak JWT
2. Verify user creation with correct Keycloak ID
3. Test conversation creation with synchronized user
4. Verify tenant context management during API calls
5. Test error scenarios and validate proper error responses

## Rollout Plan

1. Implement changes in development environment
2. Run full test suite to verify fixes
3. Create database migration for any schema changes
4. Deploy to staging environment for integration testing
5. Monitor logs for any synchronization issues
6. Deploy to production with rollback plan 