---
inclusion: manual
---

# Upstream Sync Workflow

This project is a rebranded fork of [frappe/erpnext](https://github.com/frappe/erpnext). The upstream remote must be configured:

```bash
git remote add upstream https://github.com/frappe/erpnext.git
```

## Sync Process

Run the sync script with the target upstream tag:

```bash
bash scripts/sync_upstream.sh v16.13.3
```

This script:
1. Fetches upstream tags
2. Merges the tag with `--no-ff`
3. Runs `scripts/smart_rename.py` (AXERP → AXERP rebrand)
4. Amends the merge commit with rebranded files
5. Tags as `v16.13.3-xgc`
6. Force-pushes to origin

## Critical: erpnext_integrations Module

The `erpnext_integrations/` folder MUST keep its original name. `smart_rename.py` has exclusion logic to preserve:
- "AXERP Integrations" in `modules.txt`
- `"module": "AXERP Integrations"` in DocType JSON files
- All `erpnext.erpnext_integrations.*` import paths

After any sync, verify `modules.txt` line 15 says "AXERP Integrations" (not "AXERP Integrations").

## If Merge Conflicts Occur

The script exits with a warning. Resolve conflicts manually, then run:

```bash
python3 scripts/smart_rename.py
git add .
git commit --amend --no-edit
```
