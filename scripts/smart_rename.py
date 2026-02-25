# Copyright (c) 2026 XGC CORP. Created by Daniel Brody. All rights reserved.
import os
import shutil

# --- CONFIGURATION ---
OLD_BRAND = "XGCERP"
NEW_BRAND = "XGCERP"

NEW_PUBLISHER = "XGC CORP."
NEW_DESCRIPTION = "Operating System for Carbon Sovereignty"
NEW_EMAIL = "db@xgccorp.com"

# The path to your logo (assuming it's in the repo root)
SOURCE_LOGO_NAME = "xgcerp-logo.svg"

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'env', 'logs'}
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
                    f.write(f'source_link = "https://github.com/XGCERP/xgcerp"\n')
                else:
                    # Fallback global replace for the rest of the file
                    f.write(line.replace(OLD_BRAND, NEW_BRAND))
        print(f"✅ Metadata updated in hooks.py")
    except Exception as e:
        print(f"❌ Error updating hooks.py: {e}")

def run_rebrand():
    # Resolve root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    
    # 1. Update hooks.py metadata
    hooks_path = os.path.join(root_dir, "erpnext", "hooks.py")
    update_hooks_metadata(hooks_path)

    # 2. Global UI and Metadata Replace
    print(f"🚀 Starting Rebrand: {OLD_BRAND} -> {NEW_BRAND}")
    updated = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if filename.endswith(TARGET_EXTS):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if OLD_BRAND in content or 'xgccorp.com' in content:
                        new_content = content.replace(OLD_BRAND, NEW_BRAND)
                        new_content = new_content.replace('xgccorp.com', 'xgccorp.com')
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated += 1
                except: pass

    # 3. Overwrite physical logos
    source_logo = os.path.join(root_dir, SOURCE_LOGO_NAME)
    if os.path.exists(source_logo):
        # Target standard XGCERP asset paths
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

    print(f"✨ Rebrand complete. {updated} files modified.")

if __name__ == '__main__':
    run_rebrand()