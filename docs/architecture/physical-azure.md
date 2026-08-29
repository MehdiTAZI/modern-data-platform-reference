# Azure Physical Architecture

## Baseline classic-network profile

```mermaid
flowchart TB
  subgraph Azure
    EH[Event Hubs namespace / Kafka endpoint]
    SA[ADLS Gen2 HNS]
    AC[Databricks Access Connector MI]
    V[VNet]
    H[Host subnet /26+]
    C[Container subnet /26+]
    NAT[NAT Gateway]
    DBW[Azure Databricks Premium]
    V --> H --> DBW
    V --> C --> DBW
    H --> NAT
    C --> NAT
    AC --> SA
    AC --> EH
  end
```

The baseline uses two dedicated delegated subnets, `no_public_ip=true` for classic compute and explicit NAT egress. Application workloads remain serverless-first when organizational policy and feature support allow it.

## Backend Private Link profile

```mermaid
flowchart LR
  H[Classic host subnet] --> DBW[Databricks workspace]
  C[Classic container subnet] --> DBW
  H --> PE[databricks_ui_api private endpoint]
  C --> PE
  PE --> CP[Databricks control plane]
  DNS[privatelink.azuredatabricks.net] --> PE
```

When `enable_private_link=true`, Terraform creates a dedicated private-endpoint subnet and `databricks_ui_api` endpoint, links private DNS, removes the explicit NAT Gateway, and sets Required NSG Rules to `NoAzureDatabricksRules`. Workspace public network access remains enabled because this is a **classic-compute backend-only** profile.

Full private user/browser access and serverless private data connectivity require additional endpoint/network designs and are intentionally not implied by this toggle. See ADR-025 and `docs/patterns/private-link.md`.

## Secondary region

`infra/stacks/azure-dr-secondary` creates an independent VNet-injected workspace, storage, Access Connector and observability substrate in another Azure region. It can mirror the backend Private Link profile. Databricks Managed DR remains the preferred account-level replication/failover mechanism for in-scope metadata, managed data and workspace assets; see the DR architecture document.
