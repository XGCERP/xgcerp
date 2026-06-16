# Favicon & Branding Fix — Bugfix Design

## Overview

The AXERP application displays old AXERP/XGC branding for its favicon, splash image, app logo, and email brand image. New AXERP favicon files (ICO, PNG variants, apple-touch-icon, android-chrome icons) exist in the project root but are not deployed to Frappe's static asset directory (`erpnext/public/images/`). The `hooks.py` configuration still references old `erpnext-favicon.svg` and `erpnext-logo.svg` paths. The `smart_rename.py` rebrand script only handles SVG logo overwrites and does not copy the new raster favicon/icon files. Additionally, `email_brand_image` references a non-existent `.jpg` file, and `site.webmanifest` uses root-relative icon paths that Frappe cannot serve.

The fix involves: (1) moving favicon files into the Frappe static asset directory, (2) updating `hooks.py` to reference the new favicon, (3) updating `site.webmanifest` icon paths, (4) extending `smart_rename.py` to copy raster favicon files during rebrand, and (5) fixing the `email_brand_image` path.

## Glossary

- **Bug_Condition (C)**: The condition where branding assets (favicon, splash, app logo, email logo, webmanifest icons) reference old AXERP files or files that don't exist in Frappe's static asset directory
- **Property (P)**: All branding hooks resolve to valid AXERP asset files served by Frappe at `/assets/erpnext/images/`
- **Preservation**: Existing static asset serving (JS bundles, CSS, sounds, POS icons), SVG logo overwriting by `smart_rename.py`, and all non-branding Desk UI functionality must remain unchanged
- **`hooks.py`**: The Frappe app configuration file at `erpnext/hooks.py` that defines `website_context`, `app_logo_url`, `add_to_apps_screen`, and `email_brand_image`
- **`smart_rename.py`**: The rebrand script at `scripts/smart_rename.py` that overwrites logo SVGs with `axinagroup-logo.svg` and performs text replacements across the codebase
- **Frappe static asset directory**: `erpnext/public/images/` — files here are served at `/assets/erpnext/images/` by Frappe

## Bug Details

### Bug Condition

The bug manifests when the browser requests branding assets (favicon, splash image, app logo, email logo, webmanifest icons). The `hooks.py` configuration references old AXERP-branded SVG files for the favicon and splash, the `email_brand_image` references a `.jpg` file that does not exist, and the new AXERP raster favicon files sit in the project root where Frappe cannot serve them.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type AssetRequest (a branding asset reference from hooks.py or site.webmanifest)
  OUTPUT: boolean

  RETURN (input.hookKey IN ['website_context.favicon', 'website_context.splash_image',
                            'app_logo_url', 'add_to_apps_screen.logo', 'email_brand_image']
          AND (referencedFileDoesNotExist(input.resolvedPath)
               OR referencedFileIsOldBranding(input.resolvedPath)))
         OR (input.source == 'site.webmanifest'
             AND input.iconPath does NOT start with '/assets/erpnext/images/')
         OR (input.assetFile IN ['favicon.ico', 'favicon-16x16.png', 'favicon-32x32.png',
                                  'apple-touch-icon.png', 'android-chrome-192x192.png',
                                  'android-chrome-512x512.png', 'site.webmanifest']
             AND input.assetFile is NOT present in 'erpnext/public/images/')
END FUNCTION
```

### Examples

- **Favicon**: Browser requests favicon → `hooks.py` serves `/assets/erpnext/images/erpnext-favicon.svg` → user sees old AXERP SVG favicon instead of AXERP `.ico`
- **Email logo**: Email is sent → `email_brand_image` resolves to `assets/erpnext/images/erpnext-logo.jpg` → file does not exist (only `.svg` and `.png` exist) → broken image in email
- **Webmanifest**: PWA install prompt → `site.webmanifest` references `/android-chrome-192x192.png` → Frappe cannot serve files from project root → broken icon
- **Smart rename**: Developer runs `smart_rename.py` → SVG logos are overwritten but raster favicons are not copied → favicon files remain only in project root after rebrand

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- All non-branding static assets (JS bundles, CSS, sounds, POS icons, illustrations, leaflet images, v16 assets) must continue to be served from their existing paths
- `smart_rename.py` must continue to overwrite the 3 SVG logo targets (`erpnext-logo.svg`, `erpnext-favicon.svg`, `v16/erpnext.svg`) with `axinagroup-logo.svg`
- `app_logo_url` and `add_to_apps_screen` logo continue to reference the SVG logo (which is correctly overwritten by `smart_rename.py` to show AXERP branding)
- Desk UI functionality (setup wizard, navbar, portal menu, module pages) must remain identical
- The `smart_replace()` text replacement logic and integration module preservation in `smart_rename.py` must remain unchanged

**Scope:**
All inputs that do NOT involve branding asset references (favicon, splash, email logo, webmanifest icons) or the `smart_rename.py` favicon copy step should be completely unaffected by this fix. This includes:
- All DocType CRUD operations
- All report generation
- All background job processing
- All non-branding hook configurations

## Hypothesized Root Cause

Based on the bug description, the most likely issues are:

1. **Missing file deployment**: The new AXERP favicon files (`favicon.ico`, PNG variants, `apple-touch-icon.png`, android-chrome icons, `site.webmanifest`) were added to the project root but never moved/copied into `erpnext/public/images/` where Frappe can serve them as static assets

2. **Stale hooks.py references**: `website_context["favicon"]` still points to `/assets/erpnext/images/erpnext-favicon.svg` (old branding) instead of the new `favicon.ico`. The `email_brand_image` references a `.jpg` file that has never existed in the images directory

3. **Incomplete smart_rename.py**: The rebrand script's "overwrite physical logos" section (step 3) only handles 3 SVG targets. It has no logic to copy raster favicon files from the project root into the static asset directory, so rebrand runs leave the favicon files stranded

4. **Wrong webmanifest paths**: `site.webmanifest` uses root-relative paths (`/android-chrome-192x192.png`) instead of Frappe asset paths (`/assets/erpnext/images/android-chrome-192x192.png`), so even if the manifest were served, the icon references would be broken

## Correctness Properties

Property 1: Bug Condition — Branding assets resolve to valid AXERP files

_For any_ branding asset reference in `hooks.py` (`website_context.favicon`, `website_context.splash_image`, `email_brand_image`) or `site.webmanifest` icon paths, the referenced file SHALL exist in `erpnext/public/images/` and SHALL be an AXERP-branded asset (not old AXERP branding).

**Validates: Requirements 2.1, 2.2, 2.4, 2.5**

Property 2: Preservation — Non-branding assets and SVG overwrite unchanged

_For any_ static asset request that is NOT a branding asset (favicon, splash, email logo, webmanifest icon), the system SHALL serve the same file from the same path as before the fix. The `smart_rename.py` SVG overwrite targets SHALL continue to be overwritten identically.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `erpnext/public/images/` (directory)

**Action**: Move/copy favicon files from project root

**Specific Changes**:
1. **Copy raster favicon files**: Copy `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png` from the project root into `erpnext/public/images/`
2. **Copy and update site.webmanifest**: Copy `site.webmanifest` from the project root into `erpnext/public/images/` and update its icon `src` paths to use `/assets/erpnext/images/` prefix

---

**File**: `erpnext/hooks.py`

**Function**: Top-level hook variables

**Specific Changes**:
3. **Update favicon reference**: Change `website_context["favicon"]` from `/assets/erpnext/images/erpnext-favicon.svg` to `/assets/erpnext/images/favicon.ico`
4. **Fix email_brand_image**: Change `email_brand_image` from `assets/erpnext/images/erpnext-logo.jpg` to `assets/erpnext/images/erpnext-logo.png` (the `.png` file actually exists; the `.jpg` never did)

---

**File**: `scripts/smart_rename.py`

**Function**: `run_rebrand()`

**Specific Changes**:
5. **Add favicon copy step**: After the existing SVG overwrite block (step 3), add a new step that copies the raster favicon files (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`) and `site.webmanifest` from the project root into `erpnext/public/images/`. This ensures future rebrand runs keep all branding assets in sync.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that check whether branding asset paths in `hooks.py` resolve to existing files in `erpnext/public/images/`, whether `site.webmanifest` icon paths use the correct Frappe prefix, and whether `smart_rename.py` copies raster favicons. Run these tests on the UNFIXED code to observe failures.

**Test Cases**:
1. **Favicon file existence**: Assert `favicon.ico` exists in `erpnext/public/images/` (will fail on unfixed code — file is in project root)
2. **Hooks favicon path**: Assert `website_context["favicon"]` points to a file that exists and is not old branding (will fail — points to `erpnext-favicon.svg`)
3. **Email brand image existence**: Assert the file referenced by `email_brand_image` exists (will fail — `erpnext-logo.jpg` does not exist)
4. **Webmanifest icon paths**: Assert all icon `src` values in `site.webmanifest` start with `/assets/erpnext/images/` (will fail — uses root-relative paths)

**Expected Counterexamples**:
- `favicon.ico` not found in `erpnext/public/images/`
- `email_brand_image` references non-existent `.jpg` file
- `site.webmanifest` icon paths lack `/assets/erpnext/images/` prefix

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed configuration produces the expected behavior.

**Pseudocode:**
```
FOR ALL assetRef WHERE isBugCondition(assetRef) DO
  result := resolveAsset_fixed(assetRef)
  ASSERT fileExists(result.resolvedPath)
  ASSERT isAXERPBranded(result.resolvedPath)
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold, the fixed code produces the same result as the original code.

**Pseudocode:**
```
FOR ALL assetRef WHERE NOT isBugCondition(assetRef) DO
  ASSERT resolveAsset_original(assetRef) = resolveAsset_fixed(assetRef)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It can generate many random hook key lookups and asset path resolutions to verify nothing else changed
- It catches edge cases where a path replacement might accidentally affect non-branding assets
- It provides strong guarantees that `smart_rename.py` SVG overwrite behavior is unchanged

**Test Plan**: Observe behavior on UNFIXED code first for non-branding asset paths and SVG overwrite targets, then write property-based tests capturing that behavior.

**Test Cases**:
1. **SVG overwrite preservation**: Verify `smart_rename.py` still overwrites `erpnext-logo.svg`, `erpnext-favicon.svg`, and `v16/erpnext.svg` with `axinagroup-logo.svg` after the fix
2. **Non-branding asset paths**: Verify all non-branding files in `erpnext/public/images/` (e.g., `pos.svg`, `YouTube-icon-full_color.png`, illustrations, leaflet) remain unchanged
3. **Smart replace logic**: Verify `smart_replace()` text replacement and `erpnext_integrations` preservation logic is unmodified
4. **Other hooks preservation**: Verify `app_logo_url` and `add_to_apps_screen` logo paths still reference the SVG (which is correctly overwritten by `smart_rename.py`)

### Unit Tests

- Test that all 6 raster favicon files exist in `erpnext/public/images/` after fix
- Test that `site.webmanifest` exists in `erpnext/public/images/` with correct icon paths
- Test that `hooks.py` `website_context["favicon"]` resolves to an existing file
- Test that `hooks.py` `email_brand_image` resolves to an existing file
- Test that `smart_rename.py` `run_rebrand()` copies raster favicons to `erpnext/public/images/`

### Property-Based Tests

- Generate random subsets of the files in `erpnext/public/images/` and verify non-branding files are byte-identical before and after the fix
- Generate random hook key lookups from `hooks.py` and verify non-branding hooks return identical values
- Generate random file paths from `smart_rename.py` SVG target list and verify they are still overwritten with `axinagroup-logo.svg` content

### Integration Tests

- Full asset resolution: load `hooks.py`, resolve each branding path, verify the file exists and is served with correct MIME type
- Rebrand pipeline: run `smart_rename.py` end-to-end, verify both SVG overwrites and raster favicon copies complete successfully
- Webmanifest validation: parse `erpnext/public/images/site.webmanifest` as JSON, verify all icon paths resolve to existing files in the static asset directory
