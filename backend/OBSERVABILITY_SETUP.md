# Observability Setup Guide

This guide covers setting up comprehensive logging and monitoring for the chatbot backend using Promtail + Loki + Grafana.

## Overview

The observability stack consists of:

- **Application**: Structured JSON logging with contextual information
- **Promtail**: Log collection and forwarding to Loki
- **Loki**: Log aggregation and storage
- **Grafana**: Visualization and alerting

## Architecture

```
┌─────────────────┐    ┌─────────────┐    ┌──────────┐    ┌─────────────┐
│   Application   │───▶│  Promtail   │───▶│   Loki   │───▶│   Grafana   │
│  (JSON Logs)    │    │ (Collector) │    │ (Storage)│    │ (Dashboard) │
└─────────────────┘    └─────────────┘    └──────────┘    └─────────────┘
```

## Application Logging

### Log Structure

All logs follow a consistent JSON structure:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "app.services.chat",
  "message": "prompt_filtering_start",
  "event_category": "chat",
  "event_type": "prompt_filtering_start",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "tenant_id": "789e0123-e89b-12d3-a456-426614174000",
  "request_id": "req_abc123",
  "processing_time_ms": 125.5
}
```

### Environment Variables

Add these to your `.env` file:

```bash
# Logging Configuration
LOG_LEVEL=INFO
SERVICE_NAME=chatbot-backend
ENVIRONMENT=production
APP_VERSION=1.0.0
```

## Docker Compose Configuration

### Complete Stack Setup

Create `docker-compose.observability.yml`:

```yaml
version: '3.8'

services:
  # Loki - Log aggregation
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./config/loki.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - observability

  # Promtail - Log collection
  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - ./config/promtail.yml:/etc/promtail/config.yml
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - observability

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/datasources:/etc/grafana/provisioning/datasources
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - loki
    networks:
      - observability

volumes:
  loki_data:
  grafana_data:

networks:
  observability:
    driver: bridge
```

## Configuration Files

### Loki Configuration

Create `config/loki.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

# Frontend
frontend:
  encoding: snappy

# Limits
limits_config:
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 32
  max_query_series: 100000
  max_query_parallelism: 32

# Compactor
compactor:
  working_directory: /loki/boltdb-shipper-compactor
  shared_store: filesystem
```

### Promtail Configuration

Create `config/promtail.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Chatbot backend logs
  - job_name: chatbot-backend
    static_configs:
      - targets:
          - localhost
        labels:
          job: chatbot-backend
          service: chatbot-backend
          __path__: /app/logs/*.log
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            logger: logger
            message: message
            event_category: event_category
            event_type: event_type
            user_id: user_id
            tenant_id: tenant_id
            request_id: request_id
      - labels:
          level:
          logger:
          event_category:
          event_type:
          service:
      - timestamp:
          source: timestamp
          format: RFC3339Nano

  # Docker container logs
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*.log
    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            attrs:
      - json:
          expressions:
            tag:
          source: attrs
      - regex:
          expression: (?P<container_name>(?:[^|]*))\|
          source: tag
      - timestamp:
          source: time
          format: RFC3339Nano
      - labels:
          stream:
          container_name:
      - output:
          source: output
```

### Grafana Data Source

Create `config/grafana/datasources/loki.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: true
    jsonData:
      maxLines: 1000
    editable: true
```

## Useful LogQL Queries

### Basic Queries

```logql
# All logs from chatbot backend
{service="chatbot-backend"}

# Error logs only
{service="chatbot-backend"} |= "ERROR"

# Chat events
{service="chatbot-backend", event_category="chat"}

# Security events
{service="chatbot-backend", event_category="security"}

# Specific user's activities
{service="chatbot-backend"} | json | user_id="123e4567-e89b-12d3-a456-426614174000"
```

### Advanced Queries

```logql
# Prompt filtering events
{service="chatbot-backend"} | json | event_type=~"prompt_.*"

# Slow requests (>1000ms)
{service="chatbot-backend"} | json | processing_time_ms > 1000

# Failed operations
{service="chatbot-backend"} | json | success="false"

# Authentication failures by IP
{service="chatbot-backend", event_category="security"} | json | event_type="AUTHENTICATION_FAILURE" | line_format "{{.client_ip}}"

# Error rate over time
rate({service="chatbot-backend"} |= "ERROR"[5m])

# Request duration percentiles
quantile_over_time(0.95, {service="chatbot-backend"} | json | unwrap processing_time_ms [5m])
```

### Metrics Queries

```logql
# Request rate by endpoint
sum(rate({service="chatbot-backend", event_category="api"}[5m])) by (endpoint)

# Error rate by tenant
sum(rate({service="chatbot-backend"} |= "ERROR"[5m])) by (tenant_id)

# Average response time
avg_over_time({service="chatbot-backend"} | json | unwrap processing_time_ms [5m])

# Security alerts count
count_over_time({service="chatbot-backend", event_category="security"}[1h])
```

## Grafana Dashboard Examples

### API Performance Dashboard

```json
{
  "dashboard": {
    "title": "Chatbot API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate({service=\"chatbot-backend\", event_category=\"api\"}[5m]))",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time (95th percentile)",
        "type": "stat",
        "targets": [
          {
            "expr": "quantile_over_time(0.95, {service=\"chatbot-backend\"} | json | unwrap processing_time_ms [5m])",
            "legendFormat": "P95 (ms)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate({service=\"chatbot-backend\"} |= \"ERROR\"[5m])) / sum(rate({service=\"chatbot-backend\"}[5m]))",
            "legendFormat": "Error Rate %"
          }
        ]
      }
    ]
  }
}
```

### Security Monitoring Dashboard

```json
{
  "dashboard": {
    "title": "Security Monitoring",
    "panels": [
      {
        "title": "Blocked Prompts",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate({service=\"chatbot-backend\"} | json | event_type=~\"prompt_blocked_.*\"[5m])) by (event_type)",
            "legendFormat": "{{event_type}}"
          }
        ]
      },
      {
        "title": "Authentication Failures",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, sum by (client_ip) (count_over_time({service=\"chatbot-backend\", event_category=\"security\"} | json | event_type=\"AUTHENTICATION_FAILURE\"[1h])))",
            "legendFormat": "{{client_ip}}"
          }
        ]
      },
      {
        "title": "Security Alerts by Severity",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (severity) (count_over_time({service=\"chatbot-backend\", event_category=\"security\"}[24h]))",
            "legendFormat": "{{severity}}"
          }
        ]
      }
    ]
  }
}
```

## Alerting Rules

### Grafana Alert Rules

1. **High Error Rate**
```yaml
- alert: HighErrorRate
  expr: sum(rate({service="chatbot-backend"} |= "ERROR"[5m])) / sum(rate({service="chatbot-backend"}[5m])) > 0.05
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }}% over the last 5 minutes"
```

2. **Slow Response Time**
```yaml
- alert: SlowResponseTime
  expr: quantile_over_time(0.95, {service="chatbot-backend"} | json | unwrap processing_time_ms [5m]) > 5000
  for: 3m
  labels:
    severity: warning
  annotations:
    summary: "Slow response time detected"
    description: "95th percentile response time is {{ $value }}ms"
```

3. **Security Alert**
```yaml
- alert: SecurityIncident
  expr: increase({service="chatbot-backend", event_category="security"}[5m]) > 10
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Multiple security events detected"
    description: "{{ $value }} security events in the last 5 minutes"
```

## Log Retention

Configure log retention in Loki:

```yaml
# In loki.yml
table_manager:
  retention_deletes_enabled: true
  retention_period: 168h  # 7 days
```

## Performance Tuning

### Loki Optimization

1. **Adjust limits based on volume**:
```yaml
limits_config:
  ingestion_rate_mb: 32
  ingestion_burst_size_mb: 64
  max_query_series: 500000
```

2. **Use chunk caching**:
```yaml
chunk_store_config:
  chunk_cache_config:
    embedded_cache:
      enabled: true
      max_size_mb: 1024
```

### Promtail Optimization

1. **Batch configuration**:
```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
    batchwait: 1s
    batchsize: 1048576  # 1MB
```

## Deployment

### Production Deployment

1. **Start the observability stack**:
```bash
docker-compose -f docker-compose.observability.yml up -d
```

2. **Verify services**:
```bash
# Check Loki
curl http://localhost:3100/ready

# Check Promtail
curl http://localhost:9080/ready

# Access Grafana
open http://localhost:3000
```

3. **Configure log rotation**:
```bash
# Add to /etc/logrotate.d/chatbot-backend
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    copytruncate
    notifempty
}
```

## Maintenance

### Regular Tasks

1. **Monitor disk usage**
2. **Review alert rules**
3. **Update retention policies**
4. **Backup Grafana dashboards**
5. **Review log patterns for optimization**

### Troubleshooting

1. **Check Promtail positions**:
```bash
cat /tmp/positions.yaml
```

2. **Verify Loki ingestion**:
```bash
curl http://localhost:3100/loki/api/v1/label
```

3. **Test LogQL queries**:
```bash
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={service="chatbot-backend"}' \
  --data-urlencode 'limit=10'
```

## Best Practices

1. **Use structured logging consistently**
2. **Include contextual information (user_id, tenant_id, request_id)**
3. **Monitor log volume and adjust retention**
4. **Create alerts for critical events**
5. **Use appropriate log levels**
6. **Avoid logging sensitive information**
7. **Regular review and optimization of queries** 