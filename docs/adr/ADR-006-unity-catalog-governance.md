# ADR-006: Unity Catalog governance

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs an explicit, reviewable decision for **unity catalog governance** so implementation and documentation do not drift.

## Decision
Use Unity Catalog as the authorization, lineage and governed storage abstraction boundary.

## Alternatives considered
- Keep the concern implicit in code.
- Use a different pattern per team without a common default.
- Defer the decision until production, increasing migration cost.

## Consequences
The default becomes testable and reviewable, but teams must still validate it against their scale, security, regulatory and operational constraints.

## Reconsider when
Requirements, platform capabilities, scale, compliance or ownership boundaries materially change.
