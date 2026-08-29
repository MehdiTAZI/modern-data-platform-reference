# ADR-009: Catalog and schema model

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs an explicit, reviewable decision for **catalog and schema model** so implementation and documentation do not drift.

## Decision
Use catalog=`retail_<env>` and schema=`layer` for this single-domain reference; reconsider for broader domain topology.

## Alternatives considered
- Keep the concern implicit in code.
- Use a different pattern per team without a common default.
- Defer the decision until production, increasing migration cost.

## Consequences
The default becomes testable and reviewable, but teams must still validate it against their scale, security, regulatory and operational constraints.

## Reconsider when
Requirements, platform capabilities, scale, compliance or ownership boundaries materially change.
