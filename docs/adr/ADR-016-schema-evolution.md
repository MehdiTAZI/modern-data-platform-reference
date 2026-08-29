# ADR-016: Schema evolution

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Bronze must tolerate producer drift without letting unreviewed fields silently redefine business-layer contracts. Consumers also need an explicit compatibility rule for planned schema evolution.

## Decision

Rescue unexpected source fields in Bronze. Promote business-layer changes through versioned contracts using an **expand → observe → enforce → contract** lifecycle.

A candidate version is backward compatible only when it increments the version, preserves dataset identity and business keys, preserves existing fields and types, and does not tighten nullable fields to non-nullable. New nullable fields and metric-only observations are the default expansion mechanism.

`customers.v2.yml` demonstrates a compatible nullable `loyalty_tier` addition. CI validates versioned candidates against the active contract before they can be promoted.

Breaking changes require a new dataset/versioned consumer surface or an explicitly coordinated migration rather than silent Silver drift.

## Alternatives considered

- Automatically promote all Bronze schema evolution into Silver.
- Permit breaking changes behind an unchanged contract version.
- Freeze schemas permanently and reject additive evolution.

## Consequences

Contract evolution becomes reviewable and mechanically testable. Producers may move faster in Bronze while consumer-facing compatibility remains deliberate.

## Reconsider when

An enterprise schema registry or contract platform becomes the authoritative compatibility engine.
