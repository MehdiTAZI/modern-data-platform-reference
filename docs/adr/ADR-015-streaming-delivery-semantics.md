# ADR-015: Streaming delivery semantics

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference architecture needs an explicit, reviewable decision for **streaming delivery semantics** so implementation and documentation do not drift.

## Decision
Assume at-least-once sources; use event IDs, event time, watermarking, checkpoints and deterministic deduplication.

## Alternatives considered
- Keep the concern implicit in code.
- Use a different pattern per team without a common default.
- Defer the decision until production, increasing migration cost.

## Consequences
The default becomes testable and reviewable, but teams must still validate it against their scale, security, regulatory and operational constraints.

## Reconsider when
Requirements, platform capabilities, scale, compliance or ownership boundaries materially change.
