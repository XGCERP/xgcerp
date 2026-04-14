# Implementation Plan

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** — Branding Assets Resolve to Missing or Old Files
  - **CRITICAL**: This test MUST FAIL on unfixed code — failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior — it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate branding assets are broken
  - **Scoped PBT Approach**: Scope the property to the concrete failing cases: favicon path, email brand image path, webmanifest icon paths, and raster favicon file existence
  - Test that `website_context["favicon"]` in `erpnext/hooks.py` resolves to a file that exists in `erpnext/public/images/` and is NOT old `erpnext-favicon.svg` (from Bug Condition `isBugCondition` in design)
  - Test that `email_brand_image` in `erpnext/hooks.py` resolves to a file that actually exists in `erpnext/public/images/` (currently references non-existent `.jpg`)
  - Test that all icon `src` values in `erpnext/public/images/site.webmanifest` start with `/assets/erpnext/images/` (currently uses root-relative paths or file doesn't exist)
  - Test that all 6 raster favicon files (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png`) exist in `erpnext/public/images/`
  - Test that `site.webmanifest` exists in `erpnext/public/images/`
  - Create test file at `erpnext/tests/test_favicon_branding_bug.py` using `hypothesis` for property-based generation
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct — it proves the bug exists)
  - Document counterexamples found (e.g., `favicon.ico` not in `erpnext/public/images/`, `email_brand_image` references non-existent `erpnext-logo.jpg`, webmanifest missing or has wrong paths)
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.4, 1.5, 2.1, 2.4, 2.5_

- [x] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** — Non-Branding Assets and SVG Overwrite Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - Observe: list all current files in `erpnext/public/images/` on unfixed code (e.g., `erpnext-logo.svg`, `erpnext-logo.png`, `erpnext-logo-blue.png`, `erpnext-video-placeholder.jpg`, `pos.svg`, `YouTube-icon-full_color.png`, subdirectories `illustrations/`, `leaflet/`, `ui-states/`, `v16/`)
  - Observe: `smart_rename.py` SVG overwrite targets are `erpnext-logo.svg`, `erpnext-favicon.svg`, `v16/erpnext.svg` — these are overwritten with `axinagroup-logo.svg`
  - Observe: `smart_replace()` function preserves `erpnext_integrations` module references
  - Observe: `app_logo_url` and `add_to_apps_screen` logo reference `/assets/erpnext/images/erpnext-logo.svg`
  - Write property-based test: for all non-branding files in `erpnext/public/images/` (files that are NOT `favicon.ico`, `favicon-*.png`, `apple-touch-icon.png`, `android-chrome-*.png`, `site.webmanifest`), the files remain present and byte-identical after the fix
  - Write property-based test: for all SVG overwrite targets in `smart_rename.py`, the target list still contains exactly `erpnext-logo.svg`, `erpnext-favicon.svg`, `v16/erpnext.svg`
  - Write property-based test: `smart_replace()` still preserves `erpnext_integrations` in all contexts (Python imports, JSON module fields, modules.txt)
  - Write property-based test: `app_logo_url` and `add_to_apps_screen` logo still reference the SVG logo path
  - Create test file at `erpnext/tests/test_favicon_branding_preservation.py` using `hypothesis`
  - Verify tests pass on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3. Fix for favicon and branding asset deployment

  - [x] 3.1 Copy raster favicon files into Frappe static asset directory
    - Copy `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, `android-chrome-192x192.png`, `android-chrome-512x512.png` from project root into `erpnext/public/images/`
    - These files must be byte-identical copies of the project root originals
    - _Bug_Condition: isBugCondition(input) where input.assetFile IN raster favicon list AND file NOT present in erpnext/public/images/_
    - _Expected_Behavior: All 6 raster favicon files exist in erpnext/public/images/ and are served at /assets/erpnext/images/_
    - _Preservation: Non-branding files in erpnext/public/images/ must remain unchanged_
    - _Requirements: 1.4, 2.4_

  - [x] 3.2 Copy and update site.webmanifest
    - Copy `site.webmanifest` from project root into `erpnext/public/images/`
    - Update icon `src` paths from root-relative (`/android-chrome-192x192.png`) to Frappe asset paths (`/assets/erpnext/images/android-chrome-192x192.png`)
    - Validate the resulting JSON is well-formed
    - _Bug_Condition: isBugCondition(input) where input.source == 'site.webmanifest' AND iconPath does NOT start with '/assets/erpnext/images/'_
    - _Expected_Behavior: site.webmanifest exists in erpnext/public/images/ with all icon src paths prefixed with /assets/erpnext/images/_
    - _Preservation: No other manifest or config files are affected_
    - _Requirements: 1.5, 2.5_

  - [x] 3.3 Update hooks.py favicon reference
    - Change `website_context["favicon"]` from `/assets/erpnext/images/erpnext-favicon.svg` to `/assets/erpnext/images/favicon.ico`
    - _Bug_Condition: isBugCondition(input) where input.hookKey == 'website_context.favicon' AND referencedFileIsOldBranding_
    - _Expected_Behavior: website_context["favicon"] points to /assets/erpnext/images/favicon.ico which exists_
    - _Preservation: website_context["splash_image"], app_logo_url, add_to_apps_screen logo remain unchanged_
    - _Requirements: 1.1, 2.1_

  - [x] 3.4 Fix email_brand_image path
    - Change `email_brand_image` from `assets/erpnext/images/erpnext-logo.jpg` to `assets/erpnext/images/erpnext-logo.png`
    - The `.jpg` file never existed; `erpnext-logo.png` is the correct file
    - _Bug_Condition: isBugCondition(input) where input.hookKey == 'email_brand_image' AND referencedFileDoesNotExist_
    - _Expected_Behavior: email_brand_image references erpnext-logo.png which exists in erpnext/public/images/_
    - _Preservation: Email branding functionality is preserved, only the file extension changes_
    - _Requirements: 1.6, 2.3, 3.3_

  - [x] 3.5 Extend smart_rename.py to copy raster favicons during rebrand
    - Add a new step in `run_rebrand()` after the SVG overwrite block (step 3) that copies the 6 raster favicon files + `site.webmanifest` from the project root into `erpnext/public/images/`
    - Use `shutil.copyfile()` for each raster file, consistent with existing SVG copy pattern
    - For `site.webmanifest`, read the source, update icon `src` paths to use `/assets/erpnext/images/` prefix, then write to destination
    - Add appropriate print statement for user feedback (e.g., `🖼️  Copied raster favicons and site.webmanifest`)
    - _Bug_Condition: isBugCondition(input) where smart_rename.py does not copy raster favicons_
    - _Expected_Behavior: run_rebrand() copies all 6 raster favicon files and updated site.webmanifest into erpnext/public/images/_
    - _Preservation: Existing SVG overwrite logic, smart_replace() function, and erpnext_integrations preservation must remain unchanged_
    - _Requirements: 1.6, 2.6, 3.2_

  - [x] 3.6 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** — Branding Assets Resolve to Valid AXERP Files
    - **IMPORTANT**: Re-run the SAME test from task 1 — do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1 (`erpnext/tests/test_favicon_branding_bug.py`)
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.4, 2.5_

  - [x] 3.7 Verify preservation tests still pass
    - **Property 2: Preservation** — Non-Branding Assets and SVG Overwrite Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 — do NOT write new tests
    - Run preservation property tests from step 2 (`erpnext/tests/test_favicon_branding_preservation.py`)
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all tests still pass after fix (no regressions)

- [x] 4. Checkpoint — Ensure all tests pass
  - Run both test files: `test_favicon_branding_bug.py` and `test_favicon_branding_preservation.py`
  - Ensure all tests pass, ask the user if questions arise
