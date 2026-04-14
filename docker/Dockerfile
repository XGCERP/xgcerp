# AXERP Local Test Build
# Builds a custom ERPNext image with the local AXERP codebase

# Stage 1: Build with the upstream base
FROM frappe/erpnext:v16.13.3 AS builder

USER root

# Copy local AXERP code over the upstream erpnext app
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/erpnext

USER frappe
WORKDIR /home/frappe/frappe-bench

# Reinstall the app to pick up any dependency changes
RUN pip install --no-cache-dir -e apps/erpnext 2>/dev/null || true

# Rebuild frontend assets with AXERP branding
RUN bench build --app erpnext 2>/dev/null || true

# Stage 2: Final image without the intermediate base tag lingering
FROM builder AS final
LABEL org.opencontainers.image.title="AXERP" \
      org.opencontainers.image.description="AXERP local development image"
