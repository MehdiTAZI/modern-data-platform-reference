# Validation and evidence matrix

This matrix prevents source-code capability, CI validation and real-cloud evidence from being conflated.

| Capability | Implemented in source | Automated CI validation | Real cloud/runtime evidence |
|---|---:|---:|---:|
| Python transformations / contracts | Yes | Yes: Ruff, contract checks, Spark tests, >=80% coverage | Not required for pure transforms |
| Azure foundation Terraform | Yes | Yes: fmt, init, provider validate | Pending V1.1 disposable-cloud run |
| Unity Catalog governance | Yes | Yes: provider validate | Pending V1.1 disposable-cloud run |
| Event Hubs/Kafka adapter | Yes | Static/config validation | Pending real Event Hubs execution |
| Lakeflow Bronze/Silver/Gold | Yes | Python/config tests | Pending real Bundle deployment/run |
| AUTO CDC SCD2 | Yes | Source/repository validation | Pending Lakeflow runtime evidence |
| Late-event reconciliation | Yes | Yes: Spark test | Pending end-to-end streaming evidence |
| Backend-only Private Link | Yes | Yes: AzureRM provider validate | Pending Azure network deployment/DNS proof |
| Unity Catalog ABAC mask example | Yes | SQL/source validation | Pending governed-tag policy execution |
| Secondary-region DR substrate | Yes | Yes: AzureRM provider validate | Pending cross-region deployment/failover exercise |
| Databricks Managed DR | Architecture/runbook integration | Documentation only | Pending account-level Mission Critical configuration/test |
| Secret scanning | Yes | Yes: Gitleaks | CI evidence available in Actions |
| Python dependency vulnerability audit | Yes | Yes: pip-audit | CI evidence available in Actions |
| Release SBOM/checksums/provenance | Yes | Workflow policy validated | Produced when a release workflow/tag succeeds |

A checkbox in the roadmap means the **reference implementation** is complete unless the item explicitly says real-cloud evidence. Public benchmark, availability, failover, Private Link or ABAC claims require captured environment-specific evidence.
