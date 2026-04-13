# XGCERP Local Test Build
# Builds a custom ERPNext image with the local XGCERP codebase
FROM frappe/erpnext:v16.13.3 AS base

USER root

# Copy local XGCERP code over the upstream erpnext app
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/erpnext

USER frappe
WORKDIR /home/frappe/frappe-bench

# Reinstall the app to pick up any dependency changes
RUN pip install --no-cache-dir -e apps/erpnext 2>/dev/null || true

# Rebuild frontend assets with XGCERP branding
RUN bench build --app erpnext 2>/dev/null || true
