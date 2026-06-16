# AXERP Production Dockerfile
# Base: frappe/erpnext:<ERPNEXT_VERSION> (arm64 + amd64 multi-arch)
# Bundled apps: frappe/hrms@HRMS_VERSION, frappe/crm@CRM_VERSION
# To bump ERPNext: change ERPNEXT_VERSION, run sync_upstream.sh, rebuild.
# To bump HRMS/CRM: change the ARGs below, rebuild.
#
# Build:
#   # On EC2 (arm64):
#   docker build --platform linux/arm64 -f docker/Dockerfile \
#     -t axerp:v16.23.0-axerp.1 -t axerp:prod .

ARG ERPNEXT_VERSION=v16.23.0
ARG HRMS_VERSION=version-16
ARG CRM_VERSION=main

FROM frappe/erpnext:${ERPNEXT_VERSION} AS builder

USER root

# ── HRMS ──────────────────────────────────────────────────────────────────
RUN git clone --depth 1 --branch ${HRMS_VERSION} \
      https://github.com/frappe/hrms.git \
      /home/frappe/frappe-bench/apps/hrms \
    && chown -R frappe:frappe /home/frappe/frappe-bench/apps/hrms

# ── CRM ───────────────────────────────────────────────────────────────────
RUN git clone --depth 1 --branch ${CRM_VERSION} \
      https://github.com/frappe/crm.git \
      /home/frappe/frappe-bench/apps/crm \
    && chown -R frappe:frappe /home/frappe/frappe-bench/apps/crm

# ── AXERP (rebranded ERPNext) ──────────────────────────────────────────────
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/erpnext

USER frappe
WORKDIR /home/frappe/frappe-bench

# Install all three apps and rebuild assets
RUN pip install --no-cache-dir \
      -e apps/erpnext \
      -e apps/hrms \
      -e apps/crm \
    2>/dev/null || true

RUN bench build --app erpnext 2>/dev/null || true
RUN bench build --app hrms    2>/dev/null || true
RUN bench build --app crm     2>/dev/null || true

FROM builder AS final
LABEL org.opencontainers.image.title="AXERP" \
      org.opencontainers.image.description="Operating System for Carbon Sovereignty" \
      org.opencontainers.image.vendor="Axina Group Inc." \
      org.opencontainers.image.source="https://github.com/axinagroup/axerp" \
      org.opencontainers.image.version="${ERPNEXT_VERSION}"
