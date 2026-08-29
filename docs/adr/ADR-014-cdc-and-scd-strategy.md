# ADR-014: CDC and SCD strategy

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Dimensions need deterministic current state for most consumers, while selected domains also need point-in-time history. Hand-written MERGE logic for every history table creates ordering and maintenance risk.

## Decision

Keep deterministic SCD1 materialized views for snapshot-oriented dimensions. When business history is required, use Lakeflow AUTO CDC with an explicit business key, sequence column and SCD2 target.

The reference implements both choices for customers:

- `silver.customers` is SCD1 latest state ordered by source `updated_at` with ingestion time as tie-breaker.
- `silver.customers_history` is maintained by `dp.create_auto_cdc_flow` with `stored_as_scd_type="2"`, keyed by `customer_id` and sequenced by `updated_at`.

Transport metadata is excluded from history tracking so ingestion mechanics do not create artificial business versions.

## Alternatives considered

- Hand-written Delta MERGE logic for every SCD2 table.
- Store history for every dimension whether needed or not.
- Keep only latest state and force consumers to reconstruct history from Bronze.

## Consequences

SCD1 remains simpler and cheaper for current-state use cases. SCD2 is available where audit or point-in-time semantics justify its additional storage and operational cost. Source sequencing quality remains a producer contract.

## Reconsider when

Source CDC semantics, sequencing guarantees, history requirements or Lakeflow capabilities materially change.
