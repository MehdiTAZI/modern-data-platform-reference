# Roadmap

## V0.1 — Architecture foundation

- [x] Repository structure
- [x] Architecture overview
- [x] Initial ADRs
- [x] Terraform foundation modules
- [x] Batch and streaming application skeletons
- [x] Databricks Bundle skeleton
- [x] Basic CI

## V0.2 — Complete vertical slice

- [ ] Create sample datasets and generators
- [ ] Implement Bronze batch ingestion with Auto Loader variant
- [ ] Implement Silver orders streaming transformation
- [ ] Implement Gold daily sales and real-time KPI
- [ ] Add integration tests using local Spark/Delta where appropriate
- [ ] Add DQ metrics and quarantine dashboards

## V0.3 — Governance and platform hardening

- [ ] Implement Unity Catalog Terraform module
- [ ] Add storage credentials and external locations
- [ ] Add group/service-principal grants
- [ ] Add production private networking variant
- [ ] Add cluster/serverless policy examples
- [ ] Add tagging and FinOps conventions

## V0.4 — Advanced engineering patterns

- [ ] CDC merge
- [ ] SCD Type 2
- [ ] schema evolution
- [ ] event-time watermarking and late data
- [ ] replay/recovery runbook
- [ ] performance and skew examples
- [ ] DR strategy and ADR
