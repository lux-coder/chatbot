# Phase 3: Chatbot Service – Concrete Implementation Plan

## 1. Domain Overview
- **Goal:** Implement a secure, multi-tenant chatbot microservice supporting both OpenAI and Llama.cpp, with strong authentication, audit logging, and scalable architecture.
- **Key Features:** 
  - RESTful API for chat interaction
  - Multi-model support (OpenAI, Llama.cpp)
  - User authentication (Keycloak/JWT)
  - Tenant isolation
  - Rate limiting, audit logging, and monitoring

---

## 2. API Design

### Endpoints (v1)
- `POST /api/v1/chat/`: Submit a user message, receive AI response
- `GET /api/v1/chat/history`: Retrieve chat history for the authenticated user/tenant
- `POST /api/v1/chat/feedback`: Submit feedback on AI response (optional, for future analytics)
- `GET /api/v1/healthz`: Health check

**All endpoints:**
- Require JWT authentication (Keycloak)
- Enforce tenant context via header (`X-Tenant-ID`)
- Use Pydantic models for request/response validation

---

## 3. Core Components

### a. Chat Service (Domain Logic)
- Receives user message, pseudonymizes PII if using external AI
- Selects model (OpenAI or Llama.cpp) based on config/tenant
- Calls AI model (async, with timeout and error handling)
- Stores chat history in PostgreSQL (per-tenant schema)
- Publishes audit logs to worker/queue

### b. AI Integration
- **OpenAI:** Use HTTPX for async calls, ensure PII pseudonymization
- **Llama.cpp:** Use local Python bindings, prefer for privacy
- **Fallback:** If local model fails, fallback to OpenAI (with logging)

### c. Persistence
- **PostgreSQL:** Store chat messages, user info, feedback (schema-per-tenant)
- **Redis:** Cache recent conversations, store error queue (DLQ)

### d. Security
- JWT validation (Keycloak public keys)
- Role-based access control (admin/user)
- Input validation (Pydantic)
- Rate limiting (per-user, per-IP, per-tenant, via Redis)
- Audit logging (all chat and admin actions)

### e. Observability
- Prometheus metrics for all endpoints and model calls
- Structured logging (ELK/Loki)
- Health check endpoint

---

## 4. Implementation Steps

### 1. API & Models
- [ ] Define Pydantic models for chat requests, responses, history, feedback
- [ ] Implement FastAPI routers for all endpoints
- [ ] Add dependency injection for DB, Redis, and Keycloak

### 2. Authentication & Tenant Context
- [ ] Implement JWT validation dependency
- [ ] Enforce `X-Tenant-ID` header and context middleware
- [ ] Add role-based access control decorators

### 3. Chat Logic
- [ ] Implement chat service: receive message, select model, call AI, store result
- [ ] Integrate OpenAI and Llama.cpp clients (with fallback)
- [ ] Add PII pseudonymization for external calls

### 4. Persistence
- [ ] Implement Tortoise ORM models for chat, user, feedback (with tenant schema)
- [ ] Add chat history retrieval and storage logic

### 5. Security & Rate Limiting
- [ ] Add CORS middleware and secure headers
- [ ] Implement rate limiting using Redis
- [ ] Add input validation and error handling

### 6. Audit Logging & Monitoring
- [ ] Publish audit logs to worker/queue
- [ ] Expose Prometheus metrics
- [ ] Integrate structured logging

### 7. Testing
- [ ] Write unit tests for all business logic (pytest)
- [ ] Write integration tests for API endpoints
- [ ] Achieve 80%+ code coverage

### 8. Deployment
- [ ] Update Dockerfile and docker-compose for new dependencies
- [ ] Ensure health checks and resource limits are set

---

## 5. Deliverables
- Fully functional, secure chatbot microservice
- API documentation (OpenAPI/Swagger)
- Unit and integration tests
- Deployment manifests (Docker, Kubernetes if needed)
- Operational runbook for security and monitoring 