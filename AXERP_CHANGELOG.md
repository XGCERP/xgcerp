# AXERP Changelog

This file tracks AXERP-specific changes layered on top of the upstream AXERP fork.
Format: `[version-tag] — upstream-base | date | author`

For upstream AXERP release notes see: https://github.com/frappe/erpnext/releases

---

## [v16.23.0-axerp.3] — upstream: v16.23.0 | 2026-06-17 | Daniel Brody

### Fixed — Asset pipeline, blank desktop, and socket.io

**All assets 200, socket.io 200, desktop loads correctly.**

#### Root causes resolved

**1. Asset pipeline (404s / MIME type errors for all .bundle.css/js)**

The frappe_docker `entrypoint.sh` runs on every container start:
```bash
rm -rf sites/assets && ln -s /home/frappe/frappe-bench/assets sites/assets
```
`BAKED_PATH=/home/frappe/frappe-bench/assets` is the canonical asset directory — not
`sites/assets/`. Previous builds wrote assets to `sites/assets/` which the entrypoint
then deleted. Fixed by baking all app `public/` dirs into `BAKED_PATH` at image build time.

Additional Dockerfile fixes required:
- `yarn add html2canvas` in `apps/hrms` before bench build (undeclared dependency in hrms package.json)
- Stub `sites/common_site_config.json` before bench build (hrms Vite imports `socketio_port` from it at build time)
- Removed `|| true` suppression from all `bench build` steps (was hiding failures)

**2. Post-deploy assets.json mismatch**

After `docker compose up -d`, `bench build --app frappe` runs on the live backend and
regenerates `assets.json` with new hashes in the backend's writable layer. The frontend
container still has the image-baked version → hash mismatch → 404s.

Fix: after every redeploy, sync frappe/dist + assets.json from backend to frontend:
```bash
bash /tmp/axerp-fix-assets-json.sh  # on S3: axina-openproject-files/deploy/
```

**3. Blank desktop after login**

Three issues in the DB from failed setup wizard runs:
- `common_site_config.json` had `db_type: postgres` (stale) → removed
- `System Settings.setup_complete = 0` → set to 1 via SQL on `tabSingles`
- Default company was `TGI Solar Power Group Inc. (Demo)` → corrected to `Axina Group Inc.`

**Dockerfile changes:**
```
+ yarn add html2canvas before hrms build
+ stub common_site_config.json before bench build
+ removed || true from bench build steps
+ bake all app public/ dirs into BAKED_PATH (/home/frappe/frappe-bench/assets)
+ assets.json + assets-rtl.json copied to BAKED_PATH
```

**docker-compose.axerp.yml changes:**
```
+ logging limits: json-file 10m×3 on all services
+ deploy.resources.limits: backend 2g, queue-long 1g, queue-short 512m
- removed axerp-assets named volume (conflicted with entrypoint, caused crash loop)
- removed --remove-orphans from deploy (was stopping OpenProject/Nextcloud)
```

**HTTP verification (2026-06-17, all 60 assets from public internet):**
- `login.bundle.css`, `desk.bundle.css`, `website.bundle.css` → **200**
- `libs.bundle.js`, `desk.bundle.js`, `frappe-web.bundle.js` → **200**
- `hrms.bundle.css`, `hrms.bundle.js` → **200**
- `erpnext.bundle.js`, `erpnext.bundle.css` → **200**
- `crm/frontend/assets/*.css` and `*.js` → **200**
- `insights/frontend/assets/*.css` and `*.js` → **200**
- `socket.io` → **200**
- `frappe/icons/lucide.svg` → **200**
- Desk page after login → **200** (frappe.boot loads, 29 workspaces, all roles)

---

## [v16.23.0-axerp.2] — upstream: v16.23.0 | 2026-06-16 | Daniel Brody

### Added — Frappe Insights v3 (develop branch, v16-compatible)

**Insights:** `frappe/insights` `develop` branch (v3.3.1). The stable `version-3` branch targets frappe 14/15 only; `develop` has explicit v16 CI (`ci: run compatibility check for v15 & v16`) and v16-specific fixes.

**Changed:**
- `docker/Dockerfile`: Added `RUN git clone --depth 1 --branch develop` for insights, `env/bin/pip install -e apps/insights`, `bench build --app insights`. Added `INSIGHTS_VERSION` ARG.
- `docker-compose.axerp.yml`: Image bumped to `axerp:v16.23.0-axerp.2`. `create-site` now installs insights after hrms/crm.

**Post-deploy bench sequence (full expert run):**
```bash
bench --site erp.axinagroup.com install-app insights
bench --site erp.axinagroup.com migrate
bench build --production
bench --site erp.axinagroup.com clear-cache
bench --site erp.axinagroup.com clear-website-cache
bench --site erp.axinagroup.com build-search-index
bench doctor
```

---

## [v16.23.0-axerp.1] — upstream: v16.23.0 | 2026-06-16 | Daniel Brody

### Added — HRMS and CRM apps; ERPNext v16.23.0 upstream sync

**Upstream sync:** `sync_upstream.sh v16.23.0` — merged clean, no conflicts. AXERP branding re-applied via `smart_rename.py`.

**Bundled apps added to Docker image:**
| App | Source | Version |
|-----|--------|---------|
| `frappe/hrms` | `version-16` branch | v16.9.0 (HR, Payroll, Leave, Expenses, Recruitment) |
| `frappe/crm` | `main` branch | v1.73.2 (Sales CRM, frappe >=15 <17) |

**Changed:**
- `docker/Dockerfile`: Base ARG bumped `v16.22.0` → `v16.23.0`. Added `RUN git clone --depth 1` steps for hrms and crm before AXERP COPY. Added `HRMS_VERSION` and `CRM_VERSION` ARGs (must be re-declared after `FROM` — Docker ARG scope rule). All three apps installed via `env/bin/pip install -e` (bench venv, not user site-packages) and assets built with `bench build` per app.
- Infrastructure `docker-compose.axerp.yml`: Image tag bumped to `axerp:v16.23.0-axerp.1`. `create-site` extended to `bench install-app hrms` and `bench install-app crm` after base erpnext install.

**Deploy steps for existing site (no data loss):**
```bash
# 1. Pull updated source and rebuild on EC2 (arm64)
cd /data/axerp-src && git pull
docker build --platform linux/arm64 -f docker/Dockerfile \
  -t axerp:v16.23.0-axerp.1 -t axerp:prod .

# 2. Install apps into running site
docker exec axerp-backend bench --site erp.axinagroup.com install-app hrms
docker exec axerp-backend bench --site erp.axinagroup.com install-app crm

# 3. Run migrations (ERPNext v16.23.0 may add DB columns)
docker exec axerp-backend bench --site erp.axinagroup.com migrate

# 4. Redeploy workers + frontend with new image
cd /opt/openproject
docker compose -f docker-compose.axerp.yml up -d --force-recreate \
  backend frontend websocket queue-long queue-short scheduler

# 5. Clear cache
docker exec axerp-backend bench --site erp.axinagroup.com clear-cache
```

---

## [v16.22.0-axerp.4] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Architecture change — MariaDB replaces PostgreSQL for AXERP

**Problem:** `frappe.utils.goal.get_monthly_goal_graph_data` (frappe core, not AXERP) builds
`sum('base_grand_total')` as a string literal in the generated SQL. PostgreSQL rejects
this with `function sum(unknown) is not unique`. This is one of thousands of raw SQL
queries in AXERP written assuming MariaDB; patching each one individually is not viable.

**Decision:** Deploy a dedicated `axerp-mariadb` (MariaDB 10.6, arm64) container for AXERP.
PostgreSQL remains in use for OpenProject and Nextcloud — those apps prefer it. AXERP gets
the database it was designed for.

**Changed:**
- `docker/Dockerfile`: no code change needed — image is DB-agnostic; MariaDB client libs
  are already present in the `frappe/erpnext` base image.
- Infrastructure `docker-compose.axerp.yml`:
  - Removed `--db-type postgres` from configurator and `bench new-site`.
  - Added `axerp-mariadb` service (MariaDB 10.6, arm64, `/data/axerp/mariadb` volume).
  - `create-site` now uses `--mariadb-root-password` instead of `--db-root-username/password`.
  - `configurator` waits for `axerp-mariadb` healthcheck before writing `common_site_config.json`.
- Removed all AXERP-side PostgreSQL compatibility patches from `company.py`
  (`update_company_monthly_sales`, `get_all_transactions_annual_history`) — these are no
  longer needed on MariaDB and revert to upstream standard behavior.
- `.env.example`: added `AXERP_DB_ROOT_PASSWORD`; removed `OPENPROJECT_DB_PASSWORD` cross-use.

**Database layout on EC2:**
| Container | Engine | Used by |
|-----------|--------|---------|
| `openproject-postgres` | PostgreSQL 16 | OpenProject, Nextcloud |
| `axerp-mariadb` | MariaDB 10.6 | AXERP (AXERP) only |

**Migration required:** Existing PostgreSQL-backed site must be dropped and recreated on MariaDB.
Site data at `/data/axerp/sites/erp.axinagroup.com/` deleted before redeploy.
Companies re-created via API provisioner (`infrastructure/axerp-api/create_company.py`).

---

## [v16.22.0-axerp.3] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Fixed
- **erpnext/setup/doctype/company/company.py** — Two PostgreSQL compatibility fixes:

  1. **`update_company_monthly_sales`**: Replaced `frappe.utils.goal.get_monthly_results` call with a direct Query Builder query using `Sum(si.base_grand_total)` (typed column reference). `get_monthly_results` passes `goal_field` as a plain string to `Function('sum', goal_field)`, which PostgreSQL rejects with `function sum(unknown) does not exist` because it cannot infer the type of an unresolved string literal.

  2. **`get_all_transactions_annual_history`**: Replaced MySQL-only `date_sub(curdate(), interval 1 year)` in raw SQL with a parameterized `%s` bound to `frappe.utils.add_to_date(today(), years=-1)`. PostgreSQL does not recognize `DATE_SUB()` or `curdate()`.

---

## [v16.22.0-axerp.2] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Fixed
- **docker/Dockerfile**: Corrected base image tag from non-existent `frappe/erpnext:v16.26.4` to valid `frappe/erpnext:v16.22.0`.
  - Root cause: `XLSXMetadata` / `XLSXStyleBuilder` introduced in frappe ~16.15 caused `ImportError` when creating a Company via the Setup Wizard. Old base `v16.13.3` predated these symbols; new base `v16.22.0` matches the fork's erpnext version exactly.
  - Verified: `from frappe.utils.xlsxutils import XLSXMetadata, XLSXStyleBuilder` imports successfully in running container.

---

## [v16.22.0-axerp.1] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Added
- Initial production deployment to `erp.axinagroup.com` (EC2 t4g.xlarge arm64, us-east-1).
- **docker/docker-compose.yml**: Added `docker-compose.axerp.yml` in infra repo for 9-service Frappe stack (backend, frontend, websocket, scheduler, queue-long, queue-short, configurator, create-site, two Redis instances).
- PostgreSQL backend: reuses shared `openproject-postgres` (PostgreSQL 16) container on `openproject_default` Docker network. No separate MariaDB required.
- TLS: Let's Encrypt cert issued 2026-06-16 (expires 2026-09-14), auto-renewed by existing certbot container.
- `platform: linux/arm64` pinned on all images for Graviton2 compatibility.
- Idempotent `create-site` script: skips `bench new-site` if `site_config.json` already exists.

### Changed
- **docker/Dockerfile**: Base image bumped `frappe/erpnext:v16.13.3` → `v16.22.0` to match fork's erpnext version and include frappe 16.20.x with `XLSXMetadata` support.

### Infrastructure
- Route53 A record `erp.axinagroup.com` → `44.195.198.18` created 2026-06-16.
- Site data at `/data/axerp/sites/` on 500GB EBS data volume.
- Source cloned to `/data/axerp-src` on EC2; image built natively as `axerp:prod`.

---

## [v16.22.0-axerp] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Changed (AXERP Rebrand)
- Applied `scripts/smart_rename.py`: AXERP → AXERP in UI strings, titles, metadata.
- **Preserved** (not rebranded): `erpnext_integrations` module name, all `erpnext.erpnext_integrations.*` import paths, `"module": "AXERP Integrations"` in DocType JSON.
- **hooks.py**: `app_publisher`, `app_description`, `app_email`, `source_link` updated to Axina Group values.
- **pyproject.toml**: author → `Axina Group Inc.`, description → `ERP System Built on the Frappe Framework`.
- **package.json**: author, homepage, description updated.
- **CODEOWNERS**: sole owner `@dzbrody`.
- **README.md**: removed open-source claims, Frappe School badge, upstream community links.
- **SECURITY.md**: updated contact URLs to `axinagroup.com/security`.
- **TRADEMARK_POLICY.md**: ownership updated to `Axina Group Inc.`.
- **initiate_release.yml**: upstream weekly release workflow disabled (`if: false`).
- Logo files replaced with `axinagroup-logo.svg` at all standard asset paths.

### Upstream Base
- Merged `frappe/erpnext` tag `v16.22.0` (2026-06-10) into `version-16` branch.

---

## Sync Process

To sync a new upstream release:

```bash
cd /Users/dzbrody/Dev/GitHub/AXERP
bash scripts/sync_upstream.sh v16.X.Y
# Resolve any conflicts, then update this changelog.
# Create PR: version-16 → production
```

See `xgc_github_erpsync.md` and `.kiro/steering/upstream-sync.md` for the full workflow.
