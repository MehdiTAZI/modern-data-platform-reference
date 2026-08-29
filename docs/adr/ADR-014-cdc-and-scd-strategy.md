# ADR-014: CDC and SCD strategy

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs an explicit, reviewable decision for **cdc and scd strategy** so implementation and documentation do not drift.

## Decision
Use deterministic SCD1 for snapshot dimensions; use Lakeflow AUTO CDC/SCD2 when event history is required.

## Alternatives considered
- Keep the concern implicit in code.
- Use a different pattern per team without a common default.
- Defer the decision until production, increasing migration cost.

## Consequences
The default becomes testable and reviewable, but teams must still validate it against their scale, security, regulatory and operational constraints.

## Reconsider when
Requirements, platform capabilities, scale, compliance or ownership boundaries materially change.
