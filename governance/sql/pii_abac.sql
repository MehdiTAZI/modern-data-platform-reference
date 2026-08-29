-- Unity Catalog ABAC example for the DEV retail catalog.
--
-- Prerequisites:
--   * Unity Catalog and serverless or Databricks Runtime 16.4+ for ABAC queries.
--   * Governed-tag CREATE permission at account level for the one-time bootstrap.
--   * Databricks Runtime 18.1+ when using CREATE GOVERNED TAG from SQL.
--   * ASSIGN on the governed tag, APPLY TAG on the table, and MANAGE on the schema.
--
-- One-time account bootstrap. CREATE GOVERNED TAG has no IF NOT EXISTS form, so run once:
-- CREATE GOVERNED TAG pii
--   DESCRIPTION 'Non-secret classification label for personal-information category'
--   VALUES ('email', 'name');

ALTER TABLE retail_dev.silver.customers
ALTER COLUMN email
SET TAGS ('pii' = 'email');

CREATE OR REPLACE FUNCTION retail_dev.ops.mask_email(value STRING)
RETURNS STRING
RETURN CASE
  WHEN value IS NULL THEN NULL
  ELSE regexp_replace(value, '^(.).+(@.+)$', '$1***$2')
END;

GRANT EXECUTE ON FUNCTION retail_dev.ops.mask_email TO `account users`;

CREATE OR REPLACE POLICY retail_customer_email_mask
ON SCHEMA retail_dev.silver
COLUMN MASK retail_dev.ops.mask_email
TO `account users`
EXCEPT `data-platform-admins`, `retail-data-engineers`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'email') AS email_col
ON COLUMN email_col;
