-- Data-quality operational starters. Replace retail_dev with the target environment catalog.

-- Current failure distribution by processing stage and rule.
SELECT
  dataset,
  stage,
  contract_version,
  rule_id,
  category,
  failed_records,
  first_observed_at,
  last_observed_at
FROM retail_dev.ops.data_quality_summary
ORDER BY failed_records DESC, dataset, stage, rule_id;

-- Recent row-level quality events remain payload-minimized: business key + fingerprint, no raw payload.
SELECT
  dataset,
  stage,
  rule_id,
  category,
  record_key,
  record_fingerprint,
  source_observed_at
FROM retail_dev.ops.data_quality_events
WHERE source_observed_at >= current_timestamp() - INTERVAL 24 HOURS
ORDER BY source_observed_at DESC;

-- Quarantine health signal suitable for alerting thresholds.
SELECT
  stage,
  SUM(failed_records) AS failed_records,
  MAX(last_observed_at) AS last_failure_at
FROM retail_dev.ops.data_quality_summary
GROUP BY stage
ORDER BY failed_records DESC;
