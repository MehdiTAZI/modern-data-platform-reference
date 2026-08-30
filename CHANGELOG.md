# Changelog

This project follows semantic versioning for repository release artifacts. Cloud deployment evidence is tracked independently from source versioning.

## 1.6.0 — Data engineering deep dive

- Enrich Bronze replay/idempotency metadata with source ownership, payload fingerprints and ingestion dates.
- Extend contract rules with quality categories, operational messages and dataset ownership metadata.
- Align reusable quality annotation with declarative expectation null semantics: only `TRUE` passes.
- Add normalized, payload-minimized DQ events and aggregated summaries in a dedicated Ops Lakeflow pipeline.
- Add reference-data reprocessing that can recover eventually-consistent foreign keys without mutating original quarantine evidence.
- Re-evaluate the complete current contract during reprocessing so unrelated business defects remain quarantined.
- Converge low-latency delivery, event-time reconciliation and reference-data remediation into deterministic canonical orders.
- Add SCD2 event-time as-of enrichment and a temporal Gold order fact with explicit history-coverage assertions.
- Add row-count and additive business-metric reconciliation helpers plus a fail-fast Silver-to-Gold accounting surface.
- Add deterministic second-phase sample data for demonstrating an unknown customer becoming valid after reference catch-up.
- Extend Spark tests for quality telemetry, remediation, temporal joins, duplicate accounting and processing-boundary reconciliation.
- Add DQ/reconciliation observability queries plus ADR-029 and ADR-030 documenting remediation and temporal semantics.

## 1.5.0 — Complete medallion application workflow

- Make Bronze explicitly source-faithful and non-destructive, with warn-only ingestion/schema-drift expectations.
- Add explicit Silver validated and quarantine paths for customers, products and orders.
- Split order quality into a pre-stateful parse/shape gate and a post-dedup business/reference gate.
- Detect malformed JSON using Spark corrupt-record semantics instead of treating an all-null parsed struct as valid.
- Source customer AUTO CDC SCD2 history only from rows that passed the Silver quality gate.
- Reserve fail expectations for trusted Silver/Gold invariants; row-level source defects are quarantined instead of stopping the pipeline.
- Add Gold customer/product dimensions, canonical order-line fact, exact daily/customer aggregates and streaming five-minute KPIs.
- Replace streaming exact distinct aggregation with approximate distinct metrics suited to the streaming KPI surface.
- Extend Spark tests for parse failures, late reconciliation and Gold dimensional/fact transformations.
- Add a complete application-pipeline walkthrough and ADR-028 for quality-gate semantics.

## 1.4.0 — Reproducible infrastructure dependencies

- Commit Terraform dependency lockfiles for every executable root.
- Lock AzureRM 4.81.0 and Databricks provider 1.128.0 using registry-signed checksums.
- Pre-populate provider hashes for Linux amd64, Intel macOS and Apple Silicon macOS.
- Enforce `terraform init -lockfile=readonly` in CI and local validation.
- Stop ignoring `.terraform.lock.hcl` while continuing to ignore Terraform working directories and state.
- Document the provider-upgrade/review workflow in ADR-027 and the supply-chain standard.

## 1.3.0 — Supply-chain and release engineering

- SHA-pin external GitHub Actions and validate the policy in CI.
- Add project-graph and resolved-environment Python vulnerability auditing with `pip-audit`.
- Remediate PYSEC-2026-3447 by requiring setuptools 83+ in build/CI environments.
- Add tagged release packaging with wheel, sdist, SHA-256 checksums and CycloneDX SBOM.
- Add GitHub/Sigstore package provenance and SBOM attestations.
- Expand Dependabot coverage to every executable Terraform root.
- Add an explicit validation/evidence matrix and PR claims checklist.

## 1.2.0 — Advanced data platform patterns

- Lakeflow AUTO CDC SCD2 customer history.
- Versioned contract migration/compatibility checks.
- Late-event reconciliation and canonical analytical orders.
- Optional backend-only Azure Databricks Private Link.
- Unity Catalog governed-tag ABAC masking reference.
- Managed-DR-aligned secondary Azure substrate.

## 1.1.0 — Cloud evidence automation

- OIDC-first Azure/Databricks evidence workflow.
- Persistent remote Terraform state and deterministic teardown.
- Functional and benchmark dataset profiles with sanitized evidence artifacts.

## 1.0.0 — Production-grade reference baseline

- Architecture-first Databricks/Azure lakehouse reference with Terraform, Unity Catalog, Lakeflow, batch/streaming, DQ, CI, observability and ADRs.
