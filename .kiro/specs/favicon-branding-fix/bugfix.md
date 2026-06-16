# Bugfix Requirements Document

## Introduction

The application favicon still displays old XGC/AXERP branding instead of the new AXERP branding. The `website_context` in `hooks.py` references the old `erpnext-favicon.svg` and `erpnext-logo.svg` files. New AXERP favicon files (favicon.ico, PNG variants, apple-touch-icon, android-chrome icons, and site.webmanifest) have been added to the project root but are not placed in Frappe's static asset directory (`erpnext/public/images/`) and the hooks configuration has not been updated to reference them. Additionally, the `app_logo_url`, `add_to_apps_screen` logo, `email_brand_image`, and `smart_rename.py` script still reference old branding file paths.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the website loads THEN the system serves the old `erpnext-favicon.svg` as the favicon because `website_context["favicon"]` in `hooks.py` points to `/assets/erpnext/images/erpnext-favicon.svg`

1.2 WHEN the website loads THEN the system serves the old `erpnext-logo.svg` as the splash image because `website_context["splash_image"]` in `hooks.py` points to `/assets/erpnext/images/erpnext-logo.svg`

1.3 WHEN the app logo is displayed (Desk UI, apps screen) THEN the system shows the old AXERP logo because `app_logo_url` and `add_to_apps_screen` logo in `hooks.py` point to `/assets/erpnext/images/erpnext-logo.svg`

1.4 WHEN the new AXERP favicon files are requested from the browser THEN the system cannot serve them because they are located in the project root instead of under `erpnext/public/` where Frappe serves static assets

1.5 WHEN the `site.webmanifest` references icon paths like `/android-chrome-192x192.png` THEN the system cannot serve these icons because the files are not in Frappe's static asset directory and the manifest paths do not use the `/assets/erpnext/` prefix

1.6 WHEN the `smart_rename.py` script runs THEN it only overwrites the 3 SVG logo targets (`erpnext-logo.svg`, `erpnext-favicon.svg`, `v16/erpnext.svg`) with `axinagroup-logo.svg` but does not copy the new PNG/ICO favicon files (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`) from the project root into `erpnext/public/images/`, nor does it copy the `site.webmanifest`

### Expected Behavior (Correct)

2.1 WHEN the website loads THEN the system SHALL serve the new AXERP `favicon.ico` (or appropriate PNG variant) as the favicon by updating `website_context["favicon"]` in `hooks.py` to point to the new favicon file under `/assets/erpnext/images/`

2.2 WHEN the website loads THEN the system SHALL serve the new AXERP logo as the splash image by updating `website_context["splash_image"]` in `hooks.py` to point to the correct new logo file under `/assets/erpnext/images/`

2.3 WHEN the app logo is displayed (Desk UI, apps screen) THEN the system SHALL show the new AXERP logo by updating `app_logo_url` and `add_to_apps_screen` logo in `hooks.py` to reference the correct asset path

2.4 WHEN the new AXERP favicon files are requested THEN the system SHALL serve them correctly because they have been moved from the project root into `erpnext/public/images/` (Frappe's static asset directory)

2.5 WHEN the `site.webmanifest` references icon paths THEN the system SHALL serve the icons correctly because the manifest has been moved to `erpnext/public/images/` and its icon paths use the `/assets/erpnext/images/` prefix

2.6 WHEN the `smart_rename.py` script runs THEN it SHALL copy the new AXERP favicon/icon files (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`) from the project root into `erpnext/public/images/` and copy `site.webmanifest` into `erpnext/public/images/`, so that future rebrand runs keep all branding assets in sync

### Unchanged Behavior (Regression Prevention)

3.1 WHEN other static assets are requested (JS bundles, CSS, sounds, POS icons) THEN the system SHALL CONTINUE TO serve them correctly from their existing paths under `/assets/erpnext/`

3.2 WHEN the `axinagroup-logo.svg` file is used for logo overwriting by `smart_rename.py` THEN the system SHALL CONTINUE TO overwrite the SVG logo targets (`erpnext-logo.svg`, `erpnext-favicon.svg`, `v16/erpnext.svg`) as before

3.3 WHEN email branding is rendered THEN the system SHALL CONTINUE TO display a brand image via the `email_brand_image` hook (path may be updated but functionality must be preserved)

3.4 WHEN the Desk UI loads non-favicon assets (setup wizard JS, navbar items, portal menu) THEN the system SHALL CONTINUE TO function identically
