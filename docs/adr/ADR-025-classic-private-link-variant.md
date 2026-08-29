# ADR-025: Classic compute backend Private Link variant

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

The baseline Azure reference uses VNet injection and explicit NAT. Some enterprise deployments require classic compute-to-control-plane traffic to use Azure Private Link without simultaneously forcing user/browser traffic onto a private corporate network.

## Decision

Provide an optional **classic compute plane backend-only Private Link** profile.

When `enable_private_link=true` the Azure foundation:

- creates a dedicated `/27` private-endpoint subnet;
- removes the explicit NAT Gateway from Databricks worker subnets;
- sets workspace Required NSG Rules to `NoAzureDatabricksRules`;
- keeps workspace public network access enabled for user/API access;
- creates a `databricks_ui_api` private endpoint;
- creates and links `privatelink.azuredatabricks.net` private DNS.

This profile privatizes the classic compute control-plane path only. It does **not** claim full private isolation. Private browser/API access additionally requires the appropriate inbound endpoints such as `browser_authentication` and, where applicable, `general_access`; serverless private data access requires its own connectivity design.

Data-source egress, firewalls, routing, service/private endpoints and DNS forwarding remain environment-specific enterprise network decisions.

## Alternatives considered

- Make complete private isolation the only reference topology.
- Keep all control-plane connectivity public.
- Add a private endpoint without changing the Databricks NSG/NAT profile.

## Consequences

The repository demonstrates a current enterprise Private Link pattern without hiding the additional components required for end-to-end isolation. The toggle changes network topology and must be planned as a controlled infrastructure migration.

## Reconsider when

Azure Databricks Private Link endpoint types, required NSG rules or serverless networking architecture materially change.
