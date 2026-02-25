#!/bin/bash
# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.

if [ -z "$1" ]; then
  echo "❌ Error: Please provide the upstream tag (e.g., v16.7.0)"
  exit 1
fi

UPSTREAM_TAG=$1
XGC_TAG="${UPSTREAM_TAG}-xgc"
SCRIPT_DIR="$(dirname "$0")"

echo "🔄 Syncing XGCERP with $UPSTREAM_TAG..."

# 1. Fetch
git fetch upstream --tags

# 2. Merge upstream tag
# We use --no-ff and a message to create a distinct merge commit we can later amend
git merge "$UPSTREAM_TAG" --no-ff -m "chore: merge upstream $UPSTREAM_TAG and apply XGC branding"

if [ $? -ne 0 ]; then
  echo "⚠️  Conflicts detected. Fix them, then run scripts/smart_rename.py and scripts/inject_copyright.sh manually."
  exit 1
fi

# 3. Apply Rebrand & Copyrights
echo "✨ Applying XGCERP Hard Rebrand and Assets..."
python3 "$SCRIPT_DIR/smart_rename.py"
bash "$SCRIPT_DIR/inject_copyright.sh"

# 4. Amend the Merge Commit
# This combines the rebranding changes into the merge commit itself
echo "💾 Amending commit with proprietary layer..."
git add .
git commit --amend --no-edit

# 5. Tag or Re-tag the release
echo "🏷️  Tagging release as $XGC_TAG..."
git tag -f "$XGC_TAG"

# 6. Push to origin (Force required because we amended the history)
echo "🚀 Force-pushing branch and tags to XGCERP origin..."
git push origin version-16 --force
git push origin "$XGC_TAG" --force

# 7. Refresh Bench (If on server)
if command -v bench &> /dev/null; then
    echo "🏗️  Refreshing local bench environment..."
    bench clear-cache
    bench migrate
fi

echo "✅ XGCERP is now fully branded and synced to $XGC_TAG"