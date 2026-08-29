# Pattern: Late-event reconciliation

The low-latency `silver.orders` stream keeps a 30-minute event-time watermark. The watermark bounds state and latency; it is not treated as a promise that older business events cease to matter.

`pipelines/retail/reconciliation.py` periodically compares replayable `bronze.orders_raw` with event IDs already delivered to `silver.orders` after the watermark horizon. Missing late events are parsed, checked against customer/product references, re-evaluated against the order contract and split into:

- `orders_reconciliation_candidates` — valid late events;
- `orders_reconciliation_quarantine` — late events that still fail business/DQ checks.

`orders_canonical` unions the streaming result with validated reconciliation candidates and deterministically deduplicates by event ID. Batch Gold products use this canonical surface; the real-time five-minute KPI intentionally remains on `silver.orders`, preserving its low-latency semantics.

This separates **streaming freshness** from **analytical completeness** and makes the correction path observable instead of increasing the streaming watermark indefinitely.

See ADR-017.
