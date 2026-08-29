# ADR-024: Remote state and cloud deployment evidence

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

The repository is a public reference architecture. Static validation is necessary but insufficient to claim that the reference has been exercised in a real Azure and Databricks environment. A cloud-applied demonstration must also remain reproducible, avoid long-lived credentials, preserve Terraform state between stateless CI runners, avoid leaking cloud identifiers, and support deterministic cleanup.

Terraform cannot safely create the storage account that contains its own remote state from a stateless runner without a separate bootstrap boundary. Storing local state as a CI artifact would weaken locking, consistency, recovery and operational realism.

## Decision

Use a minimal, idempotent Azure CLI bootstrap for the Terraform state resource group, storage account, state container and the deployment identity's Blob Data Contributor assignment. The state account disables shared-key authentication. After bootstrap, the Azure foundation and Databricks workspace-governance roots use the `azurerm` backend with Microsoft Entra ID and GitHub OIDC.

The deployment workflow uses the GitHub `dev` environment as the trust boundary. Azure authentication uses GitHub OIDC. Databricks authentication uses workload identity federation with `DATABRICKS_AUTH_TYPE=github-oidc`; no Databricks client secret is stored.

The lifecycle order is:

1. bootstrap remote state once;
2. plan and apply the Azure foundation using remote state;
3. derive the workspace host and platform outputs from Terraform state;
4. authenticate to Databricks through GitHub OIDC and verify Unity Catalog availability;
5. plan and apply workspace governance using a separate remote-state key;
6. generate and upload deterministic reference data;
7. validate, deploy and run the Databricks Bundle;
8. capture sanitized execution evidence as a GitHub Actions artifact;
9. destroy in reverse dependency order when the disposable environment is no longer required.

Raw run evidence is not committed automatically. A successful artifact may be curated into `docs/evidence/` only when it names the commit and Actions run that produced it. Subscription, tenant, client and principal identifiers are sanitized before artifact publication.

## Consequences

- Terraform state locking and persistence match a production-style operating model.
- The bootstrap is intentionally outside Terraform because it solves the state chicken-and-egg problem; it is kept minimal and idempotent.
- The state backend is retained when the disposable data platform is destroyed, allowing deterministic recovery and subsequent runs.
- The workflow requires one-time Azure and Databricks federation configuration outside this repository.
- A successful CI run still does not constitute cloud evidence; only the credentialed V1.1 workflow can produce that evidence.
- Cloud costs are created only by an explicit `workflow_dispatch` action and cleanup is explicit rather than automatic.

## Alternatives considered

### Local Terraform state in GitHub Actions

Rejected because runners are ephemeral and local state does not provide durable locking or recovery.

### Terraform Cloud or another hosted state service

Valid for an enterprise implementation, but Azure Blob state keeps this reference self-contained and cloud-native for the Azure implementation.

### Long-lived Azure or Databricks client secrets

Rejected. Workload identity federation is the default deployment pattern.

### Automatically commit evidence from the deployment workflow

Rejected because an automated cloud identity should not write directly to `main`, and raw output must be reviewed and sanitized before becoming permanent portfolio evidence.
