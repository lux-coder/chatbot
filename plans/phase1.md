# Phase 1: Basic Infrastructure Setup Implementation Plan

## Overview
This document outlines the detailed implementation steps for Phase 1 of the chatbot project, focusing on setting up the basic infrastructure components. This plan has been simplified to focus on core, runnable infrastructure.

## Current Status (Post-Refinement)
- PostgreSQL with schema-per-tenant capability is implemented (application layer to handle specific schema logic).
- Docker Compose file is significantly enhanced and service locations are aligned with `implementation_plan.md`.
- Core services (Postgres, Redis, Keycloak) Dockerfiles are created and correctly located.
- Nginx configuration includes reverse proxy, SSL (dev certs), security headers, OWASP CRS, and Gzip.
- `setup_infrastructure.sh` script is functional for core service deployment.
- Test coverage for application code is at 86% (infrastructure testing is separate).

## Implementation Steps

### 1. Docker Compose Environment Enhancement
**Status: DONE**
#### Tasks:
1. Update `docker-compose.yml`:
   - Health checks for all services: **DONE** (Core services verified, Nginx uses `curl /healthz` via its Dockerfile).
   - Proper networking between services: **DONE**.
   - Volume mappings for persistence: **DONE**.
   - Environment variable configurations: **DONE**.
2. Create/Locate service-specific Dockerfiles:
   - Backend service Dockerfile: **DONE** (`./backend/Dockerfile`).
   - Nginx service Dockerfile with ModSecurity: **DONE** (`./nginx/Dockerfile`).
   - Keycloak service Dockerfile: **DONE** (`./docker/services/keycloak/Dockerfile`).
   - Redis service Dockerfile: **DONE** (`./docker/services/redis/Dockerfile`).
3. Configure Docker networks (separate networks, isolation, DNS): **DONE**.

### 2. Nginx and WAF Configuration
**Status: LARGELY DONE**
#### Tasks:
1. Set up Nginx configuration (`./nginx/conf.d/app.conf`):
   - Configure reverse proxy settings: **DONE**.
   - Set up SSL/TLS termination (dev certs): **DONE**.
   - Configure proper headers (security headers): **DONE**.
   - Set up compression (Gzip): **DONE**.
   - Caching: **DEFERRED** (Can be added in a later phase if needed).
2. Configure ModSecurity WAF:
   - Install and configure ModSecurity: **DONE** (via Nginx Dockerfile).
   - Implement OWASP Core Rule Set: **DONE** (via Nginx Dockerfile).
   - Configure custom security rules: **DEFERRED**.
   - Set up WAF logging and monitoring: Basic Nginx logs to `stdout`. Advanced WAF-specific logging/monitoring **DEFERRED**.
3. Implement mTLS: **DEFERRED** (Not essential for basic setup).

### 3. PostgreSQL Enhancement
**Status: BASIC SETUP DONE**
#### Tasks:
1. Enhance current PostgreSQL setup:
   - Connection pooling: **DEFERRED** (Application or dedicated service like PgBouncer later).
   - Proper backup strategy: **DEFERRED** (Operational concern for later phases).
   - Implement monitoring: Basic health check **DONE**. Advanced DB monitoring via Prometheus **PENDING** (Part of Monitoring Stack setup).
   - Configure logging: **DONE** (Postgres logs to `stdout`).
2. Schema-per-tenant improvements: **DEFERRED TO APPLICATION LAYER**. Infrastructure provides the database instance.
   - Automated schema creation: **DEFERRED**.
   - Schema migration strategy: **DEFERRED**.
   - Schema isolation: **DEFERRED** (Conceptual, to be enforced by application).
   - Tenant cleanup procedures: **DEFERRED**.

### 4. Redis Configuration
**Status: BASIC SETUP DONE**
#### Tasks:
1. Set up Redis:
   - Configure persistence (AOF): **DONE**.
   - Set up replication: **DEFERRED**.
   - Implement security measures (`requirepass`): **DONE**.
   - Configure resource limits (`maxmemory`): **DONE**.
2. Configure session storage: **DEFERRED TO APPLICATION LAYER**.
3. Set up error queues (DLQ): **DEFERRED TO APPLICATION LAYER**.

### 5. Keycloak Setup
**Status: BASIC INSTANCE RUNNING**
#### Tasks:
1. Basic Keycloak configuration:
   - Keycloak server instance running and accessible: **DONE**.
   - Initial realm & client applications setup: **MANUAL STEP** (Post-Phase 1 automation or specific scripts can enhance this).
   - User federation: **DEFERRED/REMOVED**.
   - Configure authentication flows: **MANUAL STEP** / **DEFERRED** for automation.
2. Security configuration:
   - Configure password policies: **MANUAL STEP** / **DEFERRED** for automation.
   - Set up MFA: **DEFERRED/REMOVED**.
   - Configure session policies: **MANUAL STEP** / **DEFERRED** for automation.
   - Set up email verification: **DEFERRED/REMOVED** (Requires SMTP server).

### 6. Monitoring Stack (Prometheus, Grafana, Loki)
**Status: IN PROGRESS (Configs created, Docker Compose updated)**
#### Tasks:
1. Add Monitoring Services to `docker-compose.yml`:
   - Prometheus (metrics collection): **DONE**.
   - Grafana (visualization): **DONE**.
   - Loki (log aggregation): **DONE**.
   - Promtail (log shipping): **DONE**.
   - Redis Exporter (for Redis metrics): **DONE**.
   - Postgres Exporter (for PostgreSQL metrics): **DONE**.
   - Nginx Exporter (for Nginx metrics): **DONE**.
2. Configure Prometheus (`./monitoring/prometheus/prometheus.yml`):
   - Basic Prometheus self-scrape: **DONE**.
   - Scrape configuration for Keycloak: **DONE** (Keycloak exposes `/metrics`).
   - Scrape configuration for Redis (via Redis Exporter): **DONE**.
   - Scrape configuration for Postgres (via Postgres Exporter): **DONE**.
   - Scrape configuration for Nginx (via Nginx Prometheus Exporter): **DONE**.
   - Scrape configuration for application services (Backend, AI Service, Worker - **PENDING APP IMPLEMENTATION of /metrics**).
3. Configure Loki & Promtail (`./monitoring/loki/`, `./monitoring/promtail/`):
   - Basic Loki configuration: **DONE**.
   - Promtail configuration for Docker container log discovery: **DONE**.
4. Grafana Setup:
   - Grafana service running: **DONE**.
   - Add Loki as a datasource in Grafana: **MANUAL STEP** (or via provisioning - **DEFERRED**).
   - Add Prometheus as a datasource in Grafana: **MANUAL STEP** (or via provisioning - **DEFERRED**).
   - Create basic dashboards: **DEFERRED**.
5. Ensure services expose metrics (where applicable):
   - Keycloak: **DONE** (via `KC_METRICS_ENABLED=true`).
   - Redis: **DONE** (via `redis_exporter`).
   - PostgreSQL: **DONE** (via `postgres_exporter`).
   - Nginx: **DONE** (via `nginx-prometheus-exporter`).
   - Custom Applications (Backend, etc.): **PENDING** (Application code to expose /metrics endpoint).

## Dependencies
- Docker and Docker Compose: **MET**
- Nginx with ModSecurity: **MET**
- PostgreSQL 15+: **MET**
- Redis 7+: **MET**
- Keycloak 22+: **MET**
- Prometheus, Grafana, Loki/Promtail: **Services added, configuration in progress.**

## Security Considerations
- All services must run with least privilege: **ONGOING** (Dockerfiles use non-root where possible).
- Secrets management through Docker secrets: **PARTIALLY MET** (Passwords read from files, mounted as env vars. True Docker secrets for swarm/k8s).
- Network isolation between services: **MET**.
- Regular security updates: **OPERATIONAL CONCERN**.
- Proper certificate management: Using self-signed for dev. Production certs **DEFERRED**.
- Secure configuration defaults: **ONGOING**.

## Testing Requirements for Phase 1 Infrastructure
- Core infrastructure services (Postgres, Redis, Keycloak, Nginx) start via `setup_infrastructure.sh`: **MET**.
- Monitoring services (Prometheus, Grafana, Loki, Promtail) start with `docker compose up`: **PENDING VERIFICATION**.
- Prometheus scrapes metrics from itself, Keycloak, Redis Exporter: **PENDING VERIFICATION**.
- Loki receives logs from other containers via Promtail: **PENDING VERIFICATION**.
- Grafana connects to Prometheus and Loki: **PENDING MANUAL CONFIG & VERIFICATION**.
- WAF blocks common attack patterns (basic test): **MANUAL TEST / DEFERRED**.
- PostgreSQL properly isolates tenant data: **APPLICATION CONCERN** (DB is ready).
- Redis successfully handles sessions: **APPLICATION CONCERN** (Redis is ready).
- Keycloak authenticates users (manual setup of a test user/client): **MANUAL TEST**.

## Deliverables for Phase 1 (Revised)
1. Complete Docker Compose configuration including core and monitoring services: **LARGELY DONE, PENDING MONITORING VERIFICATION**.
2. Nginx and WAF configuration files (basic setup): **DONE**.
3. Database initialization scripts (directory structure ready): **DONE** (actual scripts are app-specific).
4. Redis configuration files (via Docker Compose args): **DONE**.
5. Keycloak running, allowing manual realm setup and export: **DONE**.
6. Basic Monitoring configuration files (Prometheus, Loki, Promtail): **DONE**.
7. Updated `setup_infrastructure.sh` script: **DONE**.
8. This updated Phase 1 plan document: **YOU ARE HERE**.

## Success Criteria (Revised for Basic Setup)
- All services defined in `docker-compose.yml` (core + monitoring) start successfully.
- Nginx serves as a reverse proxy with basic WAF and SSL (dev certs).
- PostgreSQL and Redis are running, persistent, and accessible by other services.
- Keycloak is running and accessible for manual administration.
- Prometheus is collecting basic metrics from configured targets (itself, Keycloak, Redis Exporter).
- Loki is collecting logs from containers.
- Grafana can be manually configured to view metrics and logs.

## Timeline
Estimated time: 1-2 more days for monitoring setup verification and minor adjustments.
- Week 1 (Retroactively): Docker, Nginx, PostgreSQL, Redis, Keycloak core setup - **LARGELY COMPLETE**.
- Week 2 (Current focus): Monitoring Stack integration, Phase 1 finalization & documentation update - **IN PROGRESS**. 