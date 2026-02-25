#!/bin/bash
# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.

COPYRIGHT_PY="# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved."
COPYRIGHT_JS="/* Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved. */"

# Move to repo root (assuming script is in /scripts)
cd "$(dirname "$0")/.." || exit

echo "🛡️  Injecting proprietary copyrights..."

# Target Python files
find . -type f -name "*.py" ! -path "*/.*" | while read -r file; do
  if ! grep -q "XGC CORP" "$file"; then
    # If first line is a shebang, insert after it. Otherwise, prepend.
    if head -n 1 "$file" | grep -q "^#!"; then
        sed -i '' "2i\\
$COPYRIGHT_PY\\
" "$file"
    else
        sed -i '' "1i\\
$COPYRIGHT_PY\\
" "$file"
    fi
  fi
done

# Target JS files
find . -type f -name "*.js" ! -path "*/.*" | while read -r file; do
  if ! grep -q "XGC CORP" "$file"; then
    echo -e "$COPYRIGHT_JS\n$(cat "$file")" > "$file"
  fi
done

echo "✅ Copyright injection complete."