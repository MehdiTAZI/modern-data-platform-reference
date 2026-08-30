# ADR-027: Terraform provider lockfiles

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
Provider version constraints define the compatible range, but they do not by themselves guarantee that two developers or CI runs select the same provider release. A reference architecture intended to demonstrate reproducible infrastructure should make the selected provider version and accepted package checksums reviewable in source control.

## Decision
1. Commit one `.terraform.lock.hcl` for every executable Terraform root.
2. Generate locks from the providers' origin registries using `terraform providers lock` so recorded checksums come from the publisher/registry trust path rather than a local plugin cache.
3. Pre-populate checksums for the supported contributor/automation platforms: `linux_amd64`, `darwin_amd64`, and `darwin_arm64`.
4. Keep provider constraints in `required_providers`; the lockfile selects the currently reviewed version inside that compatible range.
5. CI and local validation run `terraform init -lockfile=readonly`, so a provider constraint or dependency change that requires rewriting a lockfile fails until the lock update is explicitly reviewed and committed.
6. Provider upgrades are intentional changes: update constraints if needed, regenerate the affected root lockfile with `terraform providers lock`, review version/signature/checksum changes, and run the complete Terraform validation suite.

## Current selections

- Azure roots: `hashicorp/azurerm` **5.3.0**, constrained by `~> 5.3`. The v4 to v5 migration policy is documented in [ADR-034](ADR-034-azurerm-v5-migration.md).
- Workspace governance: `databricks/databricks` **1.128.0**, constrained by `~> 1.128.0`.

These versions are observations of the reviewed lockfiles, not permanent architecture requirements.

## Alternatives considered

- Rely only on version ranges: rejected because a later compatible provider release can change a future init without a repository diff.
- Pin exact versions in `required_providers` and omit lockfiles: rejected because this loses package checksum verification and makes normal controlled upgrades less expressive.
- Generate locks only for Linux CI: rejected because macOS contributors could otherwise add platform hashes opportunistically and create avoidable diffs.
- Commit `.terraform/`: rejected; provider binaries/module caches are generated working-directory state and must remain ignored.

## Consequences

Infrastructure runs become more reproducible and provider changes become explicit code-review events. Lockfiles add maintenance when providers are upgraded, and they currently lock providers only; Terraform does not use this file to lock remote module versions.

## Reconsider when

The project changes its supported development platforms, adopts a provider mirror/private registry, uses remote modules that require a separate pinning policy, or moves to an infrastructure system with different dependency-lock semantics.
