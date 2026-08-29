# Pattern: Managed DR-aligned secondary region

`infra/stacks/azure-dr-secondary` creates the Azure-side passive substrate for a stricter regional recovery profile:

- independent secondary resource group and address space;
- VNet-injected Premium Azure Databricks workspace;
- ADLS Gen2 storage with configurable redundancy, defaulting to GZRS where supported;
- Databricks Access Connector for region-local Unity Catalog external storage;
- Log Analytics resources;
- optional backend-only Private Link matching the primary network posture.

This stack does **not** claim to configure Databricks Managed Disaster Recovery. Managed DR is an account-level capability that requires an eligible primary/secondary workspace pair, secondary metastore, Mission Critical enablement and failover-group configuration.

Use Managed DR as the preferred replication/failover mechanism for in-scope Unity Catalog and workspace assets. Recreate and validate resources outside its replication scope—especially external locations, storage credentials, source connectivity and other region-local cloud dependencies—in the secondary environment.

GZRS improves storage durability and regional resilience but does not replicate Unity Catalog metadata or workspace configuration. It is therefore complementary to, not a substitute for, Managed DR.

A production DR exercise must measure failover/failback against business RPO/RTO and record which assets were recovered automatically versus reconstructed from IaC/source retention.

See ADR-020 and the disaster-recovery architecture document.
