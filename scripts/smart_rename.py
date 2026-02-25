# Copyright (c) 2026 XGC CORP. Created by @dzbrody Daniel Brody. All rights reserved.
import os

# Define the exact case-sensitive strings to swap
OLD_BRAND = "XGCERP"
NEW_BRAND = "XGCERP"

# Directories to ignore to prevent corrupting Git or build files
IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', 'public', 'dist', 'env', 'logs'}
TARGET_EXTS = ('.json', '.py', '.js', '.html', '.csv', '.txt', '.md')

def process_directory(root_dir):
    updated_count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        
        for filename in filenames:
            if filename.endswith(TARGET_EXTS):
                filepath = os.path.join(dirpath, filename)
                if replace_branding(filepath):
                    updated_count += 1
                    
    print(f"
✅ Smart Rename Complete! {updated_count} files updated.")

def replace_branding(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if OLD_BRAND in content:
            # Perform the case-sensitive replace
            new_content = content.replace(OLD_BRAND, NEW_BRAND)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Rebranded metadata in: {filepath}")
            return True
            
    except Exception as e:
        # Silently skip files that cannot be read (e.g., binary files masquerading as text)
        pass
    return False

if __name__ == '__main__':
    print(f"Starting Smart UI and Metadata Rename: {OLD_BRAND} -> {NEW_BRAND}...")
    process_directory('.')
