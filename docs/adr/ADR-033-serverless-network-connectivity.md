# ADR-033 — Serverless network connectivity is account-level

- Status: Accepted
- Date: 2026-08-30

## Context

Azure Databricks serverless compute does not run inside the customer-managed VNet used by classic compute. VNet injection, workspace Private Link and NSG configuration therefore do not by themselves provide private serverless egress.

Databricks provides Network Connectivity Configurations (NCCs) at account level. An NCC is regional, binds to a workspace, and can contain Azure Private Endpoint rules for destinations such as ADLS Gen2 (`blob` and `dfs`) or other supported Private Link resources.

## Decision

Serverless networking is modeled separately from the Azure workspace foundation:

- `infra/modules/serverless-ncc` owns the Databricks account-level NCC;
- one NCC is bound to a workspace through `databricks_mws_ncc_binding`;
- Azure destinations are declared as a map of Private Endpoint rules;
- the `workspace-governance` stack exposes this capability behind `enable_serverless_ncc`;
- account-level Databricks authentication uses an aliased account provider;
- NCC region must match the workspace region;
- workspace/classic-compute connectivity remains owned by the Azure foundation stack.

## Storage example

Private ADLS Gen2 serverless access normally requires separate rules for the storage account `blob` and `dfs` subresources. The repository example therefore documents both targets rather than implying that one endpoint covers the full hierarchical-namespace path.

## Lifecycle

NCC Private Endpoint rules create connection requests. The target Azure resource owner must approve the generated Private Endpoint connection before it becomes effective. Runtime evidence must verify the connection state is established; a successful Terraform plan alone is not sufficient evidence of private data-plane connectivity.

## Consequences

### Positive

- `isolated` no longer overstates what workspace Private Link accomplishes;
- classic compute and serverless network controls have clear ownership boundaries;
- private serverless destinations are declarative and reviewable;
- multiple Private Endpoint rules converge on one NCC per workspace.

### Trade-offs

- account-level Databricks permissions and credentials are required;
- NCC and workspace region coupling becomes an operational constraint;
- Private Endpoint approval is a two-sided workflow across Databricks and Azure;
- one workspace can bind to only one NCC, so rules must be aggregated rather than split across competing NCCs.

## Validation

CI performs provider initialization and `terraform validate` on the `workspace-governance` stack using the repository lockfile. Real-cloud evidence remains required for NCC binding, Private Endpoint approval and serverless connectivity.
