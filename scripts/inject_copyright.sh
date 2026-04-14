#!/bin/bash
# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.

COPYRIGHT_PY="# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved."
COPYRIGHT_JS="/* Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved. */"

# Move to repo root (assuming script is in /scripts)
cd "$(dirname "$0")/.." || exit

echo "🛡️  Injecting proprietary copyrights..."

# Target Python files
find . -type f -name "*.py" ! -path "*/.*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" | while read -r file; do
  if ! grep -q "Axina Group Inc" "$file"; then
    # Use a temp file to safely prepend (works on both macOS and Linux)
    if head -n 1 "$file" | grep -q "^#!"; then
      # If first line is a shebang, insert after it
      { head -n 1 "$file"; printf '%s\n' "$COPYRIGHT_PY"; tail -n +2 "$file"; } > "$file.tmp"
    else
      { printf '%s\n' "$COPYRIGHT_PY"; cat "$file"; } > "$file.tmp"
    fi
    mv "$file.tmp" "$file"
  fi
done

# Target JS files
# CRITICAL: Do NOT use echo -e, it interprets \n in file content and corrupts JS strings.
# Use printf + cat with a temp file instead.
find . -type f -name "*.js" ! -path "*/.*" ! -path "*/node_modules/*" | while read -r file; do
  if ! grep -q "Axina Group Inc" "$file"; then
    { printf '%s\n' "$COPYRIGHT_JS"; cat "$file"; } > "$file.tmp"
    mv "$file.tmp" "$file"
  fi
done

echo "✅ Copyright injection complete."
