# AXERP Production Dockerfile
# Base: frappe/erpnext:<ERPNEXT_VERSION> (arm64 + amd64 multi-arch)
# Bundled apps:
#   frappe/hrms        @ HRMS_VERSION    (HR, Payroll, Leave, Expenses)
#   frappe/crm         @ CRM_VERSION     (Sales CRM)
#   frappe/insights    @ INSIGHTS_VERSION (Analytics — develop branch for v16 support)
#
# Build:
#   docker build --platform linux/arm64 -f docker/Dockerfile \
#     -t axerp:v16.23.0-axerp.2 -t axerp:prod .

ARG ERPNEXT_VERSION=v16.23.0
ARG HRMS_VERSION=version-16
ARG CRM_VERSION=main
# insights version-3 is frappe 14/15 only; develop branch has explicit v16 CI
ARG INSIGHTS_VERSION=develop

FROM frappe/erpnext:${ERPNEXT_VERSION} AS builder

# Re-declare ARGs after FROM — Docker ARGs before FROM are out of scope
# inside a build stage unless explicitly re-declared (no default = inherits global)
ARG HRMS_VERSION
ARG CRM_VERSION
ARG INSIGHTS_VERSION

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

# ── Insights (develop = v16-compatible) ───────────────────────────────────
RUN git clone --depth 1 --branch ${INSIGHTS_VERSION} \
      https://github.com/frappe/insights.git \
      /home/frappe/frappe-bench/apps/insights \
    && chown -R frappe:frappe /home/frappe/frappe-bench/apps/insights

# ── AXERP (rebranded ERPNext) ──────────────────────────────────────────────
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/apps/erpnext

USER frappe
WORKDIR /home/frappe/frappe-bench

# Install into the bench virtualenv explicitly.
# Plain `pip` resolves to ~/.local/bin/pip (user packages), which bench's
# virtualenv can't see. env/bin/pip installs into the venv's site-packages.
RUN env/bin/pip install --no-cache-dir -e apps/erpnext
RUN env/bin/pip install --no-cache-dir -e apps/hrms
RUN env/bin/pip install --no-cache-dir -e apps/crm
RUN env/bin/pip install --no-cache-dir -e apps/insights

# Build frontend assets for all apps.
# bench build compiles JS/CSS bundles via Node. Failures are non-fatal
# (some apps have no bundle; frontend is also rebuilt at container runtime).
RUN bench build --app erpnext  2>/dev/null || true
RUN bench build --app hrms     2>/dev/null || true
RUN bench build --app crm      2>/dev/null || true
RUN bench build --app insights 2>/dev/null || true

FROM builder AS final
LABEL org.opencontainers.image.title="AXERP" \
      org.opencontainers.image.description="Operating System for Carbon Sovereignty" \
      org.opencontainers.image.vendor="Axina Group Inc." \
      org.opencontainers.image.source="https://github.com/axinagroup/axerp" \
      org.opencontainers.image.version="${ERPNEXT_VERSION}"
