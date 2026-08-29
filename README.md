# Modern Data Platform Reference Architecture

[![CI](https://github.com/MehdiTAZI/modern-data-platform-reference/actions/workflows/ci.yml/badge.svg)](https://github.com/MehdiTAZI/modern-data-platform-reference/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

A production-oriented, architecture-first reference for designing and engineering a modern enterprise **Databricks Lakehouse** on Azure. It demonstrates platform infrastructure, Unity Catalog governance, a complete Bronze/Silver/Gold application workflow, batch and streaming data products, contract-driven quality, CDC/SCD, testing, CI/CD, observability, FinOps, recovery, software supply-chain controls and the architectural decisions behind those patterns.

The repository deliberately implements **one deep retail/e-commerce vertical slice** instead of collecting unrelated snippets.

> **Deployment status:** V1.0 source/static validation is reproducible without cloud credentials. V1.1 adds OIDC-first cloud-evidence automation but a real cloud run still requires a disposable Azure/Databricks account and federated identities. V1.2 adds AUTO CDC SCD2, contract migration, late-event reconciliation, backend Private Link, ABAC PII masking and secondary-region DR patterns. V1.3 adds software supply-chain/release controls. V1.4 adds reproducible Terraform provider dependencies. V1.5 completes the application-side medallion workflow with explicit Silver quality gates, quarantine paths, trusted invariants and Gold dimensional/business products. Environment-dependent Lakeflow and cloud controls are not claimed as runtime-proven until exercised in a real account.

## Capability map

| Capability | Reference implementation |
|---|---|
| Cloud foundation | Azure RG, ADLS Gen2, VNet injection, NSG, NAT baseline, optional backend Private Link/private DNS, Databricks Premium |
| Identity | Databricks Access Connector managed identity + account-level groups + GitHub OIDC deployment identities |
| Governance | Unity Catalog catalog/schemas/storage/grants + governed-tag ABAC PII masking example |
| Batch ingestion | Lakeflow Spark Declarative Pipelines + Auto Loader for customers/products |
| Streaming ingestion | replayable raw order envelopes + Event Hubs/Kafka adapter |
| Bronze | source-faithful raw data, transport metadata, rescued schema drift, warn-only expectations |
| Silver | typed conformance, explicit validated/quarantine paths, two-stage order quality gate, watermark/dedup/reference integrity |
| CDC/SCD | deterministic SCD1 current state + Lakeflow AUTO CDC SCD2 customer history sourced from validated data |
| Schema evolution | rescued Bronze fields + versioned contract compatibility/migration example |
| Late data | bounded streaming watermark + Bronze reconciliation + canonical analytical orders |
| Data quality | YAML contracts, Lakeflow metric/drop/fail expectations, `_dq_errors`, parse quarantine and business quarantine |
| Gold | customer/product dimensions, order-line fact, exact daily/customer aggregates, five-minute streaming KPI |
| Packaging | Python source package + wheel/sdist release artifacts |
| Application delivery | Databricks Declarative Automation Bundle with Bronze → Silver → Gold orchestration |
| Testing | unit, Spark transformation, contract and deterministic failure-scenario tests |
| CI/CD | SHA-pinned Actions, lint/test/build, dependency/secret scans, readonly Terraform lock validation + gated OIDC cloud evidence |
| Supply chain | pip-audit, CycloneDX SBOM, SHA-256 checksums, GitHub/Sigstore attestations + multi-platform Terraform provider locks |
| Terraform state | Azure Blob remote state with Entra/OIDC auth and separate foundation/governance keys |
| Terraform dependencies | per-root `.terraform.lock.hcl`, AzureRM 4.81.0 / Databricks 1.128.0, Linux + Intel/ARM macOS hashes |
| Observability | Databricks system-table reliability / FinOps / audit starter queries |
| FinOps | environment/workload tags + billing usage attribution |
| Recovery/DR | replay/reconciliation + IaC reconstruction + Managed-DR-aligned secondary Azure substrate |
| Architecture | logical/physical/security/deployment/DR diagrams + 28 ADRs + reference NFRs |

## Complete retail application workflow

```mermaid
flowchart TB
  subgraph Sources
    C[Customer CSV snapshots]
    P[Product CSV snapshots]
    O[Order JSON files / Kafka]
  end

  subgraph Bronze[Bronze - preserve and observe]
    CR[customers_raw]
    PR[products_raw]
    OR[orders_raw]
  end

  subgraph Silver[Silver - validate and conform]
    CV[customers_validated]
    CQ[customers_quarantine]
    CS[customers current]
    CH[customers_history SCD2]
    PV[products_validated]
    PQ[products_quarantine]
    PS[products current]
    OP[orders_parsed]
    OIV[orders_parsed_validated]
    OIQ[orders_parse_quarantine]
    OV[orders_validated]
    OQ[orders_quarantine]
    OS[orders trusted stream]
    OC[orders_canonical]
  end

  subgraph Gold[Gold - serve business products]
    DC[dim_customers]
    DP[dim_products]
    F[fact_order_lines]
    DS[daily_sales]
    C360[customer_360]
    RT[realtime_sales_5m]
  end

  C --> CR
  P --> PR
  O --> OR

  CR --> CV --> CS --> DC
  CR --> CQ
  CV --> CH
  PR --> PV --> PS --> DP
  PR --> PQ

  OR --> OP --> OIV --> OV --> OS --> RT
  OP --> OIQ
  OV --> OQ
  OS --> OC --> F --> DS
  DC --> C360
  F --> C360
```

The important application rule is that each zone has a different responsibility:

- **Bronze preserves source fidelity.** It captures payloads, ingestion/transport metadata and schema drift. Expectations measure anomalies but do not destroy business records.
- **Silver is the trust boundary.** Invalid rows are classified and quarantined. Orders have a parse/shape gate **before** watermarking/deduplication, then a business/reference gate after conformance. Trusted Silver outputs use fail expectations only for invariants that should be impossible to violate after those gates.
- **Gold models for consumers.** It creates dimensions, a canonical fact and batch/streaming business aggregates. Gold does not repair source defects; broken trusted invariants fail fast.

See the [complete application-pipeline walkthrough](docs/patterns/application-pipeline.md) and [ADR-028](docs/adr/ADR-028-silver-quality-gates-and-invariants.md).

The deterministic functional dataset includes a customer update, invalid email, negative product price, duplicate event, unknown customer, invalid quantity, deliberately late event and corrupt JSON. This makes quality, ordering and recovery semantics observable rather than theoretical.

## Expectations and assertions

| Mechanism | Layer | Meaning in this reference |
|---|---|---|
| `expect` / `expect_all` | Bronze + metric controls | Observe and report without altering the dataset |
| `expect_all_or_drop` | Silver quality gates | Prevent invalid rows entering trusted outputs; matching quarantine tables retain the rejects and reasons |
| `expect_or_fail` / `expect_all_or_fail` | Trusted Silver + Gold | Assertion-like invariant: stop the affected flow if post-gate assumptions are broken |
| Python `assert` / pytest assertions | CI | Test reusable transformation behavior before deployment |

This separation is deliberate: an invalid source row is a data-quality event; a violated invariant on a trusted dataset is an application regression or contract failure.

## Architecture principles

1. **Architecture follows explicit NFRs and decision records.**
2. **Terraform owns durable platform/governance boundaries; Bundles own application resources.**
3. **Serverless-first application compute; classic VNet injection remains an enterprise reference.**
4. **Unity Catalog is the authorization and storage abstraction boundary.**
5. **Managed analytical tables; external volumes for externally-owned landing data.**
6. **Bronze is replayable/source-oriented; Silver contract-oriented; Gold consumer-oriented.**
7. **Bound streaming state deliberately; reconcile late business data instead of hiding it.**
8. **Business transformations are reusable Python functions, not notebook-only logic.**
9. **Invalid data is explicit: measure, quarantine or fail according to layer semantics; never silently disappear.**
10. **Security, cost, recovery, dependency provenance and operational evidence are part of the architecture.**

## Repository map

```text
.
├── databricks.yml
├── resources/
├── pipelines/retail/
│   ├── bronze.py
│   ├── silver.py
│   ├── history.py
│   ├── reconciliation.py
│   └── gold.py
├── src/mdpr/retail/
│   ├── contracts.py
│   ├── quality.py
│   └── transforms/
├── contracts/retail/
│   ├── customers.yml
│   ├── products.yml
│   ├── orders_ingest.yml
│   └── orders.yml
├── tests/
├── infra/
│   ├── modules/
│   └── stacks/
├── observability/sql/
├── governance/sql/
├── docs/
└── .github/workflows/
```

## Architecture documentation

- [Complete application pipeline](docs/patterns/application-pipeline.md)
- [Architecture overview](docs/architecture/overview.md)
- [Azure physical architecture](docs/architecture/physical-azure.md)
- [Identity and governance](docs/architecture/identity-and-governance.md)
- [Security architecture](docs/architecture/security-architecture.md)
- [Deployment architecture](docs/architecture/deployment.md)
- [Disaster recovery](docs/architecture/disaster-recovery.md)
- [Reference NFRs](docs/nfr/reference-nfrs.md)
- [ADR index](docs/adr/README.md)
- [Software supply-chain standard](docs/standards/supply-chain.md)
- [Validation/evidence matrix](docs/evidence/validation-matrix.md)
- [V1.1 cloud deployment evidence](docs/deployment/cloud-evidence.md)

## Local validation

Requirements: Python 3.11+ and Terraform 1.15.x for the same validation path as CI.

```bash
python -m pip install -e '.[dev]'
make data
make policy
make lint
make test
make audit
make build
make sbom
make contracts
make docs
make terraform-fmt
make terraform-validate
```

## Databricks application deployment

With a configured Databricks authentication context:

```bash
python -m build --wheel
databricks bundle validate -t dev --var="workspace_host=$DATABRICKS_HOST"
databricks bundle deploy -t dev --var="workspace_host=$DATABRICKS_HOST"
databricks bundle run -t dev retail_refresh
```

The Bundle deploys three serverless Lakeflow pipelines and one orchestration job:

```text
retail_bronze
    ↓
retail_silver
    ↓
retail_gold
```

DEV/STAGING/PROD consistently map to `retail_dev`, `retail_stg`, and `retail_prd`.

## Terraform dependency reproducibility

Every executable Terraform root commits a dependency lockfile generated from the origin registries for `linux_amd64`, `darwin_amd64`, and `darwin_arm64`. Normal validation does not permit Terraform to rewrite provider selections:

```bash
terraform -chdir=infra/stacks/azure-foundation init -backend=false -input=false -lockfile=readonly
terraform -chdir=infra/stacks/azure-foundation validate
```

Provider constraints still define compatibility; lockfiles record the currently reviewed provider release and checksums. See [ADR-027](docs/adr/ADR-027-terraform-provider-lockfiles.md).

## Azure foundation

The foundation uses a remote `azurerm` backend in real deployments. The baseline creates VNet-injected classic networking, HNS-enabled ADLS Gen2, Databricks Access Connector, Event Hubs, Log Analytics and a Premium workspace. `enable_private_link=true` switches to the documented backend-only classic compute Private Link profile; it does not imply full private user/serverless connectivity.

For a real plan/apply with persistent state, use the [V1.1 cloud-evidence lifecycle](docs/deployment/cloud-evidence.md).

## Unity Catalog governance

The governance root is intentionally separate Terraform state from the Azure foundation. It assumes referenced account-level groups already exist. Enterprise identity lifecycle remains an account/IdP concern. The ABAC PII example is deliberately separate SQL because governed-tag taxonomy and policy ownership are governance responsibilities, not an implicit application deployment side effect.

## Secondary-region DR substrate

The V1.2 secondary root is structurally validated with the same readonly provider lock policy. A real deployment needs its own remote-state key and region-specific values. This root provisions Azure substrate only; Databricks Mission Critical/Managed DR/failover-group configuration is an account-level prerequisite and must be evidenced separately.

## Release provenance

A `vX.Y.Z` tag must match `project.version`. The dedicated release workflow builds wheel and source distribution artifacts, audits project dependencies, emits a CycloneDX JSON SBOM and `SHA256SUMS`, creates GitHub/Sigstore build and SBOM attestations, and publishes the same evidence to the GitHub Release. See [ADR-026](docs/adr/ADR-026-software-supply-chain-and-release-provenance.md).

## Production adoption checklist

Before production adoption, validate Lakeflow expectation/runtime behavior, AUTO CDC execution, streaming state and throughput, the chosen Private Link/inbound/serverless networking profile, source retention/connectivity, enterprise identity ownership, ABAC tag/policy governance, regional Managed DR eligibility, measured load/skew/concurrency, budgets, enterprise observability integration and organizational software-supply-chain policy.

## License

Apache License 2.0. See [LICENSE](LICENSE).
