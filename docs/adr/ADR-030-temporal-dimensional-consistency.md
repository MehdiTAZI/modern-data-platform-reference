# ADR-030 — Temporal dimensional consistency

- **Status:** Accepted
- **Date:** 2026-08-30

## Context

The current-state customer dimension is appropriate for operational lookups and referential validation, but it is not sufficient for historical analytics. Joining an old order to today's customer state can rewrite historical context whenever customer attributes change.

The retail reference already maintains `customers_history` as SCD Type 2 through Lakeflow AUTO CDC. V1.6 makes the temporal semantics explicit for downstream facts.

## Decision

Historical fact enrichment uses an event-time as-of join against the SCD2 validity interval:

```text
order.customer_id = history.customer_id
AND order.event_time >= history.__START_AT
AND (history.__END_AT IS NULL OR order.event_time < history.__END_AT)
```

The interval is therefore half-open: `[__START_AT, __END_AT)`.

`gold.fact_order_lines_temporal` records the resolved customer-version start/end timestamps while avoiding replication of customer PII into the fact. A fail expectation requires a customer version to resolve for every canonical order.

Current-state Silver customer data remains the reference source for low-latency referential validation. SCD2 history is used where historical business semantics require the state that was valid when the event occurred.

## Consequences

### Positive

- historical facts are not silently reinterpreted after dimension changes;
- the repository demonstrates the distinction between current-state validation and historical-state analysis;
- temporal coverage becomes an explicit trusted invariant;
- PII duplication in Gold facts is minimized.

### Trade-offs

- interval joins are more expensive than equality joins and require physical optimization at scale;
- overlapping SCD2 intervals can duplicate facts, so SCD history integrity must be monitored;
- events earlier than the first known dimension version require an explicit business policy rather than an arbitrary fallback.

## Alternatives rejected

- **Always join the current dimension:** simple but historically incorrect after changes.
- **Copy all customer attributes into the event at ingestion:** preserves context but duplicates PII and couples producers to analytical dimensional semantics.
- **Fallback to the nearest available history row:** fabricates historical truth when temporal coverage is missing.
