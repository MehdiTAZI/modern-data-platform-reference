# ADR-032 — Terraform state security

- Status: Accepted
- Date: 2026-08-30

## Context

Terraform state can contain resource identifiers, configuration values and sensitive material. A shared remote backend therefore requires stronger controls than an ordinary artifact store.

Azure Storage provides remote state persistence, blob-level locking and encryption at rest. The backend must additionally prevent anonymous/public access and reduce the blast radius of accidental deletion or credential misuse.

## Decision

The state-backend stack enforces the following defaults:

- Microsoft Entra ID / RBAC-oriented access by disabling storage shared keys;
- private blob container access;
- public nested-item access disabled;
- cross-tenant replication disabled;
- infrastructure encryption enabled;
- blob versioning enabled;
- blob and container soft-delete retention, defaulting to 30 days;
- retention guarded to the range 7–365 days;
- optional `Storage Blob Data Contributor` assignment for the deployment principal.

The state storage account remains a bootstrap resource. Production deployments should additionally restrict network access through a storage firewall, service endpoint or Private Endpoint once the execution environment and DNS path are available.

## Consequences

### Positive

- accidental deletion has a recoverable window;
- historical state versions are retained;
- shared-key authentication is not part of the intended operating model;
- public container/blob exposure is explicitly prohibited;
- security properties are covered by mocked Terraform tests.

### Trade-offs

- versioning and retention consume additional storage;
- disabling shared keys requires identity-based operational tooling;
- fully private network access needs a bootstrap/network design that cannot be assumed for every reference deployment.

## Validation

`infra/stacks/state-backend/tests/security.tftest.hcl` verifies the critical storage-account and container invariants and proves that an unsafe retention period is rejected. CI runs these tests after provider initialization and `terraform validate`.
