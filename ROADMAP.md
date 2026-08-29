# Roadmap

## V1.0 — Production-grade reference baseline

- [x] Architecture/NFR/ADR documentation
- [x] Azure VNet-injected foundation with explicit outbound NAT
- [x] HNS-safe ADLS Gen2 + Unity Catalog Access Connector managed identity
- [x] Unity Catalog catalog/schema/storage/grant model
- [x] Lakeflow Auto Loader Bronze ingestion
- [x] deterministic Silver customer/product state
- [x] streaming order watermark/dedup/reference-integrity pattern
- [x] Gold batch and streaming data products
- [x] contract-driven quality and quarantine
- [x] deterministic failure-scenario generator
- [x] Python wheel packaging + Declarative Automation Bundle
- [x] unit/Spark tests, coverage, CI and Terraform validation
- [x] system-table observability/FinOps/audit starter queries
- [x] replay/DQ incident runbooks
- [x] Event Hubs/Kafka source adapter deployment example

## V1.1 — Cloud-applied demonstration evidence

Repository-side deployment automation is complete; real evidence still requires a disposable Azure + Databricks account with organization-managed identities.

### Deployment readiness

- [x] GitHub/Azure OIDC deployment path with no Azure client secret
- [x] Databricks GitHub workload-identity federation path with no Databricks client secret
- [x] persistent Azure Blob Terraform backend with Entra/OIDC authentication
- [x] separate remote-state keys for Azure foundation and workspace governance
- [x] deterministic state bootstrap and reverse-order destroy workflow
- [x] run-ID-suffixed landing files for repeatable Auto Loader evidence runs
- [x] functional DQ dataset profile and scalable deterministic benchmark generator
- [x] sanitized GitHub Actions evidence artifact and curation rules
- [x] ADR-024 documenting state/evidence lifecycle

### Real-cloud evidence

- [ ] Configure the GitHub `dev` environment and Azure/Databricks federation prerequisites
- [ ] Bootstrap the remote-state backend in the disposable subscription
- [ ] Execute Terraform apply against the disposable DEV resource group
- [ ] Apply workspace governance against a Unity Catalog-enabled workspace
- [ ] Upload generated reference data to the landing volume
- [ ] Deploy Bundle and capture successful Bronze -> Silver -> Gold run evidence
- [ ] Publish benchmark results with dataset/region/run context
- [ ] Curate reviewed screenshots/query results under `docs/evidence/`
- [ ] Destroy the disposable platform while retaining remote state for audit/recovery

See [V1.1 cloud deployment evidence](docs/deployment/cloud-evidence.md).

## V1.2 — Advanced pattern extensions

- [x] Declarative Lakeflow AUTO CDC SCD2 customer history alongside SCD1 current state
- [x] versioned schema-contract migration example with CI compatibility checks
- [x] late-event reconciliation and canonical analytical orders surface
- [x] classic-compute backend Private Link/private DNS Azure variant
- [x] Unity Catalog governed-tag ABAC PII masking example
- [x] Managed DR-aligned secondary Azure substrate with GZRS storage profile

V1.2 patterns are source/architecture reference implementations. Private Link, ABAC and Managed DR still require environment-specific cloud/account configuration and evidence before they can be claimed as deployed.

## V1.3 — Supply-chain and release engineering

- [x] external GitHub Actions pinned to immutable full commit SHAs
- [x] CI policy check preventing mutable action references
- [x] project-graph and resolved-environment Python vulnerability gates with pip-audit
- [x] remediation of PYSEC-2026-3447 through setuptools 83+
- [x] release version/tag consistency validation
- [x] wheel + source distribution + SHA-256 checksums
- [x] CycloneDX JSON SBOM generation
- [x] GitHub/Sigstore provenance and SBOM attestations
- [x] Dependabot coverage for all executable Terraform roots
- [x] validation/evidence matrix separating source, CI and cloud proof
- [x] PR template enforcing architecture/evidence/security review

V1.3 makes repository artifacts traceable and reviewable; signed provenance/SBOM evidence does not imply that an artifact or cloud deployment is secure by itself.

## V1.4 — Reproducible infrastructure dependencies

- [x] commit a Terraform dependency lockfile for every executable root
- [x] generate locks from origin registries rather than a local provider cache
- [x] pre-populate provider checksums for Linux amd64, Intel macOS and Apple Silicon macOS
- [x] lock AzureRM 4.81.0 and Databricks provider 1.128.0 within reviewed version constraints
- [x] stop ignoring `.terraform.lock.hcl` while keeping `.terraform/`, state and plans ignored
- [x] enforce `terraform init -lockfile=readonly` in CI and local validation
- [x] document the controlled provider-upgrade workflow in ADR-027 and the supply-chain standard

V1.4 improves reproducibility and dependency review. Lockfiles complement provider constraints and checksum verification; they do not lock remote Terraform modules or prove a provider is vulnerability-free.

## V1.5 — Complete application pipeline

- [x] Bronze is explicitly source-faithful and non-destructive with warn-only expectations
- [x] customer/product Silver validated streams plus reason-preserving quarantine tables
- [x] order parse/shape gate before watermarking and stateful deduplication
- [x] order business/reference conformance gate after deduplication and enrichment
- [x] malformed JSON detection through Spark corrupt-record semantics
- [x] trusted Silver outputs protected with fail-fast invariant expectations
- [x] customer SCD2 history sourced only from validated Silver input
- [x] late-event reconciliation into canonical analytical orders
- [x] Gold customer/product dimensions and canonical order-line fact
- [x] exact daily sales and customer-360 materialized aggregates
- [x] streaming five-minute sales KPI with bounded event-time state
- [x] Spark tests for parse failures, deduplication, reconciliation, fact/dimension and aggregate logic
- [x] end-to-end application workflow documentation and ADR-028

V1.5 completes the source-level application reference. A real Lakeflow deployment is still required to produce runtime expectation metrics, AUTO CDC evidence and end-to-end pipeline execution evidence.
