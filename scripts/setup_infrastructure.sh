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
mkdir -p redis/data
mkdir -p postgres/data

# Remove old data
rm -rf redis/data/*
rm -rf postgres/data/*

# Generate secrets
echo -e "\n${YELLOW}Generating secrets...${NC}"
echo -e "${GREEN}Generating PostgreSQL password...${NC}"
openssl rand -base64 32 > secrets/postgres_password.txt

echo -e "${GREEN}Generating Redis password...${NC}"
openssl rand -base64 32 > secrets/redis_password.txt

echo -e "${GREEN}Generating Keycloak admin password...${NC}"
openssl rand -base64 32 > secrets/keycloak_admin_password.txt

echo -e "${GREEN}Generating Keycloak client secret...${NC}"
openssl rand -base64 32 > secrets/keycloak_secret.txt

# Set proper permissions
echo -e "\n${YELLOW}Setting file permissions...${NC}"
chmod 600 secrets/*

# Generate SSL certificates
echo -e "\n${YELLOW}Generating SSL certificates...${NC}"
./scripts/generate_ssl_certs.sh

# Export passwords for docker-compose
export REDIS_PASSWORD=$(cat secrets/redis_password.txt)
export POSTGRES_PASSWORD=$(cat secrets/postgres_password.txt)
export KEYCLOAK_ADMIN_PASSWORD=$(cat secrets/keycloak_admin_password.txt)

# Start core services
echo -e "\n${YELLOW}Starting core services...${NC}"
docker compose up -d postgres redis keycloak

# Wait for services to be healthy
echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
timeout 300 bash -c 'until docker compose ps postgres redis keycloak | grep -q "healthy"; do echo "Waiting for services to be healthy..."; sleep 5; done'

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
if docker compose exec postgres pg_isready | grep -q "accepting connections"; then
    echo -e "${GREEN}PostgreSQL is responding correctly${NC}"
else
    echo -e "${RED}PostgreSQL health check failed${NC}"
    exit 1
fi

# Keycloak check
echo -e "\n${YELLOW}Testing Keycloak health endpoint...${NC}"
if curl -s -f http://localhost:8080/auth/health/ready > /dev/null; then
    echo -e "${GREEN}Keycloak is responding correctly${NC}"
else
    echo -e "${RED}Keycloak health check failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}Infrastructure setup completed successfully!${NC}"
echo -e "\n${YELLOW}Core services (PostgreSQL, Redis, Keycloak) are running.${NC}"
echo -e "${YELLOW}You can now proceed with the testing steps from the infrastructure_testing.md guide.${NC}" 