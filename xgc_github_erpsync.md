# AXERP Upstream Sync Setup Guide

This document describes the initial setup for syncing the AXERP fork with the upstream AXERP repository.

> **Note:** For ongoing sync operations, use `scripts/sync_upstream.sh`. See `.kiro/steering/upstream-sync.md` for the full workflow.

## Initial Repository Setup

If you have already cloned the repository and are inside the `axerp` directory, you do **not** need to clone again.

### 1. Add Frappe/AXERP as your "Upstream" source

```bash
git remote add upstream https://github.com/frappe/erpnext.git
```

### 2. Fetch all data from the Upstream repository

```bash
git fetch upstream
```

### 3. Create and switch to the `version-16` branch

```bash
git checkout -b version-16 upstream/version-16
```

### 4. Push this new branch to your AXERP repository

```bash
git push -u origin version-16
```

## Remote Setup Summary

* **`origin`** = `https://github.com/AXERP/axerp.git` (Your proprietary repo)
* **`upstream`** = `https://github.com/frappe/erpnext.git` (The official AXERP repo)

## Ongoing Sync

Whenever Frappe releases a new version (e.g., `v16.13.3`), run:

```bash
./scripts/sync_upstream.sh v16.13.3
```

This script handles fetching, merging, rebranding (AXERP → AXERP), committing, tagging as `v16.13.3-axerp`, and force-pushing to origin.

Check `https://github.com/frappe/erpnext/releases` for latest releases.

## Why Force Push

Because `git commit --amend` changes the identity of the last commit, `--force` is required to update GitHub. Since this is a proprietary fork with a single maintainer on the vendor branch, this is the standard approach for maintaining a clean history.

## Tag Safety

Using `git tag -f` ensures that re-running the script for the same version (e.g., after updating the logo) moves the tag to the newest correct commit.
