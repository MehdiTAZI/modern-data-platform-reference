# ADR-002: Use Bronze, Silver and Gold Data Layers

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Raw source fidelity, conformed enterprise data and consumer-ready models have different quality and lifecycle requirements.

## Decision

Use Bronze, Silver and Gold as logical responsibilities rather than as a requirement to copy every dataset three times.

- **Bronze:** source-oriented, replayable ingestion.
- **Silver:** validated, deduplicated and conformed domain entities.
- **Gold:** stable business data products and aggregates.

## Consequences

The model creates clear contracts and operational boundaries. Teams must avoid mechanical layering when a dataset does not require every stage.
