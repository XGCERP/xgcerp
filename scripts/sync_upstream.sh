#!/bin/bash

# Ensure a tag version was provided
if [ -z "$1" ]; then
  echo "❌ Error: Please provide the upstream tag to sync."
  echo "Usage: ./sync_upstream.sh v16.7.0"
  exit 1
fi

UPSTREAM_TAG=$1
XGC_TAG="${UPSTREAM_TAG}-xgc"

echo "🔄 Starting XGCERP Sync Protocol for $UPSTREAM_TAG..."

# 1. Fetch upstream tags
echo "📥 Fetching upstream tags..."
git fetch upstream --tags

# 2. Merge the specific tag
echo "🔀 Merging $UPSTREAM_TAG..."
git merge $UPSTREAM_TAG -m "Merge upstream tag $UPSTREAM_TAG"

# Check for merge conflicts
if [ $? -ne 0 ]; then
  echo "⚠️ Merge conflicts detected! Please resolve them manually, then run the branding scripts and commit."
  exit 1
fi

# 3. Apply Branding and Copyrights
echo "✨ Applying XGCERP Core Masking and Copyrights..."
python3 smart_rename.py
./inject_copyright.sh

# 4. Commit the changes
echo "💾 Committing proprietary layer..."
git add .
git commit -m "chore: apply XGCERP branding and copyrights for $UPSTREAM_TAG"

# 5. Tag the release
echo "🏷️ Tagging release as $XGC_TAG..."
git tag $XGC_TAG

# 6. Push to origin
echo "🚀 Pushing branch and tags to XGCERP origin..."
git push origin version-16
git push origin $XGC_TAG

echo "✅ Sync for $XGC_TAG complete! Ready for deployment."