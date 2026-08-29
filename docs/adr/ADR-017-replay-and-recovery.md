# ADR-017: Replay, late data and recovery

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Streaming watermarks bound state and latency but can exclude valid events that arrive after the configured horizon. Increasing the watermark indefinitely damages streaming efficiency and still does not replace a replay strategy.

## Decision

Treat retained Bronze/source data as the replay authority. Keep the 30-minute event-time watermark on the low-latency `silver.orders` stream, then reconcile older missing events separately from replayable Bronze.

The reconciliation flow anti-joins raw event IDs against delivered Silver IDs after the watermark horizon, reapplies parsing, referential integrity and data-quality rules, and publishes:

- `orders_reconciliation_candidates` for valid late events;
- `orders_reconciliation_quarantine` for invalid late events;
- `orders_canonical` as the deduplicated analytical surface combining streaming delivery and validated late recovery.

Batch Gold products use `orders_canonical`; the real-time KPI intentionally remains on the low-latency stream.

Full checkpoint/source replay is reserved for broader incidents such as transformation defects, checkpoint corruption or historical contract reprocessing.

## Alternatives considered

- Increase the streaming watermark until late data is practically impossible.
- Drop late data permanently.
- Rebuild Silver manually during every late-data incident.

## Consequences

Streaming freshness and analytical completeness have explicit, different SLIs. Bronze retention and stable event IDs become critical recovery dependencies.

## Reconsider when

Source lateness distributions, business completeness requirements or native reconciliation capabilities change.
