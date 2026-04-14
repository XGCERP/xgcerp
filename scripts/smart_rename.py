# Copyright (c) 2026 Axina Group Inc. Created by Daniel Brody. All rights reserved.

import json
import os
import shutil
import re

# --- CONFIGURATION ---
OLD_BRAND = "ERPNext"
NEW_BRAND = "AXERP"

# CRITICAL: Preserve "ERPNext Integrations" module name
# The integrations module MUST remain as "ERPNext Integrations" because:
# 1. The folder is named "erpnext_integrations/" (not renamed)
# 2. All Python imports reference "erpnext.erpnext_integrations.*"
# 3. Renaming this module breaks installation and all existing imports
# This exclusion prevents the bug from recurring on future upstream syncs
PRESERVE_INTEGRATIONS_MODULE = "ERPNext Integrations"

# CRITICAL: Also preserve the Python module path
PRESERVE_PYTHON_MODULE = "erpnext_integrations"

NEW_PUBLISHER = "Axina Group Inc."
NEW_DESCRIPTION = "Operating System for Carbon Sovereignty"
NEW_EMAIL = "db@axinagroup.com"

# The path to your logo (assuming it's in the repo root)
SOURCE_LOGO_NAME = "axinagroup-logo.svg"

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'env', 'logs', 'scripts'}
TARGET_EXTS = ('.json', '.py', '.js', '.html', '.csv', '.txt', '.md')


def update_hooks_metadata(hooks_path):
    """Bakes branding into the core hooks.py file"""
    if not os.path.exists(hooks_path):
        return
    
    try:
        with open(hooks_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        with open(hooks_path, 'w', encoding='utf-8') as f:
            for line in lines:
                # Update specific app metadata
                if 'app_publisher =' in line:
                    f.write(f'app_publisher = "{NEW_PUBLISHER}"\n')
                elif 'app_description =' in line:
                    f.write(f'app_description = "{NEW_DESCRIPTION}"\n')
                elif 'app_email =' in line:
                    f.write(f'app_email = "{NEW_EMAIL}"\n')
                elif 'source_link =' in line:
                    f.write(f'source_link = "https://github.com/AXERP/axerp"\n')
                else:
                    # Fallback global replace for the rest of the file
                    # BUT preserve erpnext_integrations
                    new_line = line.replace(OLD_BRAND, NEW_BRAND)
                    # Restore any erpnext_integrations that got changed
                    new_line = new_line.replace('axerp_integrations', PRESERVE_PYTHON_MODULE)
                    f.write(new_line)
        
        print(f"✅ Metadata updated in hooks.py")
    except Exception as e:
        print(f"❌ Error updating hooks.py: {e}")


def smart_replace(content, filename):
    """
    Smart replacement that preserves erpnext_integrations in all contexts
    and protects escape sequences in JS/JSON files.
    """
    # CRITICAL: Protect ALL backslash escape sequences in ALL file types.
    # The rebranding pipeline corrupted \\n, \\t, etc. inside string literals
    # into actual newlines/tabs, breaking 87+ Python files and JS files.
    # Protect in ALL files unconditionally to prevent any future corruption.
    NEWLINE_MARKER = "___PRESERVE_BACKSLASH_N___"
    TAB_MARKER = "___PRESERVE_BACKSLASH_T___"
    content = content.replace('\\n', NEWLINE_MARKER)
    content = content.replace('\\t', TAB_MARKER)

    # CRITICAL: Protect erpnext_integrations before doing any replacements
    # Use a unique marker that won't appear in normal code
    MARKER = "___PRESERVE_ERPNEXT_INTEGRATIONS___"
    
    # Protect all variations of erpnext_integrations
    # IMPORTANT: Do longer patterns first to avoid partial replacements
    protected = content
    protected = protected.replace('erpnext.erpnext_integrations', f'erpnext.{MARKER}')
    protected = protected.replace('"erpnext_integrations"', f'"{MARKER}"')
    protected = protected.replace("'erpnext_integrations'", f"'{MARKER}'")
    protected = protected.replace('erpnext_integrations', MARKER)
    
    # Special handling for modules.txt
    if filename == 'modules.txt':
        lines = protected.split('\n')
        new_lines = []
        for line in lines:
            # Preserve "ERPNext Integrations" line unchanged
            if PRESERVE_INTEGRATIONS_MODULE in line:
                new_lines.append(line)
            else:
                # Apply rebranding to all other lines
                new_lines.append(line.replace(OLD_BRAND, NEW_BRAND))
        protected = '\n'.join(new_lines)
    
    # Special handling for JSON files to preserve integrations module field
    elif filename.endswith('.json'):
        # Check if this is a DocType JSON with module field
        if '"module":' in protected:
            # Preserve "module": "ERPNext Integrations" patterns
            json_marker = "___PRESERVE_INTEGRATIONS_MODULE___"
            protected = protected.replace(
                f'"module": "{PRESERVE_INTEGRATIONS_MODULE}"',
                f'"module": "{json_marker}"'
            )
            
            # Apply global rebranding
            protected = protected.replace(OLD_BRAND, NEW_BRAND)
            
            # Restore the preserved integrations module
            protected = protected.replace(
                f'"module": "{json_marker}"',
                f'"module": "{PRESERVE_INTEGRATIONS_MODULE}"'
            )
        else:
            # Regular JSON file without module field
            protected = protected.replace(OLD_BRAND, NEW_BRAND)
    
    else:
        # Regular file processing for all other files
        protected = protected.replace(OLD_BRAND, NEW_BRAND)
    
    # Restore all protected erpnext_integrations references
    protected = protected.replace(MARKER, PRESERVE_PYTHON_MODULE)
    
    # Restore protected escape sequences in ALL files
    protected = protected.replace(NEWLINE_MARKER, '\\n')
    protected = protected.replace(TAB_MARKER, '\\t')
    
    return protected


def run_rebrand():
    # Resolve root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    
    # 1. Update hooks.py metadata
    hooks_path = os.path.join(root_dir, "erpnext", "hooks.py")
    update_hooks_metadata(hooks_path)
    
    # 2. Global UI and Metadata Replace
    print(f"🚀 Starting Rebrand: {OLD_BRAND} -> {NEW_BRAND}")
    print(f"🔒 Preserving: {PRESERVE_PYTHON_MODULE} module")
    
    updated = 0
    preserved = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if filename.endswith(TARGET_EXTS):
                filepath = os.path.join(dirpath, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if file needs processing
                    if OLD_BRAND in content or 'axinagroup.com' in content:
                        # Check if file contains erpnext_integrations
                        has_integrations = PRESERVE_PYTHON_MODULE in content
                        
                        # Apply smart replacement
                        new_content = smart_replace(content, filename)
                        
                        # Write back
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        updated += 1
                        
                        if has_integrations:
                            preserved += 1
                            # Verify preservation worked
                            if PRESERVE_PYTHON_MODULE not in new_content:
                                print(f"⚠️  WARNING: {filepath} lost erpnext_integrations!")
                
                except Exception as e:
                    pass  # Skip files that can't be processed
    
    # 3. Overwrite physical logos
    source_logo = os.path.join(root_dir, SOURCE_LOGO_NAME)
    if os.path.exists(source_logo):
        # Target standard AXERP asset paths
        paths = [
            os.path.join(root_dir, "erpnext", "public", "images", "erpnext-logo.svg"),
            os.path.join(root_dir, "erpnext", "public", "images", "erpnext-favicon.svg"),
            os.path.join(root_dir, "erpnext", "public", "images", "v16", "erpnext.svg")
        ]
        
        for target in paths:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(source_logo, target)
        
        print(f"🖼️  Overwrote core logos with {SOURCE_LOGO_NAME}")
    else:
        print(f"⚠️  Logo source not found at {source_logo}")
    
    # 4. Copy raster favicons and site.webmanifest
    raster_favicons = [
        "favicon.ico",
        "favicon-16x16.png",
        "favicon-32x32.png",
        "apple-touch-icon.png",
        "android-chrome-192x192.png",
        "android-chrome-512x512.png",
    ]
    images_dir = os.path.join(root_dir, "erpnext", "public", "images")
    os.makedirs(images_dir, exist_ok=True)

    for fname in raster_favicons:
        src = os.path.join(root_dir, fname)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(images_dir, fname))

    # Copy site.webmanifest with updated icon paths
    manifest_src = os.path.join(root_dir, "site.webmanifest")
    if os.path.exists(manifest_src):
        with open(manifest_src, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for icon in manifest.get("icons", []):
            src_path = icon.get("src", "")
            if src_path and not src_path.startswith("/assets/erpnext/images/"):
                basename = src_path.rsplit("/", 1)[-1]
                icon["src"] = f"/assets/erpnext/images/{basename}"
        with open(os.path.join(images_dir, "site.webmanifest"), "w", encoding="utf-8") as f:
            json.dump(manifest, f)

    print("🖼️  Copied raster favicons and site.webmanifest")
    
    print(f"✨ Rebrand complete!")
    print(f"   📝 {updated} files modified")
    print(f"   🔒 {preserved} files with preserved erpnext_integrations")


if __name__ == '__main__':
    run_rebrand()
