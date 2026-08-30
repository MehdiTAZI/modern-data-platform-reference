-- Trusted processing-boundary reconciliation. Replace retail_dev with the target catalog.

-- Canonical Silver -> canonical Gold fact.
SELECT
  'canonical_fact' AS control,
  source_rows,
  target_rows,
  row_delta,
  source_metric,
  target_metric,
  metric_delta,
  tolerance,
  rows_balanced,
  metrics_balanced,
  is_balanced
FROM retail_dev.gold.order_fact_reconciliation

UNION ALL

-- Canonical Silver -> SCD2 as-of Gold fact. This also detects overlapping history intervals
-- that would multiply one canonical order into multiple temporal fact rows.
SELECT
  'temporal_fact' AS control,
  source_rows,
  target_rows,
  row_delta,
  source_metric,
  target_metric,
  metric_delta,
  tolerance,
  rows_balanced,
  metrics_balanced,
  is_balanced
FROM retail_dev.gold.temporal_fact_reconciliation;
