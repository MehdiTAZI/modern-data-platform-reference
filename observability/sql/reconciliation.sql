-- Trusted processing-boundary reconciliation. Replace retail_dev with the target catalog.
SELECT
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
FROM retail_dev.gold.order_fact_reconciliation;
