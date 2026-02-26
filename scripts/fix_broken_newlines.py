#!/usr/bin/env python3
# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.
"""
Fix broken \\n escape sequences in JS files.

The original rebranding copyright injection used `echo -e` which interpreted
\\n escape sequences inside JS string literals as actual newlines.

This script finds patterns where a double-quoted or single-quoted string
is broken across lines and rejoins them with \\n.

IMPORTANT: Template literals (backtick strings) are intentionally IGNORED
because they can legitimately span multiple lines in JavaScript.
"""

import os
import sys


def is_unterminated_regular_string(line):
    """
    Check if a line ends inside an unterminated double-quoted or single-quoted string.
    Backtick template literals are IGNORED (they can span multiple lines legally).
    """
    stripped = line.rstrip()
    if not stripped:
        return False

    in_double = False
    in_single = False
    in_template = False
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        # Skip escaped characters
        if ch == '\\' and i + 1 < len(stripped) and not in_template:
            i += 2
            continue
        # Track template literals (backticks) — skip over them entirely
        if ch == '`' and not in_double and not in_single:
            in_template = not in_template
        elif not in_template:
            if ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "'" and not in_double:
                in_single = not in_single
        i += 1

    # Only flag double or single quoted strings as unterminated
    # Template literals spanning lines are valid JS
    return in_double or in_single


def fix_broken_newlines(content):
    """
    Fix JS files where \\n inside regular string literals (double/single quoted)
    was replaced with actual newlines.
    """
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        if is_unterminated_regular_string(line):
            # Collect continuation lines until the string is closed
            combined = line
            j = i + 1
            max_join = 50  # Safety limit to avoid runaway joins
            joined = 0
            while j < len(lines) and joined < max_join:
                next_line = lines[j]
                combined = combined + '\\n' + next_line
                j += 1
                joined += 1
                if not is_unterminated_regular_string(combined):
                    break
            result.append(combined)
            i = j
        else:
            result.append(line)
            i += 1

    return '\n'.join(result)


def process_file(filepath):
    """Process a single JS file and fix broken newlines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        has_broken = False
        for line in content.split('\n'):
            if is_unterminated_regular_string(line):
                has_broken = True
                break

        if not has_broken:
            return False

        fixed = fix_broken_newlines(content)

        if fixed != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True

        return False
    except Exception as e:
        print(f"  ⚠️  Error processing {filepath}: {e}")
        return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    erpnext_dir = os.path.join(root_dir, "erpnext")

    ignore_dirs = {'.git', 'node_modules', '__pycache__', 'env', 'logs'}

    print("🔧 Fixing broken \\n escape sequences in JS files...")

    fixed_count = 0
    scanned = 0

    for dirpath, dirnames, filenames in os.walk(erpnext_dir):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for filename in filenames:
            if filename.endswith('.js'):
                filepath = os.path.join(dirpath, filename)
                scanned += 1

                if process_file(filepath):
                    fixed_count += 1
                    print(f"  ✅ Fixed: {os.path.relpath(filepath, root_dir)}")

    print(f"\n✨ Done! Scanned {scanned} JS files, fixed {fixed_count}")


if __name__ == '__main__':
    main()
