#!/usr/bin/env python3
# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.
"""
Fix broken \\n escape sequences in Python files.

The smart_rename.py or inject_copyright.sh pipeline corrupted \\n inside
Python string literals into actual newlines, breaking 87+ .py files with
'unterminated string literal' SyntaxErrors.

This script detects lines ending inside an unterminated regular string
(single or double quoted, NOT triple-quoted) and rejoins them with \\n.
"""

import os
import re
import py_compile


def fix_broken_newlines_in_py(content):
    """
    Fix Python files where \\n inside regular string literals
    was replaced with actual newlines.
    
    Strategy: Walk through lines. If a line ends with an unterminated
    single or double quoted string, the next line was originally part
    of that string (joined by \\n). Rejoin them.
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line ends inside an unterminated regular string
        if is_unterminated_string(line):
            # Collect continuation lines until the string is closed
            combined = line
            i += 1
            while i < len(lines):
                combined = combined + '\\n' + lines[i]
                if not is_unterminated_string(combined):
                    break
                i += 1
            result.append(combined)
        else:
            result.append(line)
        i += 1
    
    return '\n'.join(result)


def is_unterminated_string(line):
    """
    Check if a line ends inside an unterminated single or double quoted string.
    
    We track quote state character by character, handling:
    - Escaped quotes (\\", \\')
    - Triple-quoted strings (which CAN span lines legitimately)
    - Mixing of quote types
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    
    i = 0
    in_string = None  # None, or the quote character (' or ")
    in_triple = False
    
    while i < len(stripped):
        ch = stripped[i]
        
        if in_string is None:
            # Not inside a string - look for string openers
            if ch == '#':
                # Rest of line is a comment
                return False
            if ch in ('"', "'"):
                # Check for triple quote
                if stripped[i:i+3] in ('"""', "'''"):
                    in_string = ch
                    in_triple = True
                    i += 3
                    continue
                else:
                    in_string = ch
                    in_triple = False
                    i += 1
                    continue
        else:
            # Inside a string
            if ch == '\\':
                # Skip escaped character
                i += 2
                continue
            if in_triple:
                triple = ch * 3
                if stripped[i:i+3] == triple and ch == in_string:
                    in_string = None
                    in_triple = False
                    i += 3
                    continue
            else:
                if ch == in_string:
                    in_string = None
                    i += 1
                    continue
        i += 1
    
    # If we're inside a non-triple-quoted string at end of line, it's unterminated
    return in_string is not None and not in_triple


def process_file(filepath):
    """Process a single Python file and fix broken newlines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed = fix_broken_newlines_in_py(content)
        
        if fixed != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")
        return False


def main():
    print("🔧 Fixing broken \\n in Python files...")
    
    fixed_count = 0
    still_broken = []
    
    for root, dirs, files in os.walk('erpnext'):
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'node_modules'}]
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                # First check if file is broken
                try:
                    py_compile.compile(path, doraise=True)
                    continue  # File is fine
                except py_compile.PyCompileError as e:
                    if 'unterminated string' not in str(e):
                        continue  # Different error, skip
                
                # Try to fix it
                if process_file(path):
                    # Verify the fix worked
                    try:
                        py_compile.compile(path, doraise=True)
                        fixed_count += 1
                        print(f"  ✅ Fixed: {path}")
                    except py_compile.PyCompileError:
                        still_broken.append(path)
                        print(f"  ⚠️  Partially fixed but still broken: {path}")
                else:
                    still_broken.append(path)
                    print(f"  ❌ Could not fix: {path}")
    
    print(f"\n✨ Fixed {fixed_count} files")
    if still_broken:
        print(f"⚠️  {len(still_broken)} files still broken:")
        for p in still_broken:
            print(f"  - {p}")


if __name__ == '__main__':
    main()
