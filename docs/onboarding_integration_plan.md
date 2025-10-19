# XGCERP Onboarding Integration Implementation Plan

## Overview
This document outlines the tasks required to deliver the revamped onboarding
experience for the XGCERP platform. It focuses on creating a guided signup
experience, linking submitted registrations to CRM records, and ensuring
internal teams can review and approve each request securely.

## 1. Onboarding Workflow Implementation
### 1.1 Separate Signup Flows
- Provide dedicated entry points for Government Officials, Project Developers,
  and Brokers.
- Route each option to a form that pre-selects the `account_type` value while
  reusing the underlying Project Registration (or renamed User Registration)
  DocType.
- Dynamically reveal or hide fields based on account type so that each
  registrant only sees relevant inputs.

### 1.2 Signup Form Data Capture & Validation
- Collect personal, organizational, classification, location, KYC document, and
  terms acceptance data through a multi-step wizard.
- Block duplicate registrations by checking for existing users (email) and
  existing registration or lead records (registration number/ID).

### 1.3 Account Creation & Lead Record
- Create a disabled User document on submission without elevated roles.
- Generate a CRM Lead tagged with the signup category and link or create the
  associated organization record (Customer or custom Organization doctype) while
  avoiding duplicates.
- Display a submission confirmation page once all records are saved.

### 1.4 Post-Signup Confirmation & Notification
- Present a website confirmation that the account is under review.
- Send a branded acknowledgement email summarizing the submission and any
  immediate next steps (for example payment instructions if applicable).
- Move the Project Registration document to the "Under Review" workflow state.

### 1.5 Onboarding Review & Approval
- Provide an Onboarding Review workspace or DocType so admins can process
  pending registrations, assign account managers, and approve or reject
  requests.
- Ensure approval/rejection actions update workflow state, notify registrants,
  and surface outstanding items back to the applicant if more information is
  required.

## 2. CRM Integration & Lead Management
### 2.1 Lead & Organization Creation
- Populate Lead name/title, contact details, organization info, lead source, and
  signup category.
- Prevent duplicate Customers or organization records by checking existing
  entries before creating new ones.
- Store references to the generated Lead and Customer on the registration for
  traceability.

### 2.2 Assigning Account Handlers
- Capture the assigned Government Official (account manager) during review and
  propagate that relationship to CRM records for ongoing follow-up.
- Optionally notify the assigned handler when new accounts are approved.

### 2.3 Post-Approval Actions
- Enable the User account and assign the appropriate role once approved.
- Update Lead status (for example, to Qualified) while retaining it in the
  pipeline until a project engagement occurs.
- Subscribe the user to relevant Email Groups and ensure Customer records are
  flagged as prospects until conversion.

### 2.4 Sales Pipeline Alignment
- Support later conversion from Lead to Opportunity/Customer without creating
  duplicates by mapping key fields (account type, account manager) during the
  process.

## 3. Role Management & Permissions
### 3.1 Roles
- **Government Official**: Desk access, CRM permissions, onboarding dashboard
  home page, and potential approval rights.
- **Project Developer**: Portal-only permissions for project submission and
  tracking.
- **Broker**: Portal-only permissions tailored to broker interactions.
- **Onboarding Admin**: Desk access with full control over onboarding records
  and sufficient CRM visibility for validation.

### 3.2 Permission Setup
- Configure DocType permissions to restrict portal users to their own records
  while granting admins and handlers the access they require.
- Ensure only trusted roles can manage User enablement or role assignments,
  preferably through automated server-side actions on approval.

## 4. Email Templates & Notifications
- Implement a post-signup "under review" email confirming receipt and setting
  expectations.
- Implement a post-approval welcome email that introduces the assigned account
  manager and highlights next steps for the registrant’s role.
- Optionally send internal notifications to Government Officials when a new
  account is assigned to them.

## 5. User Experience Enhancements
### 5.1 Multi-Step Signup Wizard
- Break the registration form into clear steps (account type selection, account
  info, organization details, KYC upload, review & submit) with progress
  indicators and inline validation.

### 5.2 KYC Document Handling
- Add an Attach field to capture required identification documents and ensure
  reviewers can access submissions easily.

### 5.3 Confirmation & Error Handling
- Provide personalized confirmation pages after submission.
- Return actionable error messages for issues such as duplicate emails or
  missing fields.

## 6. Security Considerations
- Keep new accounts disabled or portal-only until approval to prevent premature
  desk access.
- Ensure portal roles lack desk access and only interact with their own data.
- Maintain the current stance of not enforcing two-factor authentication during
  onboarding while keeping the option available for future enhancement.

## 7. Testing & Rollout
- Validate the entire flow (signup, admin review, approval, CRM linkage, portal
  access) in a staging environment for each account type.
- Confirm that email notifications are delivered, workflow states change as
  expected, and permissions prevent unauthorized access.
