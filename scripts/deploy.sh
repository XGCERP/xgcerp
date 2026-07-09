#!/bin/bash
# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
#
# AXERP Deploy Script — push to EC2, build, deploy, verify.
#
# Usage:
#   bash scripts/deploy.sh              # deploy production branch with auto-detected image tag
#   bash scripts/deploy.sh --dry-run    # print steps without executing
#   bash scripts/deploy.sh --skip-build # skip EC2 build (redeploy same image)
#
# Prerequisites: aws CLI configured, gh CLI authenticated, jq installed.

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
EC2_INSTANCE="i-07bb8581203e52527"
AWS_REGION="us-east-1"
S3_BUCKET="axina-openproject-files"
S3_PREFIX="deploy"
SITE="erp.tspgusa.com"
COMPOSE_LOCAL="infrastructure/docker/docker-compose.axerp.yml"
MIGRATE_MONITOR_SECONDS=120  # how long to tail migrate logs after deploy

DRY_RUN=false
SKIP_BUILD=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]]    && DRY_RUN=true
  [[ "$arg" == "--skip-build" ]] && SKIP_BUILD=true
done

# ── Helpers ──────────────────────────────────────────────────────────────────
log()  { echo "$(date -u +%H:%M:%S) ▶ $*"; }
ok()   { echo "$(date -u +%H:%M:%S) ✅ $*"; }
warn() { echo "$(date -u +%H:%M:%S) ⚠️  $*"; }
fail() { echo "$(date -u +%H:%M:%S) ❌ $*" >&2; exit 1; }

run() {
  if $DRY_RUN; then
    echo "  [dry-run] $*"
  else
    "$@"
  fi
}

ssm_run() {
  local description="$1"; shift
  local commands=("$@")
  log "${description}..."

  if $DRY_RUN; then
    echo "  [dry-run] SSM: ${commands[*]}"
    return 0
  fi

  local cmd_json
  cmd_json=$(printf '%s\n' "${commands[@]}" | python3 -c "
import json, sys
lines = sys.stdin.read().strip().splitlines()
print(json.dumps(lines))
")

  local cmd_id
  cmd_id=$(aws ssm send-command \
    --instance-ids "${EC2_INSTANCE}" \
    --document-name "AWS-RunShellScript" \
    --parameters "{\"commands\":${cmd_json}}" \
    --region "${AWS_REGION}" \
    --query "Command.CommandId" \
    --output text)

  log "  SSM command ID: ${cmd_id}"

  # Poll until done
  local status="InProgress"
  local elapsed=0
  while [[ "$status" == "InProgress" || "$status" == "Pending" ]]; do
    sleep 10
    elapsed=$((elapsed + 10))
    status=$(aws ssm get-command-invocation \
      --command-id "${cmd_id}" \
      --instance-id "${EC2_INSTANCE}" \
      --region "${AWS_REGION}" \
      --query "Status" \
      --output text 2>/dev/null || echo "Pending")
    echo "  ${elapsed}s — ${status}"
    if [[ $elapsed -ge 3600 ]]; then
      fail "SSM command timed out after 60 minutes"
    fi
  done

  local output
  output=$(aws ssm get-command-invocation \
    --command-id "${cmd_id}" \
    --instance-id "${EC2_INSTANCE}" \
    --region "${AWS_REGION}" \
    --query "[StandardOutputContent, StandardErrorContent]" \
    --output text)

  echo "── SSM output ──────────────────────────────────"
  echo "$output"
  echo "────────────────────────────────────────────────"

  if [[ "$status" != "Success" ]]; then
    fail "SSM command failed with status: ${status}"
  fi
}

# ── Preflight ────────────────────────────────────────────────────────────────
log "Preflight checks..."

command -v aws  >/dev/null 2>&1 || fail "aws CLI not found"
command -v gh   >/dev/null 2>&1 || fail "gh CLI not found"
command -v git  >/dev/null 2>&1 || fail "git not found"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "production" ]]; then
  warn "Not on production branch (on: ${CURRENT_BRANCH})"
  warn "Deploy packages the production branch from origin — proceeding."
fi

# Detect image tag from Dockerfile
ERPNEXT_VER=$(grep "^ARG ERPNEXT_VERSION=" docker/Dockerfile | cut -d= -f2)
# Check compose for patch suffix (axerp.N) — derive from comment in Dockerfile
IMAGE_TAG=$(grep "axerp:v" docker/Dockerfile | grep -v "^#.*ARG" | head -1 | \
  sed -E 's/.*-t (axerp:v[^ ]+).*/\1/' | grep -v "^$" || echo "")
if [[ -z "$IMAGE_TAG" ]]; then
  IMAGE_TAG="axerp:${ERPNEXT_VER}-axerp.1"
fi

log "Target image tag: ${IMAGE_TAG}"
log "Site: ${SITE}"
log "EC2:  ${EC2_INSTANCE} (${AWS_REGION})"
echo ""

if $DRY_RUN; then warn "DRY RUN — no changes will be made"; echo ""; fi

# ── Step 1: Package production branch ────────────────────────────────────────
log "Step 1/6 — Package production branch and upload to S3"

run git archive production \
  --format=tar.gz \
  -o /tmp/axerp-production.tar.gz \
  --prefix=axerp/ 2>/dev/null || {
    # If production branch isn't available locally, fetch it
    warn "production branch not found locally — fetching from origin..."
    run git fetch origin production
    run git archive origin/production \
      --format=tar.gz \
      -o /tmp/axerp-production.tar.gz \
      --prefix=axerp/
  }

TARBALL_SIZE=$(du -sh /tmp/axerp-production.tar.gz 2>/dev/null | cut -f1 || echo "?")
log "  Tarball size: ${TARBALL_SIZE}"

run aws s3 cp /tmp/axerp-production.tar.gz \
  "s3://${S3_BUCKET}/${S3_PREFIX}/axerp-production.tar.gz" --quiet

if [[ -f "${COMPOSE_LOCAL}" ]]; then
  run aws s3 cp "${COMPOSE_LOCAL}" \
    "s3://${S3_BUCKET}/${S3_PREFIX}/docker-compose.axerp.yml" --quiet
  ok "Compose file uploaded"
else
  warn "Compose file not found at ${COMPOSE_LOCAL} — skipping"
fi

ok "Step 1 complete"
echo ""

# ── Step 2: Generate build script on the fly ─────────────────────────────────
log "Step 2/6 — Generate and upload build script for ${IMAGE_TAG}"

BUILD_SCRIPT=$(cat <<EOBUILD
#!/bin/bash
set -e
IMAGE_TAG="${IMAGE_TAG}"
SITE="${SITE}"

echo "[1] Fetching source + compose..."
aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-production.tar.gz /tmp/axerp-production.tar.gz --quiet
aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/docker-compose.axerp.yml /opt/openproject/docker-compose.axerp.yml --quiet
echo "  tarball: \$(du -sh /tmp/axerp-production.tar.gz | cut -f1)"

echo "[2] Extracting source..."
rm -rf /tmp/axerp-build && mkdir -p /tmp/axerp-build
tar -xzf /tmp/axerp-production.tar.gz -C /tmp/axerp-build --strip-components=1

echo "[3] Building \${IMAGE_TAG} (arm64)..."
echo "  start: \$(date -u +%H:%M:%S)"
cd /tmp/axerp-build
docker build \\
  --platform linux/arm64 \\
  -f docker/Dockerfile \\
  -t \${IMAGE_TAG} \\
  -t axerp:prod \\
  --no-cache \\
  . > /tmp/docker-build.log 2>&1
BUILD_EXIT=\$?
echo "  end: \$(date -u +%H:%M:%S) | exit: \${BUILD_EXIT}"
if [ \${BUILD_EXIT} -ne 0 ]; then
  echo "BUILD FAILED — last 30 lines:"
  tail -30 /tmp/docker-build.log
  exit 1
fi
echo "  SUCCESS: \$(tail -1 /tmp/docker-build.log)"

echo "[4] Redeploy stack..."
cd /opt/openproject
docker compose -f docker-compose.axerp.yml up -d 2>&1 | grep -vE "^(Pulling|pulled)" | head -20

echo "[5] Waiting 20s for containers to start..."
sleep 20
docker ps --filter "name=axerp" --format "  {{.Names}} | {{.Status}}" | sort

echo "[6] DB migration — tail axerp-migrate logs..."
# migrate container runs as a one-shot; wait for it to exit then show output
MIGRATE_DEADLINE=\$(( \$(date +%s) + 300 ))
while docker ps -a --filter "name=axerp-migrate" --filter "status=running" --format "{{.Names}}" | grep -q axerp-migrate; do
  if [ \$(date +%s) -gt \${MIGRATE_DEADLINE} ]; then
    echo "  WARN: migrate still running after 5 minutes"
    break
  fi
  sleep 5
done
MIGRATE_EXIT=\$(docker inspect axerp-migrate --format "{{.State.ExitCode}}" 2>/dev/null || echo "?")
echo "  migrate exit code: \${MIGRATE_EXIT}"
docker logs axerp-migrate 2>&1 | tail -20
if [ "\${MIGRATE_EXIT}" != "0" ] && [ "\${MIGRATE_EXIT}" != "?" ]; then
  echo "  ERROR: migration failed — check docker logs axerp-migrate"
  exit 1
fi

echo "[7] Post-deploy asset fix..."
aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-fix-assets-json.sh /tmp/axerp-fix-assets-json.sh --quiet
SITE=\${SITE} bash /tmp/axerp-fix-assets-json.sh

echo "[8] Health check..."
CODE=\$(curl -sk -o /dev/null -w "%{http_code}" "https://\${SITE}/api/method/ping")
if [ "\${CODE}" = "200" ]; then
  echo "  PASS: \${SITE} returned 200"
else
  echo "  WARN: ping returned \${CODE} (site may still be warming up)"
fi

echo "[9] Clean old images..."
docker images axerp --format "  {{.Repository}}:{{.Tag}} | {{.Size}}"
EOBUILD
)

if ! $DRY_RUN; then
  echo "$BUILD_SCRIPT" > /tmp/axerp-deploy-run.sh
  aws s3 cp /tmp/axerp-deploy-run.sh \
    "s3://${S3_BUCKET}/${S3_PREFIX}/axerp-deploy-run.sh" --quiet
fi
ok "Step 2 complete"
echo ""

# ── Step 3: Trigger EC2 build ─────────────────────────────────────────────────
# The docker build takes 15-20 min. SSM AWS-RunShellScript enforces a max execution
# timeout that kills long-running commands. Workaround: download the script in one
# short SSM command, then launch it via nohup in the background, then poll a status
# file for completion.
if $SKIP_BUILD; then
  warn "Step 3/6 — Skipped (--skip-build)"
else
  log "Step 3/6 — EC2: Stage build script..."
  ssm_run "Stage deploy script on EC2" \
    "aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-deploy-run.sh /tmp/axerp-deploy-run.sh --quiet" \
    "chmod +x /tmp/axerp-deploy-run.sh" \
    "rm -f /tmp/axerp-deploy-status"

  log "Step 3/6 — EC2: Launch build in background..."
  ssm_run "Launch background build" \
    "aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-launch.sh /tmp/axerp-launch.sh --quiet" \
    "chmod +x /tmp/axerp-launch.sh" \
    "bash /tmp/axerp-launch.sh" \
    "sleep 3" \
    "pgrep -f axerp-deploy-run.sh && echo 'BUILD RUNNING' || echo 'NOT RUNNING'"

  log "Step 3/6 — Polling EC2 build progress (allow ~25 min)..."
  BUILD_DONE=false
  POLL_ELAPSED=0
  while [[ $POLL_ELAPSED -lt 1800 ]]; do
    sleep 30
    POLL_ELAPSED=$((POLL_ELAPSED + 30))

    # Check if status file exists (build finished)
    STATUS_OUT=$(aws ssm send-command \
      --instance-ids "${EC2_INSTANCE}" \
      --document-name "AWS-RunShellScript" \
      --parameters "{\"commands\":[\"cat /tmp/axerp-deploy-status 2>/dev/null || echo RUNNING\"],\"executionTimeout\":[\"30\"]}" \
      --timeout-seconds 60 \
      --region "${AWS_REGION}" \
      --query "Command.CommandId" --output text 2>/dev/null || echo "")

    if [[ -n "$STATUS_OUT" ]]; then
      sleep 8
      STATUS_VAL=$(aws ssm get-command-invocation \
        --command-id "${STATUS_OUT}" \
        --instance-id "${EC2_INSTANCE}" \
        --region "${AWS_REGION}" \
        --query "StandardOutputContent" --output text 2>/dev/null | tr -d '[:space:]')

      if [[ "$STATUS_VAL" == "0" ]]; then
        ok "  Build completed successfully (${POLL_ELAPSED}s)"
        BUILD_DONE=true
        break
      elif [[ "$STATUS_VAL" =~ ^[1-9][0-9]*$ ]]; then
        # Non-zero exit — fetch last 40 lines of log
        LOG_CMD=$(aws ssm send-command \
          --instance-ids "${EC2_INSTANCE}" \
          --document-name "AWS-RunShellScript" \
          --parameters "{\"commands\":[\"tail -40 /tmp/axerp-deploy-run.log 2>/dev/null\"],\"executionTimeout\":[\"30\"]}" \
          --timeout-seconds 60 \
          --region "${AWS_REGION}" \
          --query "Command.CommandId" --output text 2>/dev/null || echo "")
        sleep 8
        [[ -n "$LOG_CMD" ]] && aws ssm get-command-invocation \
          --command-id "${LOG_CMD}" --instance-id "${EC2_INSTANCE}" \
          --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null
        fail "EC2 build failed with exit code ${STATUS_VAL} after ${POLL_ELAPSED}s"
      else
        # Still RUNNING — show tail of log for progress
        LOG_CMD=$(aws ssm send-command \
          --instance-ids "${EC2_INSTANCE}" \
          --document-name "AWS-RunShellScript" \
          --parameters "{\"commands\":[\"tail -5 /tmp/axerp-deploy-run.log 2>/dev/null | tr '\\n' '|'\"],\"executionTimeout\":[\"30\"]}" \
          --timeout-seconds 60 \
          --region "${AWS_REGION}" \
          --query "Command.CommandId" --output text 2>/dev/null || echo "")
        sleep 8
        TAIL=""
        [[ -n "$LOG_CMD" ]] && TAIL=$(aws ssm get-command-invocation \
          --command-id "${LOG_CMD}" --instance-id "${EC2_INSTANCE}" \
          --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null | head -c 200)
        log "  ${POLL_ELAPSED}s — still running | ${TAIL}"
      fi
    else
      log "  ${POLL_ELAPSED}s — polling..."
    fi
  done

  if [[ "$BUILD_DONE" != "true" ]]; then
    fail "Build timed out after 30 minutes — check EC2: tail /tmp/axerp-deploy-run.log"
  fi

  # Show final deploy log
  LOG_CMD=$(aws ssm send-command \
    --instance-ids "${EC2_INSTANCE}" \
    --document-name "AWS-RunShellScript" \
    --parameters "{\"commands\":[\"tail -40 /tmp/axerp-deploy-run.log\"],\"executionTimeout\":[\"30\"]}" \
    --timeout-seconds 60 \
    --region "${AWS_REGION}" \
    --query "Command.CommandId" --output text)
  sleep 8
  echo "── EC2 deploy log (tail) ──────────────────────────────"
  aws ssm get-command-invocation \
    --command-id "${LOG_CMD}" --instance-id "${EC2_INSTANCE}" \
    --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null
  echo "────────────────────────────────────────────────────────"
fi
ok "Step 3 complete"
echo ""

# ── Step 4: Final external health check ──────────────────────────────────────
log "Step 4/6 — External health checks from local machine"

CHECKS_PASSED=0
CHECKS_FAILED=0

check_url() {
  local label="$1"
  local url="$2"
  local expected="${3:-200}"
  if $DRY_RUN; then
    echo "  [dry-run] check: ${label}"
    return
  fi
  local code
  code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 "${url}" 2>/dev/null || echo "000")
  if [[ "$code" == "$expected" ]]; then
    ok "  ${label}: ${code}"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    warn "  ${label}: ${code} (expected ${expected})"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
  fi
}

check_url "ping"         "https://${SITE}/api/method/ping"
check_url "login page"   "https://${SITE}/login"
check_url "desk"         "https://${SITE}/app"  "302"

# Asset spot-check: resolve current hashes from the running backend
if ! $DRY_RUN && ! $SKIP_BUILD; then
  log "  Fetching current asset hashes from EC2..."
  HASH_CMD_ID=$(aws ssm send-command \
    --instance-ids "${EC2_INSTANCE}" \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["docker exec axerp-backend python3 -c \"import json; d=json.load(open(\047/home/frappe/frappe-bench/sites/assets/assets.json\047)); [print(k+\047:\047+v) for k,v in d.items() if any(k.startswith(p) for p in [\047desk.bundle\047,\047login.bundle\047,\047hrms.bundle\047,\047erpnext.bundle\047])]\" 2>/dev/null"]}' \
    --region "${AWS_REGION}" \
    --query "Command.CommandId" \
    --output text 2>/dev/null || echo "")

  if [[ -n "$HASH_CMD_ID" ]]; then
    sleep 8
    HASH_OUTPUT=$(aws ssm get-command-invocation \
      --command-id "${HASH_CMD_ID}" \
      --instance-id "${EC2_INSTANCE}" \
      --region "${AWS_REGION}" \
      --query "StandardOutputContent" \
      --output text 2>/dev/null || echo "")
    while IFS=":" read -r key path; do
      [[ -z "$path" ]] && continue
      check_url "  asset: ${key}" "https://${SITE}${path}"
    done <<< "$HASH_OUTPUT"
  fi
fi

echo ""
if ! $DRY_RUN; then
  log "Health check summary: ${CHECKS_PASSED} passed, ${CHECKS_FAILED} failed"
  if [[ $CHECKS_FAILED -gt 0 ]]; then
    warn "Some checks failed — review output above."
  fi
fi

# ── Step 5: Update GitHub PR ──────────────────────────────────────────────────
log "Step 5/6 — Checking open PR status"
if ! $DRY_RUN; then
  OPEN_PRS=$(gh pr list --repo axinagroup/axerp --base production --state open --json number,title --jq '.[].number' 2>/dev/null || echo "")
  if [[ -n "$OPEN_PRS" ]]; then
    log "  Open PRs targeting production: ${OPEN_PRS}"
    log "  Merge at: https://github.com/axinagroup/axerp/pulls"
  else
    log "  No open PRs targeting production"
  fi
fi

# ── Step 6: Summary ───────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
if $DRY_RUN; then
  echo "  DRY RUN complete — no changes made"
else
  echo "  DEPLOY COMPLETE"
  echo "  Image:   ${IMAGE_TAG}"
  echo "  Site:    https://${SITE}"
  echo "  Checks:  ${CHECKS_PASSED} passed / ${CHECKS_FAILED} failed"
fi
echo "══════════════════════════════════════════════════════"
