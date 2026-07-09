# AXERP Docker — Claude Code Instructions

This directory contains the production Dockerfile and all deployment tooling for
AXERP (Axina Group's ERPNext fork) running at **https://erp.tspgusa.com**.

## Environment

- **Host:** EC2 i-07bb8581203e52527 (t4g.xlarge, arm64 Graviton2, us-east-1f)
- **Access:** AWS SSM only — no SSH. All remote commands via `aws ssm send-command`.
- **S3 bucket:** `s3://axina-openproject-files/deploy/` — upload scripts here before running on EC2 to avoid SSM JSON-escaping limits.
- **Compose file locations:**
  - Local: `infrastructure/docker/docker-compose.axerp.yml` (source of truth)
  - EC2: `/opt/openproject/docker-compose.axerp.yml`
- **Data volumes on EC2:**
  - `/data/axerp/sites/` — Frappe site config, uploaded files, site DB credentials
  - `/data/axerp/mariadb/` — MariaDB data directory
  - `/data/axerp/logs/` — bench logs

## Image naming convention

```
axerp:v<ERPNEXT_VERSION>-axerp.<PATCH>
```

Examples: `axerp:v16.23.0-axerp.3`, `axerp:prod` (alias for latest)

Bump `<PATCH>` for any change to the Dockerfile or bundled apps. Bump `<ERPNEXT_VERSION>` when syncing upstream ERPNext.

## Bundled apps (current: axerp.2 @ v16.26.2)

| App | Branch/Pin | Version |
|-----|-----------|---------|
| frappe | base image | 16.26.2 |
| erpnext (AXERP) | production branch | 16.26.2 |
| hrms | version-16 | 16.10.1 |
| crm | main | 1.76.0 |
| insights | develop (v16-compatible) | 3.3.1 |
| wiki | version-3 | 3.0.0 |
| blog | develop | 0.0.1 |

## How to upgrade upstream ERPNext

```bash
# 1. Sync upstream on version-16 branch
git checkout version-16
bash scripts/sync_upstream.sh v16.X.Y   # merges upstream, applies AXERP branding

# 2. Bump ARG in Dockerfile
# ERPNEXT_VERSION=v16.X.Y
# Build tag: axerp:v16.X.Y-axerp.1

# 3. Add CHANGELOG entry in AXERP_CHANGELOG.md

# 4. Open PR: version-16 → production
# 5. Merge, then run the build+deploy procedure below
```

## How to add or upgrade a bundled app

1. Update the `ARG <APP>_VERSION` at the top of `Dockerfile`
2. If adding a new app:
   - Add `RUN git clone --depth 1 --branch ${APP_VERSION}` block
   - Add `RUN env/bin/pip install --no-cache-dir -e apps/<app>`
   - Add `RUN bench build --app <app>`
   - Add to the `BAKED_PATH` copy loop at the bottom
   - Add `bench --site $$SITE_NAME install-app <app>` to `create-site` in compose
3. Bump the axerp patch number in the image tag
4. Update `AXERP_CHANGELOG.md`

## Build procedure (on EC2 via SSM)

Scripts are on S3 at `s3://axina-openproject-files/deploy/`:

```bash
# Package the production branch
git archive production --format=tar.gz -o /tmp/axerp-production.tar.gz --prefix=axerp/
aws s3 cp /tmp/axerp-production.tar.gz s3://axina-openproject-files/deploy/axerp-production.tar.gz
aws s3 cp infrastructure/docker/docker-compose.axerp.yml s3://axina-openproject-files/deploy/docker-compose.axerp.yml

# Run the build script on EC2 (uploads build output to /tmp/docker-build.log)
# Script: s3://axina-openproject-files/deploy/axerp-build-v3b.sh
```

The build script (axerp-build-v3b.sh):
1. Downloads source tarball + compose from S3
2. Runs `docker build --platform linux/arm64 --no-cache`
3. Runs `docker compose up -d` (no `--remove-orphans` — would stop OpenProject/Nextcloud)
4. Runs the post-deploy asset sync (see below)

Build time: ~8 minutes on arm64 Graviton2.

## Frappe version tracking

Frappe Framework is bundled inside the base image (`frappe/erpnext:${ERPNEXT_VERSION}`).
When `ERPNEXT_VERSION` is bumped (e.g. `v16.25.0` → `v16.26.2`), the base image is pulled
fresh during `docker build --no-cache`, which automatically brings the matching frappe version.
No separate frappe pin is needed — frappe and erpnext versions are always in sync via the base image tag.

To verify the running frappe version:
```bash
docker exec axerp-backend bench version
```

## Post-deploy asset sync (REQUIRED after every redeploy)

**Why:** The frappe_docker entrypoint runs on every container start:
```bash
rm -rf sites/assets
ln -s /home/frappe/frappe-bench/assets sites/assets
```
This replaces `sites/assets/` with a symlink to `BAKED_PATH=/home/frappe/frappe-bench/assets`.
The image bakes all app `public/` dirs into `BAKED_PATH` at build time.
After every deploy, the backend container regenerates `assets.json` with new content hashes
in its writable layer — the frontend container still has the baked version → hash mismatch →
404s, MIME errors, broken icons/CSS.

**Critical:** use `bench build --production` (not per-app builds). Per-app builds only update
that app's entries in `assets.json`, leaving other apps' hashes stale. `--production` rebuilds
all apps in one pass and writes a fully consistent `assets.json`.

**Fix after every `docker compose up -d` with a new image:**

```bash
# On EC2 (run via SSM or S3):
# Script: s3://axina-openproject-files/deploy/axerp-fix-assets-json.sh
# Also runs automatically via scripts/deploy.sh

# What it does:
docker exec axerp-backend bench build --production   # rebuild ALL bundles + regenerate assets.json
# docker cp all app assets (frappe/erpnext/hrms/crm/insights/wiki/blog) backend → frontend
# nginx reload, Redis FLUSHALL, clear-cache, verify all bundles return 200
```

Run time: ~2–3 minutes (full rebuild). After this, all bundles return 200.

**Migrate also runs `bench build --production`:**
The `axerp-migrate` compose service runs `bench migrate` followed immediately by
`bench build --production` before the backend starts — so DB schema changes and
frontend asset changes are always applied together.

**Verify everything is serving:**
```bash
# Quick spot-check from your laptop:
curl -sk -o /dev/null -w "%{http_code}" "https://erp.tspgusa.com/assets/frappe/dist/js/desk.bundle.$(...)js"
```

## Known Dockerfile constraints

### `common_site_config.json` stub required
hrms Vite build imports `socketio_port` from `sites/common_site_config.json` at build time.
This file doesn't exist during `docker build`. A stub is created before `bench build`:
```dockerfile
RUN mkdir -p sites && \
    echo '{"socketio_port":9000,...}' > sites/common_site_config.json
```
If removed, hrms build fails with `"socketio_port" is not exported`.

### `html2canvas` must be yarn-added before hrms build
hrms imports `html2canvas` in `hierarchy_chart_desktop.js` but doesn't declare it in
`package.json`. Without `yarn add html2canvas`, bench build fails with `Could not resolve "html2canvas"`.

### Docker ARG scope
ARGs declared before `FROM` go out of scope inside the build stage. Always re-declare after `FROM`:
```dockerfile
ARG HRMS_VERSION
ARG CRM_VERSION
ARG INSIGHTS_VERSION
# (no default = inherits global value)
```

### `env/bin/pip` not plain `pip`
bench uses a virtualenv at `env/`. Plain `pip` installs to `~/.local` (user site-packages),
invisible to the venv. Always use `env/bin/pip install -e apps/<app>`.

### BAKED_PATH = `/home/frappe/frappe-bench/assets`
The frappe_docker entrypoint symlinks `sites/assets → /home/frappe/frappe-bench/assets`.
Asset files must be in `BAKED_PATH`, not in `sites/assets/`. The final RUN in the Dockerfile
copies all app `public/` dirs there.

## Fixing a blank desktop / broken assets on a running instance

### Symptom: MIME type errors, 404 for `.bundle.css`/`.bundle.js`
**Cause:** assets.json hash mismatch between backend and frontend containers.
```bash
docker exec axerp-backend bench build --app frappe
# then run axerp-fix-assets-json.sh
```

### Symptom: Blank white page after login
**Check 1:** `setup_complete` flag:
```bash
DB_NAME=$(docker exec axerp-backend python3 -c "import json; c=json.load(open('/home/frappe/frappe-bench/sites/erp.tspgusa.com/site_config.json')); print(c['db_name'])")
DB_PASS=$(docker exec axerp-backend python3 -c "import json; c=json.load(open('/home/frappe/frappe-bench/sites/erp.tspgusa.com/site_config.json')); print(c['db_password'])")
docker exec axerp-mariadb mysql -u ${DB_NAME} -p"${DB_PASS}" ${DB_NAME} \
  -e "SELECT field, value FROM tabSingles WHERE doctype='System Settings' AND field='setup_complete';"
# If value != 1:
docker exec axerp-mariadb mysql -u ${DB_NAME} -p"${DB_PASS}" ${DB_NAME} \
  -e "INSERT INTO tabSingles (doctype,field,value) VALUES('System Settings','setup_complete','1') ON DUPLICATE KEY UPDATE value='1';"
docker exec axerp-redis-cache redis-cli FLUSHALL
docker exec axerp-backend bench --site erp.tspgusa.com clear-cache
```

**Check 2:** Stale `db_type: postgres` in `common_site_config.json`:
```bash
docker exec axerp-backend cat /home/frappe/frappe-bench/sites/common_site_config.json
# If db_type: postgres is present, remove it:
docker exec axerp-backend python3 -c "
import json
p='/home/frappe/frappe-bench/sites/common_site_config.json'
c=json.load(open(p)); c.pop('db_type',None); json.dump(c,open(p,'w'),indent=1)"
docker exec axerp-redis-cache redis-cli FLUSHALL
docker exec axerp-backend bench --site erp.tspgusa.com clear-cache
```

### Symptom: socket.io 400/502
- 400 = socket.io server rejecting plain HTTP GET (normal — it needs a WS upgrade handshake)
- 502 = nginx can't reach `axerp-websocket:9000` — check `docker ps` for websocket container
- The outer nginx (openproject-nginx) proxies `/socket.io/` directly to `axerp-websocket:9000`

### Symptom: Nextcloud 503 after AXERP redeploy
The AXERP build script previously used `--remove-orphans` which stops all containers in
the `openproject_default` network including Nextcloud. The current build script does NOT use
`--remove-orphans`. If Nextcloud is down, restart it:
```bash
cd /opt/openproject && docker compose -f docker-compose.nextcloud.yml up -d
```
If Nextcloud shows "invalid data directory", create the missing `.ncdata` marker:
```bash
NC_VOL=$(docker inspect nextcloud-app --format '{{range .Mounts}}{{if eq .Destination "/var/www/html"}}{{.Source}}{{end}}{{end}}')
echo "# Nextcloud data directory" > ${NC_VOL}/data/.ncdata
chown 33:33 ${NC_VOL}/data/.ncdata
```

## Deploy .env variables

The compose file reads from `/opt/openproject/.env` on EC2 (chmod 600):
```
AXERP_DB_ROOT_PASSWORD=...
AXERP_ADMIN_PASSWORD=...   # used only on first-run site creation
AXERP_SITE_NAME=erp.tspgusa.com
```

Admin password after initial setup is managed inside Frappe (not from env).
Stored in 1Password as **"AXERP Admin"** under Administrator account.

## Container names and roles

| Container | Role |
|-----------|------|
| `axerp-backend` | Gunicorn (Python WSGI, port 8000) |
| `axerp-frontend` | Nginx (serves assets + proxies to backend, port 8082→8080) |
| `axerp-websocket` | Node socket.io (port 9000) |
| `axerp-scheduler` | bench schedule (background tasks) |
| `axerp-queue-long` | RQ worker — long/default/short queues |
| `axerp-queue-short` | RQ worker — short/default queues |
| `axerp-configurator` | One-shot: writes common_site_config.json |
| `axerp-create-site` | One-shot: bench new-site + install-app (first run only) |
| `axerp-mariadb` | MariaDB 10.6 (arm64) |
| `axerp-redis-cache` | Redis cache (no persistence) |
| `axerp-redis-queue` | Redis job queue (persisted) |

## Useful diagnostic commands

```bash
# Health check
docker ps --filter "name=axerp" --format "{{.Names}} | {{.Status}}"

# Live logs
docker logs axerp-backend --tail 50 -f
docker logs axerp-frontend --tail 20

# Frappe site shell
docker exec axerp-backend bench --site erp.tspgusa.com console

# Run migrate (after app updates)
docker exec axerp-backend bench --site erp.tspgusa.com migrate

# Clear all caches
docker exec axerp-redis-cache redis-cli FLUSHALL
docker exec axerp-backend bench --site erp.tspgusa.com clear-cache
docker exec axerp-backend bench --site erp.tspgusa.com clear-website-cache

# Check installed apps + versions
docker exec axerp-backend bench --site erp.tspgusa.com list-apps

# Test API
curl -s "https://erp.tspgusa.com/api/method/ping"

# Reset admin password
docker exec axerp-backend bench --site erp.tspgusa.com set-admin-password <newpassword>

# DB shell
docker exec -it axerp-mariadb mysql -u root -p
```
