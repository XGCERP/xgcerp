Here is the comprehensive, step-by-step implementation of the **Core Masking** strategy.

### What is "Core Masking"?

Core Masking is an architectural strategy used when forking massive, frequently updated frameworks like XGCERP. Instead of destroying the original directory structures and variable names (which breaks Git’s ability to merge future updates), you **"mask"** the core system at the presentation and metadata layers.

By executing the three steps below, the underlying code remains structurally identical to `upstream/version-16` (ensuring easy merges), but every touchpoint a user, admin, or developer interacts with screams **XGCERP**.

---

### Step 1: The "Smart UI and Metadata Rename"

This step safely replaces the capitalized word **"XGCERP"** with **"XGCERP"**. This specifically targets Frappe's metadata assignments (DocType modules), Workspace titles, UI Labels, and translation strings, without touching the lowercase `import erpnext` statements.

**1. Create the script:**
In the root of your `xgcerp` repository, create a new file called `smart_rename.py`:

**2. Paste the following Python code:**

```python
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
                    
    print(f"\n✅ Smart Rename Complete! {updated_count} files updated.")

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

```

**3. Run the script:**

```bash
python3 scripts/smart_rename.py

```

---

### Step 2: Copyright Header Injection

*(Note: I have fixed a few minor syntax errors in your bash script where `fi` and `done` were merged on the same line).*

Now that the metadata is rebranded, we will inject the proprietary IP notices for Daniel Brody and XGC CORP into every executable source file.

**1. Create the bash script:**

```bash
nano inject_copyright.sh

```

**2. Paste your corrected code:**

```bash
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

```

**3. Make it executable and run it:**

```bash
chmod +x inject_copyright.sh
./scripts/inject_copyright.sh

```

---

### Step 3: Deep Core Masking via `xgc_theme` App (The Final Layer)

Even after renaming metadata, the core system will still try to load XGCERP logos and default Frappe styling. You must use your custom `xgc_theme` app to override the visual layer at runtime.

In your `xgc_theme` repository, open the `xgc_theme/hooks.py` file and add these Core Masking overrides:

```python
# xgc_theme/hooks.py

# 1. Override Global Application Name
app_title = "XGCERP"
app_description = "Operating System for Carbon Sovereignty"
app_publisher = "XGC CORP."
app_email = "db@xgccorp.com"
app_license = "Proprietary"

# 2. Override Logos and Branding
app_logo_url = "/assets/xgc_theme/images/xgc_logo_dark.svg"
brand_html = "<div><img src='/assets/xgc_theme/images/xgc_logo_dark.svg' style='max-height: 30px;'></div>"

# 3. Inject Global CSS/JS to hide or restyle any remaining XGCERP elements
app_include_css = "/assets/xgc_theme/css/xgcerp_master.css"
app_include_js = "/assets/xgc_theme/js/xgcerp_master.js"

# 4. Translation Override (Catch-All)
# If a new update from upstream introduces the word "XGCERP" or "erpnext" into the UI, 
# this translation dictionary will instantly mask it to "XGCERP" for the user.
translations = [
    {"language": "en", "source_text": "XGCERP", "translated_text": "XGCERP"},
    {"language": "en", "source_text": "erpnext", "translated_text": "xgcerp"},
    {"language": "en", "source_text": "About XGCERP", "translated_text": "About XGCERP OS"}
]

```

---

### Step 4: Compile, Migrate, and Commit

Because we have modified JSON files (which are cached in the database) and injected new headers, you must rebuild the system assets and migrate the database.

Run these commands from your `frappe-bench` directory:

```bash
# Clear the system cache
bench clear-cache

# Sync the newly rebranded DocType JSONs to the MariaDB/PostgreSQL database
bench migrate

# Recompile the CSS and JavaScript assets
bench build --force

```

Finally, save your pristine, rebranded, and copyrighted fork to your repository:

```bash
cd apps/xgcerp  # or wherever your repo is located
git add .
git commit -m "feat: complete core masking, metadata rebrand, and copyright injection for XGCERP"
git push origin version-16

```

### Result

You now have a fully proprietary fork. The backend file structure remains compatible with `version-16` upstream updates, but every piece of metadata, UI text, and source code header is explicitly branded as **XGCERP by Daniel Brody at XGC CORP**.