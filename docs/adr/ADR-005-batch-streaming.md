# ADR-005: Treat Batch and Streaming as First-Class Processing Patterns

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Enterprise domains commonly mix snapshots, incremental extracts, CDC and event streams.

## Decision

Support batch and Structured Streaming patterns through common governed Delta tables, shared engineering standards and compatible data-quality conventions.

## Consequences

Teams can choose latency based on business need rather than separate platform silos. Streaming introduces explicit state, checkpointing, late-data and operational-latency concerns that must be designed and tested.
