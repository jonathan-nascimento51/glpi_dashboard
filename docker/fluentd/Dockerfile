# GLPI Dashboard Fluentd Docker Image
# ===================================

FROM fluent/fluentd:v1.16-debian-1

# Switch to root to install packages
USER root

# Install required packages and plugins
RUN apt-get update && apt-get install -y \
    build-essential \
    ruby-dev \
    libgeoip-dev \
    geoip-database \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Fluentd plugins
RUN gem install \
    fluent-plugin-elasticsearch \
    fluent-plugin-geoip \
    fluent-plugin-record-transformer \
    fluent-plugin-grep \
    fluent-plugin-sampling \
    fluent-plugin-prometheus \
    fluent-plugin-systemd \
    fluent-plugin-kubernetes_metadata_filter \
    fluent-plugin-multi-format-parser \
    fluent-plugin-detect-exceptions \
    fluent-plugin-concat \
    fluent-plugin-rewrite-tag-filter

# Create necessary directories
RUN mkdir -p \
    /var/log/fluentd-buffers \
    /var/log/fluentd-output \
    /var/log/fluentd-positions \
    /var/log/nginx \
    /var/log/backend \
    /var/log/redis

# Set proper permissions
RUN chown -R fluent:fluent \
    /var/log/fluentd-buffers \
    /var/log/fluentd-output \
    /var/log/fluentd-positions \
    /var/log/nginx \
    /var/log/backend \
    /var/log/redis

# Copy configuration
COPY fluent.conf /fluentd/etc/fluent.conf
RUN chown fluent:fluent /fluentd/etc/fluent.conf

# Create entrypoint script
RUN cat > /fluentd/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

# Create directories if they don't exist
mkdir -p /var/log/fluentd-buffers
mkdir -p /var/log/fluentd-output
mkdir -p /var/log/fluentd-positions

# Set proper permissions
chown -R fluent:fluent /var/log/fluentd-buffers
chown -R fluent:fluent /var/log/fluentd-output
chown -R fluent:fluent /var/log/fluentd-positions

# Switch to fluent user and start fluentd
exec gosu fluent fluentd -c /fluentd/etc/fluent.conf -v
EOF

RUN chmod +x /fluentd/entrypoint.sh

# Install gosu for proper user switching
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:24220/api/plugins.json || exit 1

# Expose ports
EXPOSE 24224 24220

# Set environment variables
ENV FLUENTD_CONF="fluent.conf"
ENV FLUENTD_OPT=""
ENV FLUENTD_SYSTEMD_CONF="disable"

# Use custom entrypoint
ENTRYPOINT ["/fluentd/entrypoint.sh"]