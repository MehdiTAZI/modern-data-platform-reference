# ADR-020: Disaster recovery

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Storage redundancy alone does not recover Unity Catalog metadata, workspace assets, permissions or orchestration state. A stricter regional DR profile therefore needs both cloud substrate in a second Azure region and a Databricks-aware replication/failover mechanism.

## Decision

Use Databricks **Managed Disaster Recovery** as the preferred cross-region replication and failover mechanism when the required Mission Critical/account capabilities are available.

The repository's `azure-dr-secondary` Terraform root provisions a secondary-region Azure substrate: VNet-injected Premium workspace, ADLS Gen2 storage, Access Connector, observability resources and an optional backend Private Link profile. Its default storage profile is GZRS where region support permits it.

GZRS is a storage durability choice, not a substitute for Managed DR. The secondary workspace, secondary metastore/failover group, Mission Critical activation and Databricks account-level replication are intentionally outside this Azure resource stack and must be configured as an organizational control.

External locations and storage credentials remain region-local prerequisites and must be recreated/validated in the secondary environment. Network security, Private Link and encryption posture must match the primary when Managed DR is used.

## Alternatives considered

- Rely on GZRS alone.
- Build custom scripts to copy every workspace and Unity Catalog asset.
- Recreate the entire platform only after a regional incident.

## Consequences

The infrastructure substrate can be reviewed and validated independently, while actual Databricks DR claims require a configured failover group and exercised failover/failback evidence. RPO/RTO remain measured business targets, not architecture-diagram promises.

## Reconsider when

Managed DR scope, licensing, supported assets or organizational RPO/RTO requirements materially change.
