# Project Structure

## Top Level
```
erpnext/                  # Main Python package (the Frappe app)
  hooks.py                # App-level configuration: doc_events, scheduler, routes, etc.
  modules.txt             # Registered Frappe modules list
  patches.txt             # Migration patches registry ([pre_model_sync] / [post_model_sync])
  __init__.py             # Version, utility functions
  controllers/            # Shared base controller classes (accounts_controller, taxes_and_totals, etc.)
  patches/                # Data migration scripts organized by version (v10_0, v11_0, ..., v16_0)
  tests/                  # App-level integration tests
  public/                 # Frontend assets (JS bundles, SCSS, images, icons, sounds)
  templates/              # Jinja/HTML templates for web views and print formats
```

## Modules
Each business domain is a Frappe module directory under `erpnext/`:

```
accounts/   assets/       buying/         selling/
stock/      manufacturing/ projects/      crm/
support/    setup/         maintenance/   subcontracting/
regional/   quality_management/  telephony/
erpnext_integrations/     communication/  bulk_transaction/
utilities/  portal/        edi/
```

## Module Internal Structure
Each module follows a consistent pattern:

```
erpnext/<module>/
  __init__.py
  doctype/                # DocTypes (data models) — one subfolder per doctype
    <doctype_name>/
      <doctype_name>.json     # Schema definition (field list, permissions, etc.)
      <doctype_name>.py       # Server-side Python logic (Document subclass)
      <doctype_name>.js       # Client-side form script
      test_<doctype_name>.py  # Unit/integration tests
      test_records.json       # Test fixture data (optional)
      __init__.py
  report/                 # Script reports and query reports
  workspace/              # Desk workspace definitions (JSON)
  page/                   # Custom Desk pages (optional)
  dashboard_chart/        # Dashboard chart definitions (optional)
  notification/           # Notification templates (optional)
```

## DocType Pattern (critical)
DocTypes are the fundamental building block. Each doctype has:
- A **JSON schema** (`<name>.json`) defining fields, permissions, naming rules — edited via Frappe UI or directly
- A **Python class** (`<name>.py`) extending `frappe.model.document.Document` with validation, business logic, and whitelisted API methods
- A **JS file** (`<name>.js`) for client-side form behavior (`frappe.ui.form.on(...)`)
- **Tests** (`test_<name>.py`) using `frappe.tests.utils.FrappeTestCase`

## Patches
Migration patches live in `erpnext/patches/v<major>_<minor>/` and are registered in `erpnext/patches.txt` under `[pre_model_sync]` or `[post_model_sync]` sections.

## Controllers
Shared logic for transaction documents lives in `erpnext/controllers/`:
- `accounts_controller.py` — base for all accounting transactions
- `buying_controller.py` / `selling_controller.py` — purchase/sales logic
- `stock_controller.py` — inventory movements
- `taxes_and_totals.py` — tax calculation engine
- `status_updater.py` — cross-document status sync

## Regional
Country-specific overrides in `erpnext/regional/<country>/`. Hooked via `regional_overrides` in `hooks.py`.

## Frontend Assets
- `erpnext/public/js/` — client-side JS (bundled as `erpnext.bundle.js`)
- `erpnext/public/scss/` — styles (bundled as `erpnext.bundle.css`)
