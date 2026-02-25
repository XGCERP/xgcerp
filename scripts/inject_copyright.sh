#!/bin/bash

# Define copyright strings based on XGC Corp details
COPYRIGHT_PY="# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved."
COPYRIGHT_JS="/* Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved. */"

echo "Injecting copyrights into XGCERP..."

# Inject into Python files
find . -type f -name "*.py" ! -path "*/\.*" | while read -r file; do
  # Check if copyright already exists to prevent duplication
  if ! grep -q "XGC CORP" "$file"; then
    # Prepend the copyright and rewrite the file
    echo -e "$COPYRIGHT_PY\n$(cat "$file")" > "$file"
    echo "Injected PY: $file"
  fi
done

# Inject into JavaScript files
find . -type f -name "*.js" ! -path "*/\.*" | while read -r file; do
  if ! grep -q "XGC CORP" "$file"; then
    echo -e "$COPYRIGHT_JS\n$(cat "$file")" > "$file"
    echo "Injected JS: $file"
  fi
done

echo "✅ Copyright injection complete."