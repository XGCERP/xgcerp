# Implementation Plan: Axina Rebranding

## Overview

Rebrand the ERP application from XGC/AXERP identity to Axina Group/AXERP identity across 10 files, rename one Python class, and delete one stale logo file. All changes are string replacements in existing files — no new modules, no database changes. Protected identifiers (`app_name="erpnext"`, `erpnext_integrations`, `/assets/erpnext/`) must remain unchanged.

## Tasks

- [x] 1. Update core app metadata and Python class
  - [x] 1.1 Update `erpnext/hooks.py` brand strings
    - Replace `app_title = "AXERP"` → `"AXERP"`
    - Replace `app_publisher = "XGC CORP."` → `"Axina Group Inc."`
    - Replace `app_email = "db@xgccorp.com"` → `"db@axinagroup.com"`
    - Replace `source_link = "https://github.com/AXERP/xgcerp"` → `"https://github.com/AXERP/axerp"`
    - Replace `AXERPAddress` → `AXERPAddress` in `extend_doctype_class`
    - Replace `AXERP` → `AXERP` in `default_mail_footer` link text
    - Replace `# AXERP doctypes for Global Search` → `# AXERP doctypes for Global Search`
    - Replace `app_color = "#e74c3c"` → `app_color = "#f9720a"` (Axina Group orange accent)
    - Verify `app_name = "erpnext"` is unchanged
    - Verify all `/assets/erpnext/` paths are unchanged
    - Verify all `erpnext.*` module paths are unchanged
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 11.1, 11.2, 11.3_

  - [x] 1.2 Rename class in `erpnext/accounts/custom/address.py`
    - Rename class `AXERPAddress` → `AXERPAddress`
    - _Requirements: 1.7_

- [x] 2. Update documentation files
  - [x] 2.1 Update `README.md`
    - Replace all `AXERP` → `AXERP` (headings, badge labels, descriptive text)
    - Replace logo alt text `AXERP Logo` → `AXERP Logo`
    - Replace `xgccorp.com` → `axinagroup.com` in screenshot image URLs
    - Replace `docs.xgccorp.com` → `docs.axinagroup.com`
    - Replace `xgccorp.com/security` → `axinagroup.com/security`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.2 Update `TRADEMARK_POLICY.md`
    - Replace all `AXERP` → `AXERP`
    - Add `Axina Group Inc.` where XGC-related company attribution is stated
    - _Requirements: 3.1, 3.2_

  - [x] 2.3 Update `SECURITY.md`
    - Replace all `AXERP` → `AXERP`
    - Replace `xgccorp.com/security/report` → `axinagroup.com/security/report`
    - Replace `xgccorp.com/security` → `axinagroup.com/security`
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 2.4 Update `.github/CONTRIBUTING.md`
    - Replace all `AXERP` → `AXERP`
    - _Requirements: 5.1_

  - [x] 2.5 Update `.github/ISSUE_TEMPLATE/feature_request.md`
    - Replace all `AXERP` → `AXERP`
    - Replace `docs.xgccorp.com` → `docs.axinagroup.com`
    - Replace `xgccorp.com/partners` → `axinagroup.com/partners`
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 3. Checkpoint - Verify documentation changes
  - Ensure all documentation files have correct brand strings, ask the user if questions arise.

- [x] 4. Update CI helper, build config, and rebranding script
  - [x] 4.1 Update `.github/helper/documentation.py`
    - Replace `"docs.xgccorp.com"` → `"docs.axinagroup.com"` in `DOCUMENTATION_DOMAINS` list
    - _Requirements: 7.1_

  - [x] 4.2 Update `commitlint.config.js` copyright header
    - Replace `XGC CORP.` → `Axina Group Inc.` in the copyright comment
    - _Requirements: 8.1_

  - [x] 4.3 Update `scripts/smart_rename.py`
    - Replace copyright header `XGC CORP.` → `Axina Group Inc.`
    - Set `OLD_BRAND = "AXERP"`
    - Set `NEW_BRAND = "AXERP"`
    - Set `NEW_PUBLISHER = "Axina Group Inc."`
    - Set `NEW_EMAIL = "db@axinagroup.com"`
    - Set `SOURCE_LOGO_NAME = "axinagroup-logo.svg"`
    - Update `source_link` in `update_hooks_metadata` to `"https://github.com/AXERP/axerp"`
    - Replace `xgccorp.com` domain references with `axinagroup.com`
    - Verify `erpnext_integrations` preservation logic is unchanged
    - _Requirements: 8.2, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

- [x] 5. Remove old logo file
  - Delete `xgcerp-logo.svg` from the repository root
  - Verify `axinagroup-logo.svg` exists in the repository root
  - _Requirements: 10.1, 10.2_

- [x] 6. Final checkpoint - Verify all changes and protected identifiers
  - Ensure all tests pass, ask the user if questions arise.
  - Grep affected files for residual `AXERP`, `xgccorp.com`, `XGC CORP.` strings to confirm none remain
  - Verify protected identifiers: `app_name = "erpnext"`, `erpnext_integrations`, `/assets/erpnext/` paths are intact in `hooks.py`
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

## Notes

- No property-based tests — this is deterministic static string replacement with no input variation
- All changes are find-and-replace operations; no new modules, APIs, or database changes
- Protected identifiers (`app_name="erpnext"`, `erpnext_integrations`, `/assets/erpnext/`) must never be modified
- Each task references specific requirements for traceability
