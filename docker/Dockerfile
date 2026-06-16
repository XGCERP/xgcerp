# AXERP Production Dockerfile
# Base: frappe/erpnext:<ERPNEXT_VERSION> (arm64 + amd64 multi-arch)
# To bump: change ERPNEXT_VERSION, run sync_upstream.sh, rebuild.
#
# Build:
#   docker build -f docker/Dockerfile -t axerp:v16.22.0-axerp.2 -t axerp:prod .
#   # On EC2 (arm64):
#   docker build --platform linux/arm64 -f docker/Dockerfile -t axerp:prod .

ARG ERPNEXT_VERSION=v16.22.0
FROM frappe/erpnext:${ERPNEXT_VERSION} AS builder

USER root

# Copy AXERP code (rebranded fork) over the upstream erpnext app
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/erpnext

USER frappe
WORKDIR /home/frappe/frappe-bench

# Reinstall app to pick up any Python dependency changes in pyproject.toml
RUN pip install --no-cache-dir -e apps/erpnext 2>/dev/null || true

# Rebuild frontend assets with AXERP branding (logos, strings)
RUN bench build --app erpnext 2>/dev/null || true

FROM builder AS final
LABEL org.opencontainers.image.title="AXERP" \
      org.opencontainers.image.description="Operating System for Carbon Sovereignty" \
      org.opencontainers.image.vendor="Axina Group Inc." \
      org.opencontainers.image.source="https://github.com/axinagroup/axerp" \
      org.opencontainers.image.version="${ERPNEXT_VERSION}"
