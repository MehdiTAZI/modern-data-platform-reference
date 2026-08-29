# Pattern: CDC and SCD

The reference keeps two dimension semantics side by side instead of forcing one model onto every source.

## SCD1 snapshot state

`silver.customers` and `silver.products` remain deterministic latest-state materialized views. They order by source `updated_at` and use ingestion time as a stable tie-breaker.

## SCD2 history

`pipelines/retail/history.py` declares `silver.customers_history` as a Lakeflow streaming table and feeds it with `dp.create_auto_cdc_flow(..., stored_as_scd_type="2")`. `customer_id` is the business key and `updated_at` is the sequence column, so out-of-order updates are sequenced declaratively rather than with hand-written MERGE logic.

The history flow tracks changes to first name, last name and email. Transport metadata is excluded from the SCD target so ingestion-time differences do not create artificial business history.

Use SCD2 only where consumers need point-in-time history, auditability or historical dimension joins; otherwise the SCD1 surface is cheaper and simpler.

See ADR-014 and the Databricks AUTO CDC documentation.
