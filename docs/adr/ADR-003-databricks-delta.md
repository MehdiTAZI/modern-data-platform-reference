# ADR-003: Use Databricks and Delta as the Primary Reference Implementation

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

The reference project needs one concrete implementation deep enough to demonstrate production patterns rather than remaining technology-neutral pseudocode.

## Decision

Use Databricks as the primary execution/governance platform and Delta tables as the primary lakehouse table implementation. PySpark and SQL are the primary application APIs.

## Consequences

The implementation can demonstrate governance, transactions, streaming and deployment coherently. Architectural concepts remain separated from provider-specific modules so alternate implementations can be added later.
