# Azure Physical Architecture

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

The classic-network variant uses two dedicated delegated subnets and explicit NAT egress. Application workloads remain serverless-first when organizational policy and feature support allow it. Private Link/private DNS is deliberately documented as an adoption variant rather than falsely claiming the public reference is fully private.
