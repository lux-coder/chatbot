# Use the official Keycloak image
FROM quay.io/keycloak/keycloak:25.0 as builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true \
    KC_METRICS_ENABLED=true \
    KC_FEATURES=token-exchange,admin-fine-grained-authz,web-authn \
    KC_DB=postgres \
    KC_HTTP_ENABLED=true \
    KC_HOSTNAME_STRICT=false \
    KC_HOSTNAME_STRICT_HTTPS=false \
    KC_PROXY=edge \
    KC_HTTP_RELATIVE_PATH=/

# Copy configuration and realm
COPY conf/keycloak.conf /opt/keycloak/conf/keycloak.conf
COPY conf/realm_chatbot.json /opt/keycloak/data/import/realm_chatbot.json

# Build optimized version
RUN /opt/keycloak/bin/kc.sh build

# Create final image
FROM quay.io/keycloak/keycloak:25.0

# Copy built Keycloak, configuration and realm
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Expose ports
EXPOSE 8080
EXPOSE 8443
EXPOSE 9000

# Optional: Replace this with bash or wget-based healthcheck, or remove
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD bash -c "exec 3<>/dev/tcp/localhost/9000"

# Start Keycloak with realm import
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
CMD ["start", "--optimized", "--import-realm"]
