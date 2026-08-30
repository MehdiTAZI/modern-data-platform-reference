# ADR-031 — Platform connectivity profiles

- Status: Accepted
- Date: 2026-08-30

## Context

A single `enable_private_link` flag is not sufficient to express a production platform posture. It allows combinations that are syntactically valid but architecturally ambiguous, and it makes security intent difficult to review in Terraform plans.

Azure Databricks distinguishes public access, classic compute back-end Private Link, inbound/front-end Private Link, browser authentication, and serverless Network Connectivity Configuration (NCC). These controls must be composed intentionally.

## Decision

The Azure foundation stack exposes one `deployment_profile` with three supported values.

| Profile | Workspace public access | Classic compute back-end Private Link | Browser auth PE | NAT egress | Intended use |
|---|---:|---:|---:|---:|---|
| `managed` | Enabled | No | No | Yes | Development and lower-risk environments requiring simple deterministic egress |
| `enterprise` | Enabled | Yes | No | No | Private classic-compute control-plane connectivity while retaining public browser/API access |
| `isolated` | Disabled | Yes | Yes | No | Private workspace/browser path for high-isolation environments |

The profile mapping is code-owned rather than supplied as independent booleans. Terraform tests assert the invariants for every profile.

## Serverless boundary

The `isolated` profile covers the workspace/classic-compute foundation implemented in this repository. Complete private isolation for Databricks serverless also requires account-level NCC private endpoints and endpoint rules. That capability is tracked separately and must not be inferred merely from `deployment_profile = "isolated"`.

## Browser authentication ownership

Azure Databricks allows one `browser_authentication` private endpoint per Azure region and private DNS zone. A mature multi-workspace production topology should therefore host this endpoint on a dedicated regional web-auth workspace. The reference stack can create it on the workspace for a self-contained example, but shared production ownership should be implemented at account/platform scope.

## Consequences

### Positive

- Security posture becomes reviewable as one explicit architectural choice.
- Invalid combinations are removed from the public stack interface.
- CI detects regressions in public access, NAT, NSG and Private Link behavior.
- The distinction between classic-compute isolation and serverless NCC isolation is explicit.

### Trade-offs

- Profiles are opinionated; exceptional deployments require extending the profile model rather than toggling arbitrary booleans.
- The self-contained `isolated` example is not the recommended ownership model for a browser-auth endpoint shared by many production workspaces.
- Private connectivity adds Azure Private Endpoint/DNS cost and operational dependencies.

## Validation

`infra/stacks/azure-foundation/tests/profiles.tftest.hcl` performs mocked `terraform plan` tests for all three profiles. CI executes these tests after provider lockfile initialization and `terraform validate`.
