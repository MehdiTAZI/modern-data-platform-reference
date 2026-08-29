# Disaster Recovery

The reference separates ordinary availability/durability from true regional disaster recovery.

## Baseline availability profile

The primary reference uses zone-redundant Azure Storage by default and reconstructs infrastructure/governance configuration from code. Bronze/source retention remains the replay authority for data-pipeline recovery; streaming checkpoints are processing state, not the only business-data copy.

This profile improves resilience but is not a regional Databricks DR solution.

## Strict regional DR profile

For workloads with stricter RPO/RTO, deploy the `azure-dr-secondary` Terraform stack in a supported secondary Azure region. It provisions independent network, workspace, storage, Access Connector and observability substrate. Storage defaults to GZRS where supported.

The preferred Databricks replication/failover layer is **Managed Disaster Recovery**. Managed DR must be configured at the Databricks account level against eligible primary and secondary workspaces/metastores with Mission Critical capabilities enabled. The repository does not claim that account-level configuration has been applied.

Managed DR and Azure infrastructure responsibilities are complementary:

| Concern | Preferred recovery mechanism |
|---|---|
| Azure network/workspace substrate | Terraform reconstruction/pre-provisioned secondary |
| In-scope UC managed data/metadata | Databricks Managed DR |
| Workspace assets in Managed DR scope | Databricks Managed DR |
| External locations/credentials | Recreate and validate region-local configuration |
| External/source systems | Source-specific DR/retention strategy |
| Raw replayable ingestion | Retained source/Bronze data |
| Application resources | Declarative Automation Bundle deployment |

## Network parity

If the primary uses Private Link, the secondary must implement an equivalent private networking and DNS posture before failover. The V1.2 secondary stack exposes the same backend-only Private Link toggle for that reason. Full private user access still needs the additional inbound endpoint design documented in the Private Link pattern.

## Evidence required

Architecture targets are not recovery claims. A DR test should record:

- replication health and known out-of-scope assets;
- failover and failback timestamps;
- achieved RPO/RTO for representative data products;
- DNS/stable-URL behavior where configured;
- identity, grants and storage-access validation;
- replay/reconciliation performed after recovery;
- cleanup and return-to-primary procedure.

See ADR-020 and `docs/patterns/managed-dr.md`.
