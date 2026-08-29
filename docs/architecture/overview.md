# Architecture Overview

This reference separates **durable platform infrastructure**, **workspace governance**, and **data-product delivery**. Terraform provisions Azure and Unity Catalog boundaries; Declarative Automation Bundles deploy Lakeflow pipelines/jobs; the retail domain publishes Bronze, Silver and Gold datasets.

```mermaid
flowchart LR
  Git[GitHub] --> TF[Terraform]
  TF --> Azure[Azure foundation]
  TF --> UC[Unity Catalog]
  Git --> Bundle[Declarative Automation Bundle]
  Bundle --> LDP[Lakeflow pipelines]
  Sources[Files / Event Hubs] --> Bronze --> Silver --> Gold --> Consumers[BI / AI / sharing]
  UC -. governs .-> Bronze
  UC -. governs .-> Silver
  UC -. governs .-> Gold
```

See the physical, security, identity, deployment, observability and DR documents in this folder and the ADR index for decision rationale.
