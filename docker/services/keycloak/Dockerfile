# Use the official Keycloak image
FROM quay.io/keycloak/keycloak:22.0 as builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true \
    KC_METRICS_ENABLED=true \
    KC_FEATURES=token-exchange,admin-fine-grained-authz,declarative-user-profile \
    KC_DB=postgres \
    KC_HTTP_ENABLED=true \
    KC_HOSTNAME_STRICT=false \
    KC_HOSTNAME_STRICT_HTTPS=false \
    KC_PROXY=edge \
    KC_HTTP_RELATIVE_PATH=/

# Build optimized version
RUN /opt/keycloak/bin/kc.sh build

# Create final image
FROM quay.io/keycloak/keycloak:22.0

# Copy built Keycloak
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Install curl for healthcheck
USER root
RUN set -e; \
    if ! command -v curl >/dev/null 2>&1; then \
        if command -v microdnf >/dev/null 2>&1; then \
            microdnf install -y curl && microdnf clean all; \
        elif command -v dnf >/dev/null 2>&1; then \
            dnf install -y curl && dnf clean all; \
        elif command -v apt-get >/dev/null 2>&1; then \
            apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*; \
        elif command -v apk >/dev/null 2>&1; then \
            apk add --no-cache curl; \
        else \
            echo "No supported package manager found and curl not installed" && exit 1; \
        fi; \
    fi && \
    command -v curl >/dev/null 2>&1
USER 1000

# Expose ports
EXPOSE 8080
EXPOSE 8443

# Health check using curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health/ready || exit 1

# Start Keycloak
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
CMD ["start", "--optimized"] 