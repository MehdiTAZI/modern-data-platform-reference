# ADR-034: AzureRM v5 migration and provider registration

- **Status:** Accepted
- **Date:** 2026-08-31

## Context

AzureRM v5 is a major provider release with breaking schema removals and provider-level behavioural changes. The most material behavioural change for this repository is resource-provider registration: AzureRM v5 defaults to registering no Azure Resource Providers, whereas v4 used the legacy automatic registration set. AzureRM v5 also disables location and resource-provider enhanced validation by default.

The reference architecture contains three executable Azure roots (`azure-foundation`, `azure-dr-secondary`, and `state-backend`) plus reusable Azure modules. A partial upgrade would create incompatible provider constraints and make infrastructure validation non-deterministic.

## Decision

1. Upgrade all executable Azure roots together to `hashicorp/azurerm` `~> 5.3`, with reviewed lockfiles selecting `5.3.0`.
2. Align reusable modules that constrain AzureRM, including `databricks-private-link`, to the same major/minor compatibility range.
3. Do not restore the broad v4 `legacy` Resource Provider registration behaviour.
4. Explicitly register only the service Resource Providers required by each executable root:
   - `azure-foundation`: `Microsoft.Databricks`, `Microsoft.EventHub`, `Microsoft.Network`, `Microsoft.OperationalInsights`, `Microsoft.Storage`.
   - `azure-dr-secondary`: `Microsoft.Databricks`, `Microsoft.Network`, `Microsoft.OperationalInsights`, `Microsoft.Storage`.
   - `state-backend`: `Microsoft.Storage`.
5. Preserve the v4 plan-time location and Resource Provider validation behaviour by enabling `features.enhanced_validation.locations` and `features.enhanced_validation.resource_providers`.
6. Do not enable Azure preflight validation by default. Preflight performs live Azure API calls during planning, requires credentials, and is currently supported only for a subset of resources. It can be enabled later for deployment environments where that operational dependency is desirable.
7. Treat future AzureRM major upgrades as coordinated migrations across all Azure roots and module constraints, with lockfile regeneration and the complete Terraform CI suite required before merge.

## Compatibility review

The Azure resources currently used by this repository were reviewed against the AzureRM v5 upgrade guide. Existing code already uses the non-deprecated v5 forms relevant to the repository, including:

- `azurerm_eventhub.namespace_id` rather than the removed `namespace_name`/`resource_group_name` form.
- `azurerm_storage_container.storage_account_id` rather than the removed `storage_account_name` form.
- no removed Log Analytics internet-access flags.

The migration therefore requires provider policy and dependency-lock changes rather than resource-model rewrites for the current architecture.

## Consequences

Provider upgrades become consistent across the Azure reference architecture, and deployments do not silently lose required Resource Provider registration when moving from v4 to v5. Registration is narrower and easier to audit than the v4 legacy set. Plan-time validation remains strict, while live preflight checks remain opt-in.

Deployment identities that are expected to register Resource Providers must have the necessary Azure permissions. In organizations where registration is centrally managed, the listed providers should instead be pre-registered and the deployment operating model documented accordingly.

## Alternatives considered

- Keep AzureRM v4: rejected because it postpones a necessary major-version migration and leaves the reference architecture behind the current provider line.
- Enable `resource_provider_registrations = "legacy"`: rejected because it preserves broad automatic registration of many providers the architecture does not use.
- Rely on AzureRM v5 defaults with no explicit registration list: rejected because fresh subscriptions could fail only at deployment time when required Resource Providers are absent.
- Enable preflight validation globally: deferred because it introduces live-Azure dependencies at plan time and does not yet cover most resources in this architecture.

## References

- HashiCorp AzureRM v5 upgrade guide: https://registry.terraform.io/providers/hashicorp/azurerm/5.0.0/docs/guides/5.0-upgrade-guide
- AzureRM provider releases: https://github.com/hashicorp/terraform-provider-azurerm/releases
