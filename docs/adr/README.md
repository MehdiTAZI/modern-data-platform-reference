# Architecture Decision Records

ADRs document decisions that materially shape the platform or application architecture.

| ADR | Decision | Status |
|---|---|---|
| [001](ADR-001-lakehouse.md) | Adopt a Lakehouse architecture | Accepted |
| [002](ADR-002-medallion.md) | Use Bronze / Silver / Gold data layers | Accepted |
| [003](ADR-003-databricks-delta.md) | Use Databricks + Delta as primary runtime/table implementation | Accepted |
| [004](ADR-004-terraform-vs-bundles.md) | Separate platform IaC from application deployment | Accepted |
| [005](ADR-005-batch-streaming.md) | Support batch and streaming as first-class patterns | Accepted |
| [006](ADR-006-unity-catalog.md) | Centralize governance with Unity Catalog | Accepted |
| [007](ADR-007-environment-isolation.md) | Isolate DEV/STAGING/PROD deployment targets | Accepted |
| [008](ADR-008-production-code.md) | Prefer modular source code over notebook-centric production apps | Accepted |
