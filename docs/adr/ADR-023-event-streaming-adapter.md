# ADR-023: Azure Event Hubs through the Kafka protocol and Unity Catalog service credentials

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs a production-realistic event source while keeping the data-engineering layer source-neutral and locally reproducible. Azure Event Hubs exposes a Kafka-compatible endpoint, and current Azure Databricks runtimes support Unity Catalog service credentials for passwordless access to Event Hubs from serverless Kafka workloads.

## Decision
Use two interchangeable order-event adapters that produce the same Bronze raw envelope:

1. `files` is the default deterministic demo/replay adapter.
2. `kafka` connects to Azure Event Hubs through its Kafka-compatible endpoint.

The Kafka adapter authenticates with `databricks.serviceCredential`. Terraform registers the Azure Databricks Access Connector managed identity as a Unity Catalog `SERVICE` credential, while Azure RBAC grants that identity `Azure Event Hubs Data Receiver` on the namespace. No Event Hubs key, SAS token, client secret, or connection string is stored in source code or Bundle configuration.

Bronze retains the original payload plus source metadata (`topic`, `partition`, `offset`, broker timestamp and ingestion timestamp). Silver and Gold are independent of the selected source adapter.

## Alternatives considered
- **Event Hubs Spark connector:** rejected for Lakeflow pipelines because the third-party JVM connector is not the preferred/supported pipeline path; the Kafka-compatible endpoint uses the built-in Spark Kafka connector.
- **SAS connection strings:** supported, but rejected as the default because they introduce long-lived secret lifecycle and rotation requirements.
- **Client ID + secret OAuth:** rejected because managed identity via Unity Catalog service credentials removes application secrets and centralizes authorization.
- **Kafka-only demo:** rejected because it would make the repository impossible to run deterministically without cloud infrastructure.

## Consequences
- The same application can be demonstrated locally/replayed from retained files and operated against Event Hubs in Azure.
- Event Hubs authorization is visible in both Azure RBAC and Unity Catalog governance.
- The runtime identity must have `ACCESS` on the service credential and Azure Event Hubs receive permission.
- Deployments must use a Databricks runtime/serverless capability that supports service credentials for Kafka.

## Reconsider when
Use Lakeflow Connect managed Kafka ingestion instead when its managed connector feature set, lifecycle and SLOs better fit the production requirement, or choose a different broker when portability, ordering, throughput, retention or multi-cloud requirements justify it.
