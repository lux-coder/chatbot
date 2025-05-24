#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default: do not remove volumes
COMPLETE_TEARDOWN=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --complete_teardown=true)
      COMPLETE_TEARDOWN=true
      ;;
    --complete_teardown=false)
      COMPLETE_TEARDOWN=false
      ;;
    *)
      # Unknown option
      ;;
  esac
  shift
done

if $COMPLETE_TEARDOWN; then
  echo -e "\n${YELLOW}Cleaning up old containers and volumes (complete teardown)...${NC}"
  docker compose down -v
else
  echo -e "\n${YELLOW}Stopping old containers (preserving volumes and data)...${NC}"
  docker compose down
fi

echo -e "${YELLOW}Starting infrastructure setup...${NC}"

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p scripts/secrets
mkdir -p nginx/certs
mkdir -p docker/services/postgres/init
mkdir -p monitoring/prometheus
mkdir -p monitoring/loki
mkdir -p monitoring/promtail

# Remove old data from potential previous local bind mounts (optional, as named volumes are used)
# rm -rf docker/services/redis/data/* # Redis uses named volume 'redis_data'
# rm -rf docker/services/postgres/data/* # Postgres uses named volume 'postgres_data'

# Generate secrets
echo -e "\n${YELLOW}Generating secrets...${NC}"

if $COMPLETE_TEARDOWN || [ ! -f secrets/postgres_password.txt ]; then
  echo -e "${GREEN}Generating PostgreSQL password...${NC}"
  openssl rand -base64 32 > secrets/postgres_password.txt
else
  echo -e "${YELLOW}Using existing PostgreSQL password${NC}"
fi

if $COMPLETE_TEARDOWN || [ ! -f secrets/redis_password.txt ]; then
  echo -e "${GREEN}Generating Redis password...${NC}"
  openssl rand -base64 32 > secrets/redis_password.txt
else
  echo -e "${YELLOW}Using existing Redis password${NC}"
fi

# Ensure admin password is not base64 for Keycloak direct use
if $COMPLETE_TEARDOWN || [ ! -f secrets/keycloak_admin_password.txt ]; then
  echo -e "${GREEN}Generating Keycloak admin password (plain text)...${NC}"
  openssl rand -hex 16 > secrets/keycloak_admin_password.txt
else
  echo -e "${YELLOW}Using existing Keycloak admin password${NC}"
fi

if $COMPLETE_TEARDOWN || [ ! -f secrets/keycloak_secret.txt ]; then
  echo -e "${GREEN}Generating Keycloak client secret...${NC}"
  openssl rand -base64 32 > secrets/keycloak_secret.txt
else
  echo -e "${YELLOW}Using existing Keycloak client secret${NC}"
fi

if $COMPLETE_TEARDOWN || [ ! -f secrets/keycloak_webhook_secret.txt ]; then
  echo -e "${GREEN}Generating Keycloak webhook secret...${NC}"
  openssl rand -base64 32 > secrets/keycloak_webhook_secret.txt
else
  echo -e "${YELLOW}Using existing Keycloak webhook secret${NC}"
fi

# Set proper permissions
echo -e "\n${YELLOW}Setting file permissions...${NC}"
chmod 600 secrets/*

# Generate SSL certificates
echo -e "\n${YELLOW}Generating SSL certificates...${NC}"
./generate_ssl_certs.sh # Assuming this script is in the same directory (scripts/)

# Export passwords for docker-compose
export REDIS_PASSWORD=$(cat secrets/redis_password.txt)
export POSTGRES_PASSWORD=$(cat secrets/postgres_password.txt)
export KEYCLOAK_ADMIN_PASSWORD=$(cat secrets/keycloak_admin_password.txt)
export KEYCLOAK_CLIENT_SECRET=$(cat secrets/keycloak_secret.txt)
export KEYCLOAK_WEBHOOK_SECRET=$(cat secrets/keycloak_webhook_secret.txt)
export OPENAI_API_KEY=$(cat secrets/openai_api_key.txt)

# Start core services
echo -e "\n${YELLOW}Starting core services...${NC}"
docker compose up -d --build postgres redis keycloak

# Wait for services to be healthy
echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
# Basic health checks
echo -e "\n${YELLOW}Performing basic health checks...${NC}"

# Redis check
echo -e "\n${YELLOW}Testing Redis connection...${NC}"
if docker compose exec redis redis-cli -a "$REDIS_PASSWORD" ping | grep -q "PONG"; then
    echo -e "${GREEN}Redis is responding correctly${NC}"
else
    echo -e "${RED}Redis health check failed${NC}"
    exit 1
fi

# Postgres check
echo -e "\n${YELLOW}Testing PostgreSQL connection...${NC}"
if docker compose exec postgres pg_isready -U postgres -d chatbot | grep -q "accepting connections"; then
    echo -e "${GREEN}PostgreSQL is responding correctly${NC}"
else
    echo -e "${RED}PostgreSQL health check failed${NC}"
    exit 1
fi

# Keycloak check
echo -e "\n${YELLOW}Waiting for Keycloak to become ready...${NC}"
KEYCLOAK_READY=0
for i in {1..24}; do
    if curl -s -f http://localhost:9000/health/ready > /dev/null; then
        KEYCLOAK_READY=1
        break
    fi
    echo -e "${YELLOW}Keycloak not ready yet... (${i}/24)${NC}"
    sleep 5
done
if [ $KEYCLOAK_READY -eq 1 ]; then
    echo -e "${GREEN}Keycloak is responding correctly${NC}"
else
    echo -e "${RED}Keycloak health check failed${NC}"
    docker compose logs keycloak
    exit 1
fi

# Build Nginx image only if it doesn't exist to save time
if [ -z "$(docker images -q chatbot-nginx)" ]; then
    echo -e "\n${YELLOW}Building Nginx image (first run)...${NC}"
    docker compose build nginx
fi

# Start monitoring services
echo -e "\n${YELLOW}Starting monitoring services...${NC}"
docker compose up -d redis_exporter postgres_exporter nginx_exporter prometheus grafana loki promtail

# Wait for monitoring services to be healthy
echo -e "\n${YELLOW}Waiting for monitoring services to be healthy...${NC}"

# Redis Exporter check
echo -e "\n${YELLOW}Testing Redis Exporter...${NC}"
if curl -s -f http://localhost:9121/metrics > /dev/null; then
    echo -e "${GREEN}Redis Exporter is responding correctly${NC}"
else
    echo -e "${RED}Redis Exporter health check failed${NC}"
    docker compose logs redis_exporter
fi

# Postgres Exporter check
echo -e "\n${YELLOW}Testing Postgres Exporter...${NC}"
if curl -s -f http://localhost:9187/metrics > /dev/null; then
    echo -e "${GREEN}Postgres Exporter is responding correctly${NC}"
else
    echo -e "${RED}Postgres Exporter health check failed${NC}"
    docker compose logs postgres_exporter
fi

# Nginx Exporter check
echo -e "\n${YELLOW}Testing Nginx Exporter...${NC}"
if curl -s -f http://localhost:9113/metrics > /dev/null; then
    echo -e "${GREEN}Nginx Exporter is responding correctly${NC}"
else
    echo -e "${RED}Nginx Exporter health check failed${NC}"
    docker compose logs nginx_exporter
fi

# Prometheus check
echo -e "\n${YELLOW}Testing Prometheus...${NC}"
if curl -s -f http://localhost:9090/-/healthy > /dev/null; then
    echo -e "${GREEN}Prometheus is responding correctly${NC}"
else
    echo -e "${RED}Prometheus health check failed${NC}"
    docker compose logs prometheus
fi

# Grafana check
echo -e "\n${YELLOW}Testing Grafana...${NC}"
if curl -s -f http://localhost:3001/api/health > /dev/null; then
    echo -e "${GREEN}Grafana is responding correctly${NC}"
else
    echo -e "${RED}Grafana health check failed${NC}"
    docker compose logs grafana
fi

# Loki check
echo -e "\n${YELLOW}Testing Loki...${NC}"
if curl -s -f http://localhost:3100/ready > /dev/null; then
    echo -e "${GREEN}Loki is responding correctly${NC}"
else
    echo -e "${RED}Loki health check failed${NC}"
    docker compose logs loki
fi

# Start backend service
echo -e "\n${YELLOW}Building and starting backend service...${NC}"
docker compose up -d --build backend

# Start AI service
echo -e "\n${YELLOW}Building and starting AI service...${NC}"
docker compose up -d --build ai_service

# Start frontend service
echo -e "\n${YELLOW}Building and starting frontend service...${NC}"
docker compose up -d --build frontend

# Wait for frontend to be healthy
echo -e "\n${YELLOW}Waiting for frontend to be healthy...${NC}"
FRONTEND_HEALTHY=0
for i in {1..12}; do
    if curl -s -f http://localhost:3000 > /dev/null; then
        FRONTEND_HEALTHY=1
        break
    fi
    echo -e "${YELLOW}Waiting for frontend to become healthy... (${i}/12)${NC}"
    sleep 5
done
if [ $FRONTEND_HEALTHY -eq 1 ]; then
    echo -e "${GREEN}Frontend is responding correctly${NC}"
else
    echo -e "${RED}Frontend health check failed${NC}"
    docker compose logs frontend
    exit 1
fi

# Wait for backend to be healthy
BACKEND_HEALTHY=0
for i in {1..10}; do
    if curl -s -f http://localhost:8000/api/v1/healthz > /dev/null; then
        BACKEND_HEALTHY=1
        break
    fi
    echo -e "${YELLOW}Waiting for backend to become healthy... (${i}/10)${NC}"
    sleep 5
done
if [ $BACKEND_HEALTHY -eq 1 ]; then
    echo -e "${GREEN}Backend is responding correctly${NC}"
else
    echo -e "${RED}Backend health check failed${NC}"
    docker compose logs backend
    exit 1
fi

# Wait for AI service to be healthy
AI_SERVICE_HEALTHY=0
for i in {1..10}; do
    if curl -s -f http://localhost:8001/healthz > /dev/null; then
        AI_SERVICE_HEALTHY=1
        break
    fi
    echo -e "${YELLOW}Waiting for AI service to become healthy... (${i}/10)${NC}"
    sleep 5
done
if [ $AI_SERVICE_HEALTHY -eq 1 ]; then
    echo -e "${GREEN}AI service is responding correctly${NC}"
else
    echo -e "${RED}AI service health check failed${NC}"
    docker compose logs ai_service
    exit 1
fi

echo -e "\n${GREEN}Infrastructure setup completed successfully!${NC}"
echo -e "\n${YELLOW}All services are running:${NC}"
echo -e "- Core services (PostgreSQL, Redis, Keycloak)"
echo -e "- Application services (Backend, AI Service, Frontend)"
echo -e "- Monitoring (Redis Exporter, Postgres Exporter, Nginx Exporter, Prometheus, Grafana, Loki, Promtail)"
echo -e "\n${YELLOW}You can access:${NC}"
echo -e "- Frontend application at http://localhost:3000"
echo -e "- Backend API at http://localhost:8000/api/v1"
echo -e "- Keycloak admin at http://localhost:8080/admin"
echo -e "- Grafana at http://localhost:3001 (default credentials: admin/admin)"
echo -e "- Prometheus at http://localhost:9090"
echo -e "- Redis Exporter metrics at http://localhost:9121/metrics"
echo -e "- Postgres Exporter metrics at http://localhost:9187/metrics"
echo -e "- Nginx Exporter metrics at http://localhost:9113/metrics"
echo -e "- Loki at http://localhost:3100"
echo -e "\n${YELLOW}You can now proceed with the testing steps from the infrastructure_testing.md guide.${NC}" 