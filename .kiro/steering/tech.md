# Tech Stack & Build

## Core Framework
- **Frappe Framework** (>=16.0.0, <17.0.0) — full-stack Python/JS web framework providing ORM, REST API, background jobs, permissions, and the Desk UI
- **Python** >=3.14 (per pyproject.toml)
- **MariaDB** — primary database (PostgreSQL also supported by Frappe but CI runs MariaDB)
- **Redis** — caching and background job queues
- **Node.js** — asset bundling and frontend tooling

## Python Dependencies (notable)
- `holidays`, `Unidecode`, `rapidfuzz`, `barcodenumber`
- `googlemaps`, `plaid-python`, `python-youtube` (integrations)
- `mt-940` (bank statement parsing)
- `pypng` / PyQRCode (QR/barcode generation)

## Frontend
- Frappe client-side framework (jQuery, custom JS classes)
- SCSS for styles
- ESLint for JS linting, Prettier for JS/Vue/SCSS formatting
- Global JS variables: `frappe`, `erpnext`, `cur_frm`, `$`, `moment`, etc.

## Build System
- **flit** (`flit_core`) for Python packaging (pyproject.toml)
- **bench** CLI for site/app management (install, migrate, build, test)

## Linting & Formatting
- **Ruff** — Python linter and formatter (tab indentation, 110 char line length, double quotes)
- **ESLint** — JS linting (relaxed rules, many globals whitelisted)
- **Prettier** — JS/Vue/SCSS formatting
- **Flake8** — legacy config present but Ruff is primary
- **pre-commit** hooks enforce all of the above

## Code Style Rules
- Indentation: **tabs** for Python, JS, Vue, CSS, SCSS, HTML
- Indentation: **spaces (1)** for JSON files (doctype schemas)
- Line length: **110** characters
- Python quote style: **double quotes**
- Line endings: **LF**
- Final newline: yes (except JSON)
- Trim trailing whitespace: yes

## Common Commands

```bash
# Start the development server
bench start

# Run all Python tests
bench --site <site_name> run-tests --app erpnext

# Run tests for a specific doctype
bench --site <site_name> run-tests --doctype "Sales Invoice"

# Run a specific test file
bench --site <site_name> run-tests --module erpnext.accounts.doctype.sales_invoice.test_sales_invoice

# Run database migrations after schema changes
bench --site <site_name> migrate

# Build frontend assets
bench build --app erpnext

# Create a new site
bench new-site <site_name>
bench --site <site_name> install-app erpnext

# Lint Python (via ruff)
ruff check erpnext/
ruff format erpnext/

# Lint JS
npx eslint erpnext/
```
