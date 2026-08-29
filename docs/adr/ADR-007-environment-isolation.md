# ADR-007: Isolate DEV, STAGING and PROD Deployment Targets

- **Status:** Accepted
- **Date:** 2026-08-29

## Decision

Maintain explicit DEV, STAGING and PROD targets with distinct configuration and controlled promotion. Production resources are not modified from developer-local state.

## Consequences

Promotion is more predictable and auditable, at the cost of additional environment configuration and deployment automation.
