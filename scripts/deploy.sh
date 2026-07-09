#!/bin/bash
# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.
#
# AXERP Deploy Script — build on EC2, push to ECR, deploy via compose.
#
# Flow:
#   1. Package production branch → upload to S3 (source tarball)
#   2. Upload compose file → S3
#   3. Stage build + launch scripts on EC2 via SSM
#   4. EC2 builds image, pushes to ECR (010438486646.dkr.ecr.us-east-1.amazonaws.com/axerp)
#   5. EC2 docker compose up -d (pulls from ECR)
#   6. migrate service runs bench migrate + bench build --production
#   7. fix-assets-json.sh syncs assets backend→frontend, verifies 200s
#   8. Health checks from local machine
#
# Usage:
#   bash scripts/deploy.sh              # full deploy
#   bash scripts/deploy.sh --dry-run    # preview without executing
#   bash scripts/deploy.sh --skip-build # skip build, just redeploy + asset fix
#
# Prerequisites: aws CLI configured with ECR access, gh CLI authenticated.

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
EC2_INSTANCE="i-07bb8581203e52527"
AWS_REGION="us-east-1"
AWS_ACCOUNT="010438486646"
ECR_REGISTRY="${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPO="${ECR_REGISTRY}/axerp"
S3_BUCKET="axina-openproject-files"
S3_PREFIX="deploy"
SITE="erp.tspgusa.com"
COMPOSE_LOCAL="infrastructure/docker/docker-compose.axerp.yml"

DRY_RUN=false
SKIP_BUILD=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]]    && DRY_RUN=true
  [[ "$arg" == "--skip-build" ]] && SKIP_BUILD=true
done

# ── Helpers ───────────────────────────────────────────────────────────────────
log()  { echo "$(date -u +%H:%M:%S) ▶ $*"; }
ok()   { echo "$(date -u +%H:%M:%S) ✅ $*"; }
warn() { echo "$(date -u +%H:%M:%S) ⚠️  $*"; }
fail() { echo "$(date -u +%H:%M:%S) ❌ $*" >&2; exit 1; }

run() { $DRY_RUN && echo "  [dry-run] $*" || "$@"; }

ssm_run() {
  local description="$1"; shift
  local commands=("$@")
  log "${description}..."
  if $DRY_RUN; then echo "  [dry-run] SSM: ${commands[*]}"; return 0; fi

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
    --query "Command.CommandId" --output text)
  log "  SSM: ${cmd_id}"

  local status="InProgress" elapsed=0
  while [[ "$status" == "InProgress" || "$status" == "Pending" ]]; do
    sleep 10; elapsed=$((elapsed + 10))
    status=$(aws ssm get-command-invocation \
      --command-id "${cmd_id}" --instance-id "${EC2_INSTANCE}" \
      --region "${AWS_REGION}" --query "Status" --output text 2>/dev/null || echo "Pending")
    echo "  ${elapsed}s — ${status}"
    [[ $elapsed -ge 600 ]] && fail "SSM timed out after 10 min"
  done

  local out
  out=$(aws ssm get-command-invocation \
    --command-id "${cmd_id}" --instance-id "${EC2_INSTANCE}" \
    --region "${AWS_REGION}" --query "[StandardOutputContent,StandardErrorContent]" --output text)
  echo "── SSM output ──────────────────────────────────"
  echo "$out"
  echo "────────────────────────────────────────────────"
  [[ "$status" != "Success" ]] && fail "SSM failed: ${status}"
}

poll_background_build() {
  log "Polling EC2 build (allow ~25 min)..."
  local elapsed=0
  while [[ $elapsed -lt 1800 ]]; do
    sleep 30; elapsed=$((elapsed + 30))

    local poll_id
    poll_id=$(aws ssm send-command \
      --instance-ids "${EC2_INSTANCE}" \
      --document-name "AWS-RunShellScript" \
      --parameters '{"commands":["cat /tmp/axerp-deploy-status 2>/dev/null || echo RUNNING"]}' \
      --region "${AWS_REGION}" \
      --query "Command.CommandId" --output text 2>/dev/null || echo "")
    [[ -z "$poll_id" ]] && { log "  ${elapsed}s — polling..."; continue; }

    sleep 8
    local val
    val=$(aws ssm get-command-invocation \
      --command-id "${poll_id}" --instance-id "${EC2_INSTANCE}" \
      --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null | tr -d '[:space:]')

    if [[ "$val" == "0" ]]; then
      ok "Build completed (${elapsed}s)"
      return 0
    elif [[ "$val" =~ ^[1-9][0-9]*$ ]]; then
      # Build failed — fetch log
      local log_id
      log_id=$(aws ssm send-command \
        --instance-ids "${EC2_INSTANCE}" --document-name "AWS-RunShellScript" \
        --parameters '{"commands":["tail -50 /tmp/axerp-deploy-run.log"]}' \
        --region "${AWS_REGION}" --query "Command.CommandId" --output text 2>/dev/null || echo "")
      sleep 8
      echo "── Build log (tail) ────────────────────────────"
      [[ -n "$log_id" ]] && aws ssm get-command-invocation \
        --command-id "${log_id}" --instance-id "${EC2_INSTANCE}" \
        --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null
      echo "────────────────────────────────────────────────"
      fail "EC2 build failed (exit ${val}) after ${elapsed}s"
    else
      # Still running — show tail
      local tail_id
      tail_id=$(aws ssm send-command \
        --instance-ids "${EC2_INSTANCE}" --document-name "AWS-RunShellScript" \
        --parameters '{"commands":["tail -3 /tmp/axerp-deploy-run.log 2>/dev/null | tr \"\\n\" \"|\" | head -c 200"]}' \
        --region "${AWS_REGION}" --query "Command.CommandId" --output text 2>/dev/null || echo "")
      sleep 8
      local tail=""
      [[ -n "$tail_id" ]] && tail=$(aws ssm get-command-invocation \
        --command-id "${tail_id}" --instance-id "${EC2_INSTANCE}" \
        --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null | head -c 200)
      log "  ${elapsed}s — building | ${tail}"
    fi
  done
  fail "Build timed out after 30 min — check EC2: tail /tmp/axerp-deploy-run.log"
}

# ── Preflight ─────────────────────────────────────────────────────────────────
log "Preflight..."
command -v aws >/dev/null 2>&1 || fail "aws CLI not found"
command -v gh  >/dev/null 2>&1 || fail "gh CLI not found"
command -v git >/dev/null 2>&1 || fail "git not found"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

CURRENT_BRANCH=$(git branch --show-current)
[[ "$CURRENT_BRANCH" != "production" ]] && warn "On branch ${CURRENT_BRANCH} — packaging origin/production"

# Detect image tag from Dockerfile comment line
IMAGE_TAG=$(grep "axerp:v" docker/Dockerfile | grep -v "^#.*ARG" | head -1 | \
  sed -E 's/.*-t (axerp:v[^ ]+).*/\1/' | grep -v "^$" || echo "")
[[ -z "$IMAGE_TAG" ]] && IMAGE_TAG="axerp:$(grep '^ARG ERPNEXT_VERSION=' docker/Dockerfile | cut -d= -f2)-axerp.1"
ECR_IMAGE="${ECR_REPO}:${IMAGE_TAG#axerp:}"
ECR_IMAGE_PROD="${ECR_REPO}:prod"

log "Image tag:  ${IMAGE_TAG}"
log "ECR image:  ${ECR_IMAGE}"
log "Site:       ${SITE}"
log "EC2:        ${EC2_INSTANCE}"
$DRY_RUN && warn "DRY RUN — no changes"
echo ""

# ── Step 1: Package production branch ────────────────────────────────────────
log "Step 1/7 — Package production branch → S3"

run git archive origin/production \
  --format=tar.gz -o /tmp/axerp-production.tar.gz --prefix=axerp/ 2>/dev/null || {
  warn "Fetching origin/production..."
  run git fetch origin production
  run git archive origin/production \
    --format=tar.gz -o /tmp/axerp-production.tar.gz --prefix=axerp/
}

log "  Tarball: $(du -sh /tmp/axerp-production.tar.gz 2>/dev/null | cut -f1)"
run aws s3 cp /tmp/axerp-production.tar.gz \
  "s3://${S3_BUCKET}/${S3_PREFIX}/axerp-production.tar.gz" --quiet

[[ -f "${COMPOSE_LOCAL}" ]] && \
  run aws s3 cp "${COMPOSE_LOCAL}" \
    "s3://${S3_BUCKET}/${S3_PREFIX}/docker-compose.axerp.yml" --quiet && \
  ok "Compose uploaded" || warn "Compose not found at ${COMPOSE_LOCAL}"

ok "Step 1 complete"
echo ""

# ── Step 2: Generate build script ─────────────────────────────────────────────
log "Step 2/7 — Generate build + launcher scripts"

# Main build script — runs on EC2, builds image, pushes to ECR, deploys
cat > /tmp/axerp-deploy-run.sh << EOBUILD
#!/bin/bash
set -e
IMAGE_TAG="${IMAGE_TAG}"
ECR_IMAGE="${ECR_IMAGE}"
ECR_IMAGE_PROD="${ECR_IMAGE_PROD}"
ECR_REGISTRY="${ECR_REGISTRY}"
SITE="${SITE}"
AWS_REGION="${AWS_REGION}"
S3_BUCKET="${S3_BUCKET}"
S3_PREFIX="${S3_PREFIX}"

echo "[1] Fetch source + compose from S3..."
aws s3 cp s3://\${S3_BUCKET}/\${S3_PREFIX}/axerp-production.tar.gz /tmp/axerp-production.tar.gz --quiet
aws s3 cp s3://\${S3_BUCKET}/\${S3_PREFIX}/docker-compose.axerp.yml /opt/openproject/docker-compose.axerp.yml --quiet
echo "  tarball: \$(du -sh /tmp/axerp-production.tar.gz | cut -f1)"

echo "[2] Extract source..."
rm -rf /tmp/axerp-build && mkdir -p /tmp/axerp-build
tar -xzf /tmp/axerp-production.tar.gz -C /tmp/axerp-build --strip-components=1

echo "[3] ECR login..."
aws ecr get-login-password --region \${AWS_REGION} | \
  docker login --username AWS --password-stdin \${ECR_REGISTRY}

echo "[4] Build \${IMAGE_TAG} (arm64, no-cache)..."
echo "  start: \$(date -u +%H:%M:%S)"
cd /tmp/axerp-build
docker build \\
  --platform linux/arm64 \\
  --no-cache \\
  -f docker/Dockerfile \\
  -t \${IMAGE_TAG} \\
  -t axerp:prod \\
  -t \${ECR_IMAGE} \\
  -t \${ECR_IMAGE_PROD} \\
  . > /tmp/docker-build.log 2>&1
BUILD_EXIT=\$?
echo "  end:   \$(date -u +%H:%M:%S) | exit: \${BUILD_EXIT}"
if [ \${BUILD_EXIT} -ne 0 ]; then
  echo "BUILD FAILED — last 40 lines:"
  tail -40 /tmp/docker-build.log
  exit 1
fi
echo "  \$(tail -1 /tmp/docker-build.log)"

echo "[5] Push to ECR..."
docker push \${ECR_IMAGE}
docker push \${ECR_IMAGE_PROD}
echo "  Pushed: \${ECR_IMAGE}"

echo "[6] Update compose image tag to ECR URI..."
sed -i "s|image: axerp:.*|image: \${ECR_IMAGE}|g" /opt/openproject/docker-compose.axerp.yml

echo "[7] Pull fresh from ECR on this host (validates push)..."
docker pull \${ECR_IMAGE}

echo "[8] Deploy stack..."
cd /opt/openproject
docker compose -f docker-compose.axerp.yml up -d 2>&1 | grep -vE "^(Pulling|pulled)" | head -30

echo "[9] Wait 25s for containers..."
sleep 25
docker ps --filter "name=axerp" --format "  {{.Names}} | {{.Status}}" | sort

echo "[10] Wait for migrate to complete..."
MIGRATE_DEADLINE=\$(( \$(date +%s) + 600 ))
while docker ps -a --filter "name=axerp-migrate" --filter "status=running" \
  --format "{{.Names}}" 2>/dev/null | grep -q axerp-migrate; do
  [ \$(date +%s) -gt \${MIGRATE_DEADLINE} ] && { echo "  WARN: migrate timeout"; break; }
  sleep 10
done
MIGRATE_EXIT=\$(docker inspect axerp-migrate --format "{{.State.ExitCode}}" 2>/dev/null || echo "?")
echo "  migrate exit: \${MIGRATE_EXIT}"
docker logs axerp-migrate 2>&1 | tail -15
if [ "\${MIGRATE_EXIT}" != "0" ] && [ "\${MIGRATE_EXIT}" != "?" ]; then
  echo "ERROR: migration failed"
  exit 1
fi

echo "[11] Asset fix..."
aws s3 cp s3://\${S3_BUCKET}/\${S3_PREFIX}/axerp-fix-assets-json.sh /tmp/axerp-fix-assets-json.sh --quiet
SITE=\${SITE} bash /tmp/axerp-fix-assets-json.sh

echo "[12] Ping..."
CODE=\$(curl -sk -o /dev/null -w "%{http_code}" "https://\${SITE}/api/method/ping")
[ "\${CODE}" = "200" ] && echo "  PASS: \${SITE} 200" || echo "  WARN: \${SITE} returned \${CODE}"

echo "[13] Clean old local images (keep ECR copies)..."
for OLD in axerp:v16.25.0-axerp.2 axerp:v16.25.0-axerp.1 axerp:v16.23.0-axerp.4 axerp:v16.23.0-axerp.2; do
  docker rmi \${OLD} 2>/dev/null && echo "  Removed \${OLD}" || true
done
docker images axerp --format "  {{.Repository}}:{{.Tag}} | {{.Size}}"

echo "=== DEPLOY COMPLETE ==="
EOBUILD

# Launcher — runs build script in background subshell, writes exit code to status file
cat > /tmp/axerp-launch.sh << 'EOLAUNCH'
#!/bin/bash
rm -f /tmp/axerp-deploy-status /tmp/axerp-deploy-run.log
(
  bash /tmp/axerp-deploy-run.sh > /tmp/axerp-deploy-run.log 2>&1
  echo $? > /tmp/axerp-deploy-status
) &
BGPID=$!
echo "Launched build PID $BGPID"
disown $BGPID
EOLAUNCH

if ! $DRY_RUN; then
  aws s3 cp /tmp/axerp-deploy-run.sh "s3://${S3_BUCKET}/${S3_PREFIX}/axerp-deploy-run.sh" --quiet
  aws s3 cp /tmp/axerp-launch.sh "s3://${S3_BUCKET}/${S3_PREFIX}/axerp-launch.sh" --quiet
fi
ok "Step 2 complete"
echo ""

# ── Step 3: Build + push on EC2 ───────────────────────────────────────────────
if $SKIP_BUILD; then
  warn "Step 3/7 — Skipped (--skip-build)"
else
  ssm_run "Step 3a/7 — Stage scripts on EC2" \
    "aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-deploy-run.sh /tmp/axerp-deploy-run.sh --quiet" \
    "aws s3 cp s3://${S3_BUCKET}/${S3_PREFIX}/axerp-launch.sh /tmp/axerp-launch.sh --quiet" \
    "chmod +x /tmp/axerp-deploy-run.sh /tmp/axerp-launch.sh" \
    "rm -f /tmp/axerp-deploy-status"

  ssm_run "Step 3b/7 — Launch background build" \
    "bash /tmp/axerp-launch.sh" \
    "sleep 5" \
    "pgrep -f axerp-deploy-run.sh && echo 'BUILD RUNNING' || echo 'NOT RUNNING'"

  if ! $DRY_RUN; then
    poll_background_build
    # Show final log tail
    FINAL_LOG_ID=$(aws ssm send-command \
      --instance-ids "${EC2_INSTANCE}" --document-name "AWS-RunShellScript" \
      --parameters '{"commands":["tail -30 /tmp/axerp-deploy-run.log"]}' \
      --region "${AWS_REGION}" --query "Command.CommandId" --output text)
    sleep 8
    echo "── EC2 deploy log (tail) ────────────────────────────"
    aws ssm get-command-invocation \
      --command-id "${FINAL_LOG_ID}" --instance-id "${EC2_INSTANCE}" \
      --region "${AWS_REGION}" --query "StandardOutputContent" --output text 2>/dev/null
    echo "────────────────────────────────────────────────────"
  fi
fi
ok "Step 3 complete"
echo ""

# ── Step 4: External health checks ───────────────────────────────────────────
log "Step 4/7 — External health checks"
CHECKS_PASSED=0; CHECKS_FAILED=0

check_url() {
  local label="$1" url="$2" expected="${3:-200}"
  if $DRY_RUN; then echo "  [dry-run] check: ${label}"; return; fi
  local code
  code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 "${url}" 2>/dev/null || echo "000")
  if [[ "$code" == "$expected" ]]; then
    ok "  ${label}: ${code}"; CHECKS_PASSED=$((CHECKS_PASSED + 1))
  else
    warn "  ${label}: ${code} (expected ${expected})"; CHECKS_FAILED=$((CHECKS_FAILED + 1))
  fi
}

check_url "ping"       "https://${SITE}/api/method/ping"
check_url "login page" "https://${SITE}/login"
check_url "desk"       "https://${SITE}/app" "302"

echo ""
log "Health checks: ${CHECKS_PASSED} passed / ${CHECKS_FAILED} failed"
[[ $CHECKS_FAILED -gt 0 ]] && warn "Some checks failed"

# ── Step 5: ECR image verification ────────────────────────────────────────────
log "Step 5/7 — Verify ECR image pushed"
if ! $DRY_RUN; then
  aws ecr describe-images \
    --repository-name axerp \
    --region "${AWS_REGION}" \
    --query "sort_by(imageDetails, &imagePushedAt)[-3:] | reverse(@) | \
      [].{tag: imageTag[0], pushed: imagePushedAt, size: imageSizeInBytes}" \
    --output table 2>/dev/null || warn "Could not query ECR"
fi

# ── Step 6: GitHub release ────────────────────────────────────────────────────
log "Step 6/7 — Create GitHub release for ${IMAGE_TAG}"
if ! $DRY_RUN; then
  # Only create if no release exists for this tag
  EXISTING=$(gh api "repos/axinagroup/axerp/releases/tags/${IMAGE_TAG#axerp:}" \
    --jq '.tag_name' 2>/dev/null || echo "")
  if [[ -z "$EXISTING" ]]; then
    ERPNEXT_VER=$(grep '^ARG ERPNEXT_VERSION=' docker/Dockerfile | cut -d= -f2)
    gh release create "${IMAGE_TAG#axerp:}" \
      --repo axinagroup/axerp \
      --title "AXERP ${IMAGE_TAG#axerp:}" \
      --notes "## ${IMAGE_TAG}

Built from upstream ERPNext ${ERPNEXT_VER} with AXERP branding.
ECR: \`${ECR_IMAGE}\`

### Apps
- frappe (base image ${ERPNEXT_VER})
- erpnext/AXERP (production branch)
- hrms (version-16)
- crm (main)
- insights (develop)
- wiki (version-3)
- blog (develop)" \
      --latest
    ok "GitHub release created: ${IMAGE_TAG#axerp:}"
  else
    log "  Release already exists for ${IMAGE_TAG#axerp:}"
  fi
fi

# ── Step 7: Summary ───────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
if $DRY_RUN; then
  echo "  DRY RUN complete"
else
  echo "  DEPLOY COMPLETE"
  echo "  Image:  ${IMAGE_TAG}"
  echo "  ECR:    ${ECR_IMAGE}"
  echo "  Site:   https://${SITE}"
  echo "  Checks: ${CHECKS_PASSED} passed / ${CHECKS_FAILED} failed"
fi
echo "══════════════════════════════════════════════════════════"
