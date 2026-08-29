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

Requires a real Azure + Databricks test account and organization-managed identities.

- [ ] Execute Terraform apply against disposable DEV subscription/resource group
- [ ] Apply workspace governance against a Unity Catalog-enabled workspace
- [ ] Upload generated reference data to the landing volume
- [ ] Deploy Bundle and capture successful Bronze→Silver→Gold run evidence
- [ ] Publish benchmark results against the reference NFR dataset profile
- [ ] Export dashboard screenshots / query results to `docs/evidence/`

## V1.2 — Advanced pattern extensions

- [ ] Declarative AUTO CDC SCD2 implementation alongside the SCD1 reference
- [ ] schema-contract version migration example
- [ ] late-event reconciliation/backfill scenario
- [ ] Private Link/private DNS Azure variant
- [ ] policy/tag-driven PII mask implementation example
- [ ] geo-redundant DR variant driven by stricter RPO/RTO
