# Validation and evidence matrix

This matrix prevents source-code capability, CI validation and real-cloud evidence from being conflated.

| Capability | Implemented in source | Automated CI validation | Real cloud/runtime evidence |
|---|---:|---:|---:|
| Python transformations / contracts | Yes | Yes: Ruff, contract checks, Spark tests, >=90% coverage | Not required for pure transforms |
| Contract rule metadata / null semantics | Yes | Yes: unit + Spark tests | Lakeflow expectation metrics pending runtime evidence |
| Silver quality gates / quarantine | Yes | Yes: Spark transformation/failure tests | Pending real Lakeflow expectation/quarantine evidence |
| Quality telemetry / Ops model | Yes | Yes: normalized-event Spark tests + repository validation | Pending `retail_ops` pipeline execution |
| Reference-data reprocessing | Yes | Yes: recoverable + still-invalid Spark scenarios | Pending two-phase end-to-end catch-up run |
| Late-event reconciliation | Yes | Yes: Spark test | Pending end-to-end streaming evidence |
| SCD2 temporal/as-of join | Yes | Yes: local Spark interval-resolution test | Pending AUTO CDC + temporal Gold runtime evidence |
| Silver-to-Gold row/metric reconciliation | Yes | Yes: balanced + drift-detection Spark tests | Pending Gold fail-expectation runtime evidence |
| Azure foundation Terraform | Yes | Yes: fmt, readonly lock init, provider validate | Pending V1.1 disposable-cloud run |
| Unity Catalog governance | Yes | Yes: readonly lock init, provider validate | Pending V1.1 disposable-cloud run |
| Terraform provider reproducibility | Yes: per-root multi-platform lockfiles | Yes: lockfiles required + `-lockfile=readonly` | CI/provider-registry evidence; cloud apply remains separate |
| Event Hubs/Kafka adapter | Yes | Static/config validation | Pending real Event Hubs execution |
| Lakeflow Bronze/Silver/Gold/Ops | Yes | Python/config/repository tests | Pending real Bundle deployment/run |
| AUTO CDC SCD2 | Yes | Source/repository validation | Pending Lakeflow runtime evidence |
| Backend-only Private Link | Yes | Yes: AzureRM provider validate | Pending Azure network deployment/DNS proof |
| Unity Catalog ABAC mask example | Yes | SQL/source validation | Pending governed-tag policy execution |
| Secondary-region DR substrate | Yes | Yes: readonly lock init + AzureRM provider validate | Pending cross-region deployment/failover exercise |
| Databricks Managed DR | Architecture/runbook integration | Documentation only | Pending account-level Mission Critical configuration/test |
| Secret scanning | Yes | Yes: Gitleaks | CI evidence available in Actions |
| Python dependency vulnerability audit | Yes | Yes: project + resolved environment pip-audit | CI evidence available in Actions |
| Release SBOM/checksums/provenance | Yes | Workflow policy validated | Produced when a release workflow/tag succeeds |

A checkbox in the roadmap means the **reference implementation** is complete unless the item explicitly says real-cloud evidence. Public benchmark, availability, failover, Private Link, ABAC, Lakeflow expectation or AUTO CDC claims require captured environment-specific evidence.
