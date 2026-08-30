# ADR-029 — Quality telemetry and reprocessing semantics

- **Status:** Accepted
- **Date:** 2026-08-30

## Context

Silver is the trust boundary for the retail data product. V1.5 already separates validated and quarantined records, but a production data product needs to distinguish three different concerns:

1. a source record can be invalid and must remain auditable;
2. a record can be temporarily invalid because reference data has not arrived yet;
3. a trusted processing boundary can regress even when every individual row appears valid.

Treating all three cases as the same `expectation` problem either loses data, creates noisy pipeline failures or hides accounting defects.

## Decision

### Immutable quarantine

A row rejected by a Silver quality gate remains in its original quarantine surface with `_dq_errors`. Reprocessing never updates or deletes the original rejected record.

### Reference-data reprocessing

Orders rejected because customer or product reference data was unavailable are periodically re-evaluated against the current trusted dimensions. All quality rules are evaluated again, not only referential rules.

A record is eligible for canonical recovery only when `_dq_errors` becomes empty. A row whose missing reference is fixed but which still has a business defect remains rejected.

Recovered reference-late rows are unioned with low-latency delivered rows and late-event reconciliation candidates before deterministic canonical deduplication.

### Quality telemetry

Quarantine reasons are normalized into the `ops.data_quality_events` model with:

- dataset and contract version;
- processing stage;
- rule identifier, category and message;
- business key when available;
- record fingerprint;
- source observation and materialization timestamps.

The model deliberately does not replicate the raw business payload. Access to the operations schema is still governed because business keys can themselves be sensitive identifiers.

`ops.data_quality_summary` aggregates this model for alerting and trend analysis.

### Dataset-level assertions

Trusted boundaries also use accounting controls. The Gold `order_fact_reconciliation` surface compares:

- canonical Silver row count against Gold fact row count;
- canonical `quantity * unit_price` against Gold `line_amount`;
- configured numeric tolerance.

These controls use fail expectations. A mismatch is not a source-data quarantine event; it indicates a transformation or contract regression in a trusted path.

### Null semantics

A row-level contract expression that evaluates to `NULL` is treated as a failed quality rule, matching the intent of declarative expectations where only `TRUE` satisfies the constraint.

## Consequences

### Positive

- source defects remain auditable;
- eventually-consistent reference data does not cause permanent data loss;
- remediation behavior is deterministic and testable;
- DQ operations have a stable query model independent of individual quarantine schemas;
- aggregate loss or duplication can fail a trusted boundary even when row checks pass.

### Trade-offs

- reprocessing adds batch work proportional to retained quarantine volume;
- business keys in operations telemetry require governance even without payload replication;
- canonical deduplication must remain deterministic when the same event is recovered through multiple paths;
- alert thresholds and retention for DQ telemetry remain environment-specific operational policy.

## Alternatives rejected

- **Drop invalid records:** loses forensic and recovery capability.
- **Fail Silver on every invalid source row:** couples availability to source cleanliness.
- **Automatically repair business-invalid values:** changes source semantics and hides defects.
- **Reprocess only the original failed rule:** can promote rows that still violate another current rule.
- **Rely only on row expectations:** cannot detect aggregate loss, duplication or transformation drift across processing boundaries.
