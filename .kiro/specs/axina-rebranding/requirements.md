# Requirements Document

## Introduction

This feature covers the systematic rebranding of the ERP application from the old company identity (XGC Software Inc. / AXERP) to the new identity (Axina Group Inc. / AXERP). The rebrand affects user-facing brand strings, URLs, company names, publisher metadata, logo references, and the automated rebranding script. Internal Python package names (`erpnext`), Frappe app identifiers (`app_name`), asset paths (`/assets/erpnext/`), and the `erpnext_integrations` module name are explicitly preserved to avoid breaking imports and runtime behavior.

## Glossary

- **AXERP**: The new product brand name, replacing AXERP in all user-facing contexts.
- **Axina_Group_Inc**: The new company and publisher name (Axina Group Inc.), replacing XGC Software Inc. and XGC CORP.
- **axinagroup.com**: The new domain, replacing xgccorp.com in all URLs.
- **axinagroup-logo.svg**: The new logo SVG file located in the repository root.
- **Hooks_File**: The file `erpnext/hooks.py` containing Frappe app metadata and configuration.
- **Smart_Rename_Script**: The file `scripts/smart_rename.py` that automates brand string replacement across the codebase.
- **Protected_Identifiers**: The set of internal identifiers that must NOT change: `app_name = "erpnext"`, Python module paths (`erpnext.*`), asset paths (`/assets/erpnext/`), and the `erpnext_integrations` module name.

## Requirements

### Requirement 1: Update Frappe App Metadata in Hooks File

**User Story:** As a developer, I want the Frappe app metadata in hooks.py to reflect the new Axina Group branding, so that the application identifies itself correctly in the Frappe ecosystem.

#### Acceptance Criteria

1. WHEN the Hooks_File is loaded by the Frappe framework, THE Hooks_File SHALL contain `app_title = "AXERP"`.
2. WHEN the Hooks_File is loaded by the Frappe framework, THE Hooks_File SHALL contain `app_publisher = "Axina Group Inc."`.
3. WHEN the Hooks_File is loaded by the Frappe framework, THE Hooks_File SHALL contain `app_email = "db@axinagroup.com"`.
4. WHEN the Hooks_File is loaded by the Frappe framework, THE Hooks_File SHALL contain `source_link = "https://github.com/AXERP/axerp"`.
5. THE Hooks_File SHALL retain `app_name = "erpnext"` unchanged.
6. THE Hooks_File SHALL retain all `/assets/erpnext/` asset paths unchanged.
7. WHEN the `extend_doctype_class` entry for Address is read, THE Hooks_File SHALL reference `AXERPAddress` instead of `AXERPAddress`.
8. WHEN the `default_mail_footer` is rendered, THE Hooks_File SHALL display "AXERP" as the product name in the footer link text.
9. WHEN the global search doctypes comment is read, THE Hooks_File SHALL contain the comment `# AXERP doctypes for Global Search`.
10. WHEN the Hooks_File is loaded by the Frappe framework, THE Hooks_File SHALL contain `app_color = "#f9720a"` to reflect the Axina Group orange accent color.

### Requirement 2: Update README Documentation

**User Story:** As a visitor or contributor, I want the README to reflect the AXERP brand and Axina Group identity, so that the project presents its current branding accurately.

#### Acceptance Criteria

1. WHEN the README.md is viewed, THE README.md SHALL display "AXERP" as the product name in all headings, badge labels, and descriptive text where "AXERP" previously appeared.
2. WHEN the README.md is viewed, THE README.md SHALL use the alt text "AXERP Logo" for the logo image element.
3. WHEN the README.md references screenshot image URLs, THE README.md SHALL use `axinagroup.com` as the domain instead of `xgccorp.com`.
4. WHEN the README.md references the official documentation, THE README.md SHALL link to `docs.axinagroup.com` instead of `docs.xgccorp.com`.
5. WHEN the README.md references the security reporting page, THE README.md SHALL link to `axinagroup.com/security` instead of `xgccorp.com/security`.

### Requirement 3: Update Trademark Policy

**User Story:** As a user or partner, I want the trademark policy to reference the correct AXERP brand name, so that trademark guidance is accurate for the new brand.

#### Acceptance Criteria

1. WHEN the TRADEMARK_POLICY.md is viewed, THE TRADEMARK_POLICY.md SHALL use "AXERP" in place of every occurrence of "AXERP".
2. THE TRADEMARK_POLICY.md SHALL reference "Axina Group Inc." as the trademark owner where company attribution is stated, replacing references to XGC-related entities where applicable.

### Requirement 4: Update Security Policy

**User Story:** As a security researcher, I want the security policy to reference the correct brand and reporting URLs, so that I can report vulnerabilities to the right place.

#### Acceptance Criteria

1. WHEN the SECURITY.md is viewed, THE SECURITY.md SHALL use "AXERP" in place of every occurrence of "AXERP".
2. WHEN the SECURITY.md references the security reporting URL, THE SECURITY.md SHALL link to `axinagroup.com/security/report` instead of `xgccorp.com/security/report`.
3. WHEN the SECURITY.md references the security guidelines URL, THE SECURITY.md SHALL link to `axinagroup.com/security` instead of `xgccorp.com/security`.

### Requirement 5: Update Contributing Guide

**User Story:** As a contributor, I want the contributing guide to reference the correct product name, so that contribution instructions are consistent with the new brand.

#### Acceptance Criteria

1. WHEN the .github/CONTRIBUTING.md is viewed, THE .github/CONTRIBUTING.md SHALL use "AXERP" in place of every occurrence of "AXERP".

### Requirement 6: Update Issue Template

**User Story:** As a user filing a feature request, I want the issue template to reference the correct brand and URLs, so that I am directed to the right resources.

#### Acceptance Criteria

1. WHEN the feature_request.md template is viewed, THE feature_request.md SHALL use "AXERP" in place of every occurrence of "AXERP".
2. WHEN the feature_request.md references the documentation URL, THE feature_request.md SHALL link to `docs.axinagroup.com` instead of `docs.xgccorp.com`.
3. WHEN the feature_request.md references the partners page, THE feature_request.md SHALL link to `axinagroup.com/partners` instead of `xgccorp.com/partners`.

### Requirement 7: Update Documentation Helper Script

**User Story:** As a CI pipeline maintainer, I want the documentation domain check to validate against the new domain, so that pull request documentation checks work correctly.

#### Acceptance Criteria

1. WHEN the .github/helper/documentation.py script checks documentation links, THE documentation.py SHALL include `docs.axinagroup.com` in the DOCUMENTATION_DOMAINS list instead of `docs.xgccorp.com`.

### Requirement 8: Update Copyright Headers

**User Story:** As a developer, I want copyright headers to reflect the new company name, so that legal attribution is correct.

#### Acceptance Criteria

1. WHEN the commitlint.config.js file is viewed, THE commitlint.config.js SHALL contain the copyright notice referencing "Axina Group Inc." instead of "XGC CORP.".
2. WHEN the scripts/smart_rename.py file is viewed, THE scripts/smart_rename.py SHALL contain the copyright notice referencing "Axina Group Inc." instead of "XGC CORP.".

### Requirement 9: Update Smart Rename Script for New Brand Constants

**User Story:** As a developer running the rebranding script, I want the script to use the new AXERP brand constants, so that future runs of the script apply the correct AXERP-to-AXERP transformation.

#### Acceptance Criteria

1. THE Smart_Rename_Script SHALL set `OLD_BRAND` to `"AXERP"`.
2. THE Smart_Rename_Script SHALL set `NEW_BRAND` to `"AXERP"`.
3. THE Smart_Rename_Script SHALL set `NEW_PUBLISHER` to `"Axina Group Inc."`.
4. THE Smart_Rename_Script SHALL set `NEW_EMAIL` to `"db@axinagroup.com"`.
5. THE Smart_Rename_Script SHALL set `SOURCE_LOGO_NAME` to `"axinagroup-logo.svg"`.
6. THE Smart_Rename_Script SHALL update the `source_link` written in `update_hooks_metadata` to `"https://github.com/AXERP/axerp"`.
7. THE Smart_Rename_Script SHALL continue to preserve the `erpnext_integrations` module name during replacements.
8. THE Smart_Rename_Script SHALL replace `xgccorp.com` domain references with `axinagroup.com` during its text processing.

### Requirement 10: Remove Old Logo File

**User Story:** As a repository maintainer, I want the old logo file removed after the new logo is in place, so that the repository does not contain stale branding assets.

#### Acceptance Criteria

1. WHEN the rebranding is complete, THE repository SHALL NOT contain the file `xgcerp-logo.svg` in the repository root.
2. THE repository SHALL contain the file `axinagroup-logo.svg` in the repository root as the active logo source.

### Requirement 11: Preserve Protected Identifiers

**User Story:** As a developer, I want all internal Python identifiers and asset paths to remain unchanged, so that the application continues to function without import or runtime errors.

#### Acceptance Criteria

1. THE Hooks_File SHALL retain `app_name = "erpnext"` unchanged after rebranding.
2. THE Hooks_File SHALL retain all references to `erpnext.erpnext_integrations` module paths unchanged after rebranding.
3. THE Hooks_File SHALL retain all `/assets/erpnext/` prefixed paths unchanged after rebranding.
4. IF any rebranding operation modifies a Protected_Identifier, THEN THE rebranding process SHALL treat this as an error condition requiring correction.
