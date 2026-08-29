# ADR-003: Databricks and Delta reference

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs an explicit, reviewable decision for **databricks and delta reference** so implementation and documentation do not drift.

## Decision
Use Azure Databricks and Delta as the deep concrete implementation while keeping architectural boundaries portable.

## Alternatives considered
- Keep the concern implicit in code.
- Use a different pattern per team without a common default.
- Defer the decision until production, increasing migration cost.

## Consequences
The default becomes testable and reviewable, but teams must still validate it against their scale, security, regulatory and operational constraints.

## Reconsider when
Requirements, platform capabilities, scale, compliance or ownership boundaries materially change.
