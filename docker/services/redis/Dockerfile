# Use the official Redis image with Alpine Linux for a smaller footprint
FROM redis:7.2-alpine

# Add tini for proper signal handling
RUN apk add --no-cache tini

# Create data directory and set permissions
RUN mkdir -p /data && chown redis:redis /data

# Expose Redis port
EXPOSE 6379

# Set working directory
WORKDIR /data

# Switch to non-root user
USER redis

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--"]

# Start Redis
CMD ["redis-server"]

# Add healthcheck
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD redis-cli ping || exit 1 