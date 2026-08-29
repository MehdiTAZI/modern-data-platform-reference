# Pattern: CDC and SCD
Snapshot-like dimensions use deterministic latest-state SCD1 ordered by source `updated_at` plus ingestion time. When a source emits change operations/history is required, prefer Lakeflow AUTO CDC and SCD2 rather than ad-hoc MERGE logic. See ADR-014.
