# Phase 2: Security Foundation – Implementation Plan

## 1. JWT Authentication with Keycloak

- [ ] Implement FastAPI dependency for JWT validation using Keycloak public keys.
- [ ] Add middleware or dependencies to extract and validate JWT from requests.
- [ ] Enforce authentication on all protected endpoints.
- [ ] Implement role-based access control (RBAC) using Keycloak roles.
- [ ] Ensure multi-tenant support in authentication (tie JWT claims to tenant context).

## 2. Secure Headers in Nginx

- [x] Security headers are present in `nginx/conf.d/app.conf` (X-Frame-Options, X-XSS-Protection, etc.).
- [ ] Add/verify HSTS header (Strict-Transport-Security) for production.
- [ ] Review and update Content-Security-Policy as needed.

## 3. CORS Policies

- [ ] Implement CORS middleware in FastAPI backend.
- [ ] Restrict allowed origins, methods, and headers according to frontend deployment.

## 4. Rate Limiting

- [ ] Implement rate limiting middleware in FastAPI (e.g., using Redis).
- [ ] Configure per-user and per-IP rate limits for API endpoints.
- [ ] Add rate limiting for AI endpoints (to be extended in Phase 4).

## 5. Audit Logging

- [ ] Implement audit logging for authentication events, security-relevant actions, and admin operations.
- [ ] Use structured logging (e.g., with structlog) and ensure logs are sent to ELK/Loki stack.
- [ ] Add a background worker task for audit log processing (see `worker/tasks/audit.py` in plan).

## 6. mTLS Between Services

- [ ] Configure mTLS in Nginx for backend and AI service communication.
- [ ] Generate and distribute service certificates.
- [ ] Update Docker and Nginx configs to require client certificates for internal API calls.

## 7. Additional Security Hardening

- [x] WAF (ModSecurity) is enabled in Nginx.
- [ ] Review and tune WAF rules, add custom rules as needed.
- [ ] Ensure error queues (Redis) are protected and only accessible by trusted services.
- [ ] Review and restrict Docker network access between services.

## 8. Testing and Validation

- [ ] Write and run tests for authentication, CORS, rate limiting, and audit logging.
- [ ] Validate mTLS setup with integration tests.
- [ ] Use infrastructure testing scripts to verify all security controls.

---

**Deliverables:**
- All code/config changes tracked in this plan.
- Unit and integration tests for all new security features.
- Documentation for security configuration and operational procedures. 