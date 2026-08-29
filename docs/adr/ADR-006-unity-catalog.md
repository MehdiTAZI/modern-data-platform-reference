# ADR-006: Centralize Data Governance with Unity Catalog

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Data ownership, permissions, lineage and discoverability must be enforced consistently across workspaces and workloads.

## Decision

Use Unity Catalog as the governance plane for production data assets. Access is group/service-principal based; production ownership is assigned to controlled non-personal principals.

## Consequences

Governance becomes part of deployment design. Catalog/schema boundaries must reflect isolation and ownership rather than being created only for convenience.
