-- Consumer surface example. Production masking/tag policies must align with enterprise classification.
CREATE OR REPLACE VIEW retail_prd.gold.customer_360_masked AS SELECT customer_id, first_name, last_name, regexp_replace(email, '(^.).*(@.*$)', '$1***$2') AS email, orders, lifetime_value FROM retail_prd.gold.customer_360;
