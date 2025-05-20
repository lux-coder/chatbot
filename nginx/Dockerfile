# Use Alpine Linux for smaller footprint
FROM alpine:3.19 as builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    g++ \
    libc-dev \
    make \
    openssl-dev \
    pcre-dev \
    pcre2-dev \
    zlib-dev \
    linux-headers \
    curl \
    gnupg \
    libxslt-dev \
    gd-dev \
    geoip-dev \
    perl-dev \
    git \
    autoconf \
    automake \
    libtool \
    byacc \
    flex

# Download and verify ModSecurity source
WORKDIR /usr/src
RUN git clone --depth 1 -b v3/master --single-branch https://github.com/SpiderLabs/ModSecurity
WORKDIR /usr/src/ModSecurity
RUN git submodule init && git submodule update && \
    ./build.sh && \
    ./configure && \
    make && \
    make install

# Download and compile Nginx with ModSecurity
WORKDIR /usr/src
ENV NGINX_VERSION=1.24.0
RUN wget https://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz && \
    tar zxvf nginx-${NGINX_VERSION}.tar.gz

# Download and compile ModSecurity-nginx connector
RUN git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

WORKDIR /usr/src/nginx-${NGINX_VERSION}
RUN ./configure \
    --prefix=/etc/nginx \
    --sbin-path=/usr/sbin/nginx \
    --modules-path=/usr/lib/nginx/modules \
    --conf-path=/etc/nginx/nginx.conf \
    --error-log-path=/var/log/nginx/error.log \
    --http-log-path=/var/log/nginx/access.log \
    --pid-path=/var/run/nginx.pid \
    --lock-path=/var/run/nginx.lock \
    --http-client-body-temp-path=/var/cache/nginx/client_temp \
    --http-proxy-temp-path=/var/cache/nginx/proxy_temp \
    --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp \
    --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp \
    --http-scgi-temp-path=/var/cache/nginx/scgi_temp \
    --with-perl_modules_path=/usr/lib/perl5/vendor_perl \
    --user=nginx \
    --group=nginx \
    --with-compat \
    --with-file-aio \
    --with-threads \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_mp4_module \
    --with-http_random_index_module \
    --with-http_realip_module \
    --with-http_secure_link_module \
    --with-http_slice_module \
    --with-http_ssl_module \
    --with-http_stub_status_module \
    --with-http_sub_module \
    --with-http_v2_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-stream \
    --with-stream_realip_module \
    --with-stream_ssl_module \
    --with-stream_ssl_preread_module \
    --add-dynamic-module=/usr/src/ModSecurity-nginx \
    && make && make install

# Create final image
FROM alpine:3.19

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    libcurl \
    libgcc \
    libstdc++ \
    luajit \
    pcre \
    yajl \
    zlib \
    geoip \
    libxml2 \
    libxslt \
    gd \
    perl \
    tzdata

# Copy built artifacts from builder
COPY --from=builder /usr/local/modsecurity/ /usr/local/modsecurity/
COPY --from=builder /usr/lib/nginx/modules/ /usr/lib/nginx/modules/
COPY --from=builder /usr/sbin/nginx /usr/sbin/nginx
COPY --from=builder /etc/nginx /etc/nginx
COPY --from=builder /var/log/nginx /var/log/nginx

# Create nginx user/group
RUN addgroup -S nginx && \
    adduser -D -S -h /var/cache/nginx -s /sbin/nologin -G nginx nginx && \
    mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx

# Create necessary directories
RUN mkdir -p /etc/nginx/conf.d && \
    mkdir -p /usr/share/nginx/html && \
    mkdir -p /var/log/nginx && \
    mkdir -p /var/cache/nginx && \
    mkdir -p /etc/nginx/waf

# Download OWASP ModSecurity Core Rule Set
WORKDIR /etc/nginx/waf
RUN wget https://github.com/coreruleset/coreruleset/archive/v3.3.5.tar.gz && \
    tar xvf v3.3.5.tar.gz && \
    mv coreruleset-3.3.5 owasp-crs && \
    cp owasp-crs/crs-setup.conf.example owasp-crs/crs-setup.conf && \
    rm v3.3.5.tar.gz

# Copy ModSecurity configuration
COPY waf/modsecurity.conf /etc/nginx/waf/
COPY waf/crs-setup.conf /etc/nginx/waf/owasp-crs/
COPY waf/rules/ /etc/nginx/waf/rules/

# Set proper permissions
RUN chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/waf && \
    chmod -R 644 /etc/nginx/waf

# Forward request and error logs to Docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# Expose ports
EXPOSE 80 443

# Switch to non-root user
USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/healthz || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 