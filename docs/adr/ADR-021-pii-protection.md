# ADR-021: PII protection

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

PII controls must scale beyond one-off table grants and direct column masks while keeping classification and authorization reviewable by governance teams.

## Decision

Use Unity Catalog governed tags as the classification boundary and ABAC policies as the preferred broad row/column authorization mechanism when supported by the target runtime.

The DEV reference tags `retail_dev.silver.customers.email` with governed tag `pii=email` and applies a schema-level column-mask policy. Platform admins and retail data engineers are explicitly exempt in the example; ordinary account users receive the masked value.

Governed tags contain classification labels only, never sensitive values. Creating the governed-tag taxonomy is an account-level governance responsibility. Production policy principals, exemptions, UDF behavior and legal basis must be approved by the organization's security/privacy owners.

Direct table masks remain a fallback for workloads that cannot meet ABAC runtime requirements; they are not the preferred large-scale policy model.

## Alternatives considered

- Hand-maintained masks on every table/column.
- Encode PII rules inside transformation code.
- Rely only on catalog/schema grants without column-level protection.

## Consequences

Classification and enforcement can evolve independently of individual tables, but governed-tag and policy lifecycle becomes security-sensitive configuration that requires separation of duties and testing.

## Reconsider when

Enterprise policy engines, system classification tags or ABAC platform capabilities materially change.
