# AXERP Docker — Claude Code Instructions

Production AXERP (ERPNext fork) running at **https://erp.tspgusa.com**.

## Environment

| Item | Value |
|------|-------|
| Host | EC2 `i-07bb8581203e52527` (t4g.xlarge, arm64 Graviton2, us-east-1f) |
| Access | AWS SSM only — no SSH. Use `aws ssm send-command` |
| ECR registry | `010438486646.dkr.ecr.us-east-1.amazonaws.com/axerp` |
| EC2 IAM role | `axina-openproject-role` (has `AmazonEC2ContainerRegistryPowerUser`) |
| Compose on EC2 | `/opt/openproject/docker-compose.axerp.yml` |
| Outer nginx | `/opt/openproject/nginx.conf` |
| Inner nginx | `/data/axerp/sites/frappe_nginx.conf` (bind-mounted into axerp-frontend) |
| Site data | `/data/axerp/sites/erp.tspgusa.com/` |
| MariaDB data | `/data/axerp/mariadb/` |
| S3 deploy | `s3://axina-openproject-files/deploy/` |

## Image Registry — AWS ECR Private

```
010438486646.dkr.ecr.us-east-1.amazonaws.com/axerp:<tag>
```

ECR lifecycle policy: keep last 5 tagged images; untagged expire after 1 day.
EC2 pulls via IAM role — no `docker login` needed for pulls on EC2.
`docker login` IS needed for pushes (done inside the build script).

### Image tag convention

```
v<ERPNEXT_VERSION>-axerp.<PATCH>   e.g.  v16.26.2-axerp.5
```

- Bump `<PATCH>` for any Dockerfile or bundled app change at the same ERPNext version
- Reset to `.1` when syncing a new upstream ERPNext version
- **Two files must always be in sync:**
  - `docker/Dockerfile` line 10: `# -t axerp:v16.26.2-axerp.5 -t axerp:prod .`
  - `infrastructure/docker/docker-compose.axerp.yml`: `image: 010438486646.dkr.ecr.us-east-1.amazonaws.com/axerp:v16.26.2-axerp.5`
- `deploy.sh` reads the tag from the **compose file** (primary); the Dockerfile comment is fallback only

## Bundled Apps (current: axerp.5 @ v16.26.2)

| App | Branch/Pin | Version | Notes |
|-----|-----------|---------|-------|
| frappe | base image | 16.26.2 | auto-matches ERPNEXT_VERSION |
| erpnext (AXERP) | production branch | 16.26.2 | rebranded fork |
| hrms | version-16 | 16.12.1 | |
| crm | main | 1.77.3 | yarn pre-install required |
| insights | develop | 3.3.1 | version-3 is frappe 14/15 only |
| wiki | version-3 | 3.0.0 | |
| blog | develop | 0.0.1 | orange icon baked in |

## How to Deploy

```bash
bash scripts/deploy.sh
```

The script does everything: `git fetch` → tarball → S3 → EC2 build → ECR push → compose up → migrate → asset fix → health checks → GitHub release. See `scripts/deploy.sh` for the full flow.

**Critical:** `deploy.sh` always runs `git fetch origin production` before `git archive`. Never skip this — the known failure mode is packaging a stale pre-merge Dockerfile from the local ref cache.

## How to Upgrade Upstream ERPNext

```bash
# 1. Check latest v16 tag
curl -s "https://api.github.com/repos/frappe/erpnext/releases?per_page=20" | \
  python3 -c "import sys,json; r=[x['tag_name'] for x in json.load(sys.stdin) if x['tag_name'].startswith('v16')]; print(r[0])"

# 2. Run /axerp-sync — merges, rebrands, bumps Dockerfile ERPNEXT_VERSION, writes changelog

# 3. Bump image tag in BOTH files:
#    docker/Dockerfile line 10 comment
#    infrastructure/docker/docker-compose.axerp.yml image: line

# 4. Verify erpnext_integrations not rebranded
grep -n "Integrations" erpnext/modules.txt   # must say ERPNext Integrations

# 5. Open PR: version-16 → production, merge

# 6. Deploy
bash scripts/deploy.sh
```

## How to Add a Bundled App

1. Add `ARG <APP>_VERSION=<branch>` at the top of `Dockerfile` (before and after `FROM`)
2. Add `RUN git clone --depth 1 --branch ${APP_VERSION} https://github.com/frappe/<app>.git apps/<app>`
3. Add `RUN env/bin/pip install --no-cache-dir -e apps/<app>`
4. Add `RUN bench build --app <app>`
5. Add `<app>` to the BAKED_PATH copy loop
6. Add `bench --site $$SITE_NAME install-app <app>` to `create-site` in compose
7. Add app to the fix-assets sync loop in `axerp-fix-assets-json.sh` on S3
8. Bump patch tag in both files, update `AXERP_CHANGELOG.md`

## Known Dockerfile Build Constraints

Do not remove any of these — each was added to fix a real build failure:

### yarn add html2canvas (hrms)
hrms imports `html2canvas` but doesn't declare it in `package.json`. Without `yarn add html2canvas` before `bench build --app hrms`, the build fails with `Could not resolve "html2canvas"`.

### CRM yarn pre-install in app root AND frontend/
frappe's `esbuild.js:536` runs `yarn install --frozen-lockfile` in `apps/crm/` (not just `frontend/`) when `node_modules` is absent. The CRM `main` branch `yarn.lock` drifts from `package.json`. Pre-install both with `--no-frozen-lockfile`:
```dockerfile
RUN cd apps/crm && yarn install --no-frozen-lockfile --silent
RUN cd apps/crm/frontend && yarn install --no-frozen-lockfile --silent
```

### common_site_config.json stub (hrms Vite)
hrms Vite build imports `socketio_port` from `sites/common_site_config.json` at build time. Without the stub, hrms build fails with `"socketio_port" is not exported`.

### env/bin/pip not plain pip
bench uses a venv at `env/`. Plain `pip` installs to `~/.local`, invisible to the venv. Always `env/bin/pip install -e apps/<app>`.

### BAKED_PATH = /home/frappe/frappe-bench/assets
The frappe_docker entrypoint does `rm -rf sites/assets && ln -s /home/frappe/frappe-bench/assets sites/assets`. Assets must go into `BAKED_PATH`, not `sites/assets/`.

### blog-orange.svg is NOT in .dockerignore
Confirmed — `docker/blog-orange.svg` is tracked in git and not excluded. `COPY docker/blog-orange.svg` works.

## Frappe Version Tracking

Frappe is bundled in the base image `frappe/erpnext:${ERPNEXT_VERSION}`. When `ERPNEXT_VERSION` is bumped, `docker build --no-cache` pulls the new base image automatically. No separate frappe pin is needed.

```bash
docker exec axerp-backend bench version   # check running frappe version
```

## Post-Deploy Asset Fix (REQUIRED after every deploy)

`bench build --production` in the migrate container does not propagate to the frontend container's filesystem. Always run the fix script after every deploy.

**Always use `bench build --production`, never per-app builds.** Per-app builds leave other apps' hashes stale in `assets.json`, causing 404s for those bundles.

```bash
# Runs automatically via scripts/deploy.sh
# To run manually:
aws ssm send-command \
  --instance-ids i-07bb8581203e52527 \
  --document-name "AWS-RunShellScript" --region us-east-1 \
  --parameters '{"commands":["aws s3 cp s3://axina-openproject-files/deploy/axerp-fix-assets-json.sh /tmp/fix.sh --quiet && SITE=erp.tspgusa.com bash /tmp/fix.sh"]}'
```

## Nginx Architecture (two layers)

When debugging 502s after a deploy or domain change, both layers must use the correct site name:

```
Internet
  → openproject-nginx (/opt/openproject/nginx.conf)
       proxy_set_header Host erp.tspgusa.com
       proxy_set_header X-Frappe-Site-Name erp.tspgusa.com
       upstream axerp → axerp-frontend:8080
  → axerp-frontend (/data/axerp/sites/frappe_nginx.conf)
       proxy_set_header X-Frappe-Site-Name erp.tspgusa.com
       upstream backend-server → axerp-backend:8000
  → axerp-backend (Gunicorn)
       resolves site from X-Frappe-Site-Name header
       looks up sites/erp.tspgusa.com/
```

After domain changes or first deploy with a new site name:
```bash
# Fix inner nginx and restart (reload alone is not enough)
sed -i "s/OLD_DOMAIN/erp.tspgusa.com/g" /data/axerp/sites/frappe_nginx.conf
docker restart axerp-frontend

# Fix outer nginx proxy headers and reload
sed -i "s/proxy_set_header X-Frappe-Site-Name OLD/proxy_set_header X-Frappe-Site-Name erp.tspgusa.com/g" /opt/openproject/nginx.conf
sed -i "s/proxy_set_header Host OLD/proxy_set_header Host erp.tspgusa.com/g" /opt/openproject/nginx.conf
docker exec openproject-nginx nginx -s reload
```

## Container Names and Roles

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
| `axerp-migrate` | One-shot: bench migrate + bench build --production (every deploy) |
| `axerp-mariadb` | MariaDB 10.6 (arm64) |
| `axerp-redis-cache` | Redis cache (no persistence) |
| `axerp-redis-queue` | Redis job queue (persisted) |

## Diagnostic Commands

```bash
# Container health
docker ps --filter "name=axerp" --format "{{.Names}} | {{.Status}}" | sort

# Live logs
docker logs axerp-backend --tail 50 -f
docker logs axerp-migrate --tail 30

# Verify ping
curl -s "https://erp.tspgusa.com/api/method/ping"   # expect: {"message":"pong"}

# Installed apps + versions
docker exec axerp-backend bench --site erp.tspgusa.com list-apps
docker exec axerp-backend bench version

# Frappe site shell
docker exec axerp-backend bench --site erp.tspgusa.com console

# Run migrate manually
docker exec axerp-backend bench --site erp.tspgusa.com migrate

# Clear all caches
docker exec axerp-redis-cache redis-cli FLUSHALL
docker exec axerp-backend bench --site erp.tspgusa.com clear-cache
docker exec axerp-backend bench --site erp.tspgusa.com clear-website-cache

# Test Gunicorn directly with correct host header (bypasses nginx)
BACKEND_IP=$(docker inspect axerp-backend \
  --format "{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}" | awk '{print $1}')
curl -sk -H "Host: erp.tspgusa.com" http://$BACKEND_IP:8000/api/method/ping

# Reset admin password
docker exec axerp-backend bench --site erp.tspgusa.com set-admin-password <newpassword>

# DB shell
docker exec -it axerp-mariadb mysql -u root -p

# ECR image list
aws ecr describe-images --repository-name axerp --region us-east-1 \
  --query "sort_by(imageDetails,&imagePushedAt)[-5:] | reverse(@) | [].{tag:imageTag[0],pushed:imagePushedAt,mb:to_string(imageSizeInBytes)}" \
  --output table

# Check build log from last EC2 deploy
# (run via SSM send-command)
tail -50 /tmp/axerp-deploy-run.log
tail -40 /tmp/docker-build.log
```

## Deploy .env on EC2

`/opt/openproject/.env` (chmod 600):
```
AXERP_DB_ROOT_PASSWORD=...
AXERP_ADMIN_PASSWORD=...   # used only on first-run site creation
AXERP_SITE_NAME=erp.tspgusa.com
```

Admin password after first setup is managed inside Frappe. Stored in 1Password as **"AXERP Admin"** (Administrator account).

## Symptom → Fix Reference

| Symptom | First check | Fix |
|---------|------------|-----|
| 502 Bad Gateway | `grep X-Frappe-Site-Name /data/axerp/sites/frappe_nginx.conf` | Update inner nginx, `docker restart axerp-frontend` |
| 502 persists | `grep X-Frappe-Site-Name /opt/openproject/nginx.conf` | Update outer nginx, reload |
| CSS/icons broken | assets.json hash mismatch | Run `axerp-fix-assets-json.sh` |
| Blank desktop | `setup_complete` flag or stale db_type in common_site_config | See CLAUDE.md troubleshooting above |
| Build fails: CRM yarn | `yarn.lock` drift in CRM `main` | Already fixed in Dockerfile; if it recurrs, check CRM upstream |
| Nextcloud 503 after deploy | compose up killed Nextcloud orphan containers | `docker compose -f docker-compose.nextcloud.yml up -d` |
| socket.io 502 | `axerp-websocket` container down | `docker compose -f docker-compose.axerp.yml up -d axerp-websocket` |
