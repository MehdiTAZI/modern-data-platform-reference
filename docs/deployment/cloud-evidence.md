# V1.1 cloud deployment evidence

V1.1 turns the validated reference implementation into a repeatable real-cloud demonstration. The workflow is intentionally manual because it creates billable Azure and Databricks resources.

## Trust model

The GitHub Actions job targets the `dev` environment. Configure federation against that environment rather than a broad repository branch subject.

### Azure

Create a Microsoft Entra application or user-assigned managed identity with a federated identity credential for this repository's GitHub `dev` environment. For a disposable demonstration subscription, the deployment identity needs enough management-plane permission to create the reference resources and role assignments. A practical lab setup is Contributor plus User Access Administrator at the disposable subscription or resource-group scope; tighten this for a long-lived environment.

Add these **environment secrets** to GitHub `dev`:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_PRINCIPAL_OBJECT_ID`

No Azure client secret is used.

### Databricks

Create or reuse an account-level Databricks service principal and configure a GitHub federation policy whose subject is:

```text
repo:MehdiTAZI/modern-data-platform-reference:environment:dev
```

Add its application/client ID as the GitHub `dev` environment secret:

- `DATABRICKS_CLIENT_ID`

The service principal must be able to access the created workspace and must have the Unity Catalog privileges required to create storage credentials, service credentials, external locations, catalogs, schemas, volumes and grants. If your account does not make account identities automatically available to new workspaces, assign the service principal to the DEV workspace before the governance step.

Optionally configure these GitHub `dev` environment variables when your group names differ from the reference defaults:

- `DATABRICKS_PLATFORM_ADMIN_GROUP`
- `DATABRICKS_ENGINEER_GROUP`
- `DATABRICKS_ANALYST_GROUP`

## Workflow lifecycle

The workflow is `.github/workflows/deploy.yml` and is invoked with **Actions → V1.1 Cloud Evidence → Run workflow**.

### 1. Bootstrap

Run `action=bootstrap` once. This creates only the remote-state resource group, Azure Storage account and `tfstate` container, then grants the deployment identity Blob Data Contributor. The storage account disables shared-key authentication.

The bootstrap is deliberately not Terraform-managed from CI; see [ADR-024](../adr/ADR-024-remote-state-and-deployment-evidence.md).

### 2. Apply and execute

Run `action=apply`.

The workflow:

1. plans and applies the Azure foundation using remote state;
2. obtains the workspace host, storage and Event Hubs outputs from Terraform;
3. validates Databricks GitHub OIDC and Unity Catalog availability;
4. plans and applies the workspace-governance Terraform root using a separate state key;
5. generates a deterministic dataset;
6. uploads new run-ID-suffixed objects to the governed landing area;
7. validates and deploys the Bundle;
8. runs `retail_refresh` through Bronze, Silver and Gold;
9. captures the Silver/Gold table inventory and execution metrics;
10. sanitizes cloud identifiers and publishes an Actions evidence artifact.

Two dataset profiles are available:

- `functional`: small data containing duplicates, invalid values, a missing reference, a late event and corrupt JSON to prove DQ/quarantine behavior;
- `benchmark`: deterministic valid data with 10,000 customers, 1,000 products and a configurable order count (100,000 by default).

Benchmark numbers are reference-run observations, not universal Databricks performance claims. Record region, commit, dataset size and execution context with every result.

### 3. Curate evidence

A successful Actions artifact is raw evidence. Review it before adding selected results to `docs/evidence/<date>-<run-id>/`. Permanent evidence must include the originating Git commit and GitHub Actions run ID.

Do not commit credentials, Terraform state, plan binaries, subscription IDs, tenant IDs or client IDs.

### 4. Destroy

Run `action=destroy` with `confirm_destroy=true`. The workflow destroys Bundle resources, Unity Catalog governance objects and the Azure foundation in reverse order. The small remote-state backend is retained deliberately for recovery and future runs.

## Expected external blockers

The workflow fails early and visibly when the external account setup is incomplete. Typical blockers are:

- missing GitHub `dev` environment secrets;
- missing Azure federated identity credential;
- insufficient Azure role-assignment permission;
- missing Databricks federation policy;
- Databricks service principal not assigned to the new workspace;
- workspace not attached to a Unity Catalog metastore;
- reference groups not present in the Databricks account.

These are deployment-account prerequisites, not repository secrets and are intentionally not automated from a public reference repository.
