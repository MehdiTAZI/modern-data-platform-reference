# Security Architecture

Core principles are least privilege, workload identities, short-lived CI credentials, no secrets in Git, separation of platform-admin/data-engineering/analyst duties, auditability, explicit network trust boundaries, encryption in transit/at rest, and Unity Catalog as the authorization/storage abstraction boundary.

## Identity

GitHub cloud deployment uses OIDC federation to Azure and Databricks rather than long-lived deployment secrets. Data-plane access uses managed identity through the Databricks Access Connector where supported.

## Network

The baseline keeps workspace public network access enabled while classic compute uses `no_public_ip=true` and explicit NAT egress. The V1.2 backend-only Private Link variant additionally privatizes classic-compute control-plane connectivity using a `databricks_ui_api` private endpoint and `privatelink.azuredatabricks.net` DNS, with Databricks Required NSG Rules set to `NoAzureDatabricksRules`.

This is not equivalent to full private isolation. Private browser/API access, serverless private access, source/storage firewalls and enterprise routing remain explicit adoption decisions.

## Data authorization and PII

Unity Catalog grants provide the baseline object authorization model. For broad PII protection, the reference prefers governed-tag classification plus Unity Catalog ABAC column-mask policies where runtime support permits it. The DEV example tags customer email as `pii=email` and masks it for ordinary account users while exempting designated platform/data-engineering groups.

Governed tags store non-secret classification metadata only. Production classification taxonomy, exemptions and masking semantics require enterprise privacy/security ownership.

## Recovery security

A secondary-region DR workspace must preserve equivalent identity, encryption and Private Link posture before failover. Storage redundancy alone is not treated as authorization/workspace recovery; see ADR-020 and the Managed DR pattern.
