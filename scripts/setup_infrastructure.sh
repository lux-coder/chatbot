#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting infrastructure setup...${NC}"

# Clean up old containers and volumes
echo -e "\n${YELLOW}Cleaning up old containers and volumes...${NC}"
docker compose down -v

# Create necessary directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p secrets
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
echo -e "${GREEN}Generating PostgreSQL password...${NC}"
openssl rand -base64 32 > secrets/postgres_password.txt

echo -e "${GREEN}Generating Redis password...${NC}"
openssl rand -base64 32 > secrets/redis_password.txt

# Ensure admin password is not base64 for Keycloak direct use
echo -e "${GREEN}Generating Keycloak admin password (plain text)...${NC}"
openssl rand -hex 16 > secrets/keycloak_admin_password.txt # Generate a hex string for easier use

echo -e "${GREEN}Generating Keycloak client secret...${NC}"
openssl rand -base64 32 > secrets/keycloak_secret.txt

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

# Start core services
echo -e "\n${YELLOW}Starting core services...${NC}"
docker compose up -d postgres redis keycloak

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
echo -e "\n${YELLOW}Waiting additional time for Keycloak to fully initialize...${NC}"
sleep 60 # Keep this sleep as Keycloak might take longer after healthcheck reports ready
echo -e "\n${YELLOW}Testing Keycloak health endpoint...${NC}"
# Corrected Keycloak health check URL
if curl -s -f http://localhost:8080/health/ready > /dev/null; then
    echo -e "${GREEN}Keycloak is responding correctly${NC}"
else
    echo -e "${RED}Keycloak health check failed${NC}"
    docker compose logs keycloak # Output Keycloak logs on failure
    exit 1
fi

# Start monitoring services
echo -e "\n${YELLOW}Starting monitoring services...${NC}"
docker compose up -d redis_exporter prometheus grafana loki promtail

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

echo -e "\n${GREEN}Infrastructure setup completed successfully!${NC}"
echo -e "\n${YELLOW}All services are running:${NC}"
echo -e "- Core services (PostgreSQL, Redis, Keycloak)"
echo -e "- Monitoring (Redis Exporter, Prometheus, Grafana, Loki, Promtail)"
echo -e "\n${YELLOW}You can access:${NC}"
echo -e "- Grafana at http://localhost:3001 (default credentials: admin/admin)"
echo -e "- Prometheus at http://localhost:9090"
echo -e "- Redis Exporter metrics at http://localhost:9121/metrics"
echo -e "- Loki at http://localhost:3100"
echo -e "\n${YELLOW}You can now proceed with the testing steps from the infrastructure_testing.md guide.${NC}" 