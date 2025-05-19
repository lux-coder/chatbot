# Infrastructure Testing Plan

## Prerequisites
- Docker and Docker Compose installed
- curl installed for HTTP requests
- openssl for certificate verification
- redis-cli for Redis testing

## 1. Initial Setup

### 1.1 Generate Required Secrets
```bash
# Create secrets directory if it doesn't exist
mkdir -p secrets

# Generate random passwords for services
openssl rand -base64 32 > secrets/postgres_password.txt
openssl rand -base64 32 > secrets/redis_password.txt
openssl rand -base64 32 > secrets/keycloak_admin_password.txt
openssl rand -base64 32 > secrets/keycloak_secret.txt
```

### 1.2 Generate SSL Certificates
```bash
# Generate SSL certificates for development
./scripts/generate_ssl_certs.sh
```

## 2. Starting Services

### 2.1 Start Core Infrastructure
```bash
# Start only infrastructure services first
docker compose up -d postgres redis keycloak nginx
```

### 2.2 Verify Service Status
```bash
# Check if all containers are running
docker compose ps

# Check logs for any errors
docker compose logs
```

## 3. Testing Individual Components

### 3.1 Redis Testing
```bash
# Get Redis password from secrets
REDIS_PASSWORD=$(cat secrets/redis_password.txt)

# Test Redis connection
redis-cli -a "$REDIS_PASSWORD" ping  # Should return PONG

# Test Redis write/read
redis-cli -a "$REDIS_PASSWORD" set test "Hello World"
redis-cli -a "$REDIS_PASSWORD" get test  # Should return "Hello World"

# Test Redis persistence
redis-cli -a "$REDIS_PASSWORD" save  # Should create dump.rdb

# Verify memory limits
redis-cli -a "$REDIS_PASSWORD" info memory  # Check maxmemory setting

# Test disabled commands
redis-cli -a "$REDIS_PASSWORD" flushall  # Should return error
```

### 3.2 Keycloak Testing
```bash
# Get Keycloak admin password
KEYCLOAK_ADMIN_PASSWORD=$(cat secrets/keycloak_admin_password.txt)

# Test Keycloak health endpoint
curl http://localhost:8080/health

# Test Keycloak metrics endpoint
curl http://localhost:8080/metrics

# Test Keycloak admin console access
curl -I http://localhost:8080/admin/  # Should redirect to login

# Get access token (replace realm and client values)
curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password"
```

### 3.3 Nginx Testing
```bash
# Test HTTP to HTTPS redirect
curl -I http://localhost  # Should return 301 to HTTPS

# Test HTTPS connection
curl -k https://localhost  # -k flag for self-signed cert

# Verify SSL certificate
openssl s_client -connect localhost:443 -servername localhost

# Test security headers
curl -k -I https://localhost | grep -E "Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options"

# Test WAF rules
# Should be blocked:
curl -k "https://localhost/?q=<script>alert(1)</script>"
curl -k "https://localhost/?q=1' OR '1'='1"
```

## 4. Integration Testing

### 4.1 End-to-End Authentication Flow
1. Start all services:
```bash
docker compose up -d
```

2. Create test realm and client in Keycloak:
```bash
# Get access token first
TOKEN=$(curl -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
  -d "grant_type=password" | jq -r .access_token)

# Create test realm
curl -X POST http://localhost:8080/admin/realms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"realm": "test", "enabled": true}'

# Create test client
curl -X POST http://localhost:8080/admin/realms/test/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"clientId": "test-client", "enabled": true, "publicClient": true, "redirectUris": ["*"]}'
```

3. Test authentication flow:
```bash
# Get login page
curl -k https://localhost/auth/realms/test/protocol/openid-connect/auth \
  -d "client_id=test-client" \
  -d "response_type=code" \
  -d "redirect_uri=http://localhost:3000"
```

### 4.2 Session Management Testing
1. Test Redis session storage:
```bash
# Create test session
redis-cli -a "$REDIS_PASSWORD" hset "session:test" "user" "testuser"

# Verify session
redis-cli -a "$REDIS_PASSWORD" hget "session:test" "user"

# Test session expiration
redis-cli -a "$REDIS_PASSWORD" expire "session:test" 60
```

## 5. Monitoring and Logging

### 5.1 Check Service Logs
```bash
# Check individual service logs
docker compose logs redis
docker compose logs keycloak
docker compose logs nginx

# Follow logs in real-time
docker compose logs -f
```

### 5.2 Check Metrics
```bash
# Redis metrics
redis-cli -a "$REDIS_PASSWORD" info stats
redis-cli -a "$REDIS_PASSWORD" info memory

# Keycloak metrics
curl http://localhost:8080/metrics

# Nginx metrics (if configured)
curl http://localhost/nginx_status
```

## 6. Cleanup
```bash
# Stop all services
docker compose down

# Remove volumes if needed
docker compose down -v

# Remove generated certificates and secrets (if needed)
rm -rf nginx/certs/*
rm -rf secrets/*
```

## 7. Common Issues and Troubleshooting

### 7.1 Redis Issues
- Check Redis logs: `docker compose logs redis`
- Verify password is being read correctly
- Check memory usage and limits
- Verify persistence directory permissions

### 7.2 Keycloak Issues
- Check Keycloak logs: `docker compose logs keycloak`
- Verify database connection
- Check realm and client configuration
- Verify admin credentials

### 7.3 Nginx Issues
- Check Nginx logs: `docker compose logs nginx`
- Verify SSL certificate paths and permissions
- Check WAF configuration
- Verify upstream service connectivity 