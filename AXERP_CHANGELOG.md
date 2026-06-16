# AXERP Changelog

This file tracks AXERP-specific changes layered on top of the upstream ERPNext fork.
Format: `[version-tag] — upstream-base | date | author`

For upstream ERPNext release notes see: https://github.com/frappe/erpnext/releases

---

## [v16.22.0-axerp.3] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Fixed
- **erpnext/setup/doctype/company/company.py** — Two PostgreSQL compatibility fixes:

  1. **`update_company_monthly_sales`**: Replaced `frappe.utils.goal.get_monthly_results` call with a direct Query Builder query using `Sum(si.base_grand_total)` (typed column reference). `get_monthly_results` passes `goal_field` as a plain string to `Function('sum', goal_field)`, which PostgreSQL rejects with `function sum(unknown) does not exist` because it cannot infer the type of an unresolved string literal.

  2. **`get_all_transactions_annual_history`**: Replaced MySQL-only `date_sub(curdate(), interval 1 year)` in raw SQL with a parameterized `%s` bound to `frappe.utils.add_to_date(today(), years=-1)`. PostgreSQL does not recognize `DATE_SUB()` or `curdate()`.

---

## [v16.22.0-axerp.2] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Fixed
- **docker/Dockerfile**: Corrected base image tag from non-existent `frappe/erpnext:v16.26.4` to valid `frappe/erpnext:v16.22.0`.
  - Root cause: `XLSXMetadata` / `XLSXStyleBuilder` introduced in frappe ~16.15 caused `ImportError` when creating a Company via the Setup Wizard. Old base `v16.13.3` predated these symbols; new base `v16.22.0` matches the fork's erpnext version exactly.
  - Verified: `from frappe.utils.xlsxutils import XLSXMetadata, XLSXStyleBuilder` imports successfully in running container.

---

## [v16.22.0-axerp.1] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Added
- Initial production deployment to `erp.axinagroup.com` (EC2 t4g.xlarge arm64, us-east-1).
- **docker/docker-compose.yml**: Added `docker-compose.axerp.yml` in infra repo for 9-service Frappe stack (backend, frontend, websocket, scheduler, queue-long, queue-short, configurator, create-site, two Redis instances).
- PostgreSQL backend: reuses shared `openproject-postgres` (PostgreSQL 16) container on `openproject_default` Docker network. No separate MariaDB required.
- TLS: Let's Encrypt cert issued 2026-06-16 (expires 2026-09-14), auto-renewed by existing certbot container.
- `platform: linux/arm64` pinned on all images for Graviton2 compatibility.
- Idempotent `create-site` script: skips `bench new-site` if `site_config.json` already exists.

### Changed
- **docker/Dockerfile**: Base image bumped `frappe/erpnext:v16.13.3` → `v16.22.0` to match fork's erpnext version and include frappe 16.20.x with `XLSXMetadata` support.

### Infrastructure
- Route53 A record `erp.axinagroup.com` → `44.195.198.18` created 2026-06-16.
- Site data at `/data/axerp/sites/` on 500GB EBS data volume.
- Source cloned to `/data/axerp-src` on EC2; image built natively as `axerp:prod`.

---

## [v16.22.0-axerp] — upstream: v16.22.0 | 2026-06-16 | Daniel Brody

### Changed (AXERP Rebrand)
- Applied `scripts/smart_rename.py`: ERPNext → AXERP in UI strings, titles, metadata.
- **Preserved** (not rebranded): `erpnext_integrations` module name, all `erpnext.erpnext_integrations.*` import paths, `"module": "ERPNext Integrations"` in DocType JSON.
- **hooks.py**: `app_publisher`, `app_description`, `app_email`, `source_link` updated to Axina Group values.
- **pyproject.toml**: author → `Axina Group Inc.`, description → `ERP System Built on the Frappe Framework`.
- **package.json**: author, homepage, description updated.
- **CODEOWNERS**: sole owner `@dzbrody`.
- **README.md**: removed open-source claims, Frappe School badge, upstream community links.
- **SECURITY.md**: updated contact URLs to `axinagroup.com/security`.
- **TRADEMARK_POLICY.md**: ownership updated to `Axina Group Inc.`.
- **initiate_release.yml**: upstream weekly release workflow disabled (`if: false`).
- Logo files replaced with `axinagroup-logo.svg` at all standard asset paths.

### Upstream Base
- Merged `frappe/erpnext` tag `v16.22.0` (2026-06-10) into `version-16` branch.

---

## Sync Process

To sync a new upstream release:

```bash
cd /Users/dzbrody/Dev/GitHub/AXERP
bash scripts/sync_upstream.sh v16.X.Y
# Resolve any conflicts, then update this changelog.
# Create PR: version-16 → production
```

See `xgc_github_erpsync.md` and `.kiro/steering/upstream-sync.md` for the full workflow.
