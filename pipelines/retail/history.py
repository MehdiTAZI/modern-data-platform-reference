# ruff: noqa: F821

from pyspark import pipelines as dp
from pyspark.sql import functions as F


dp.create_streaming_table(
    "customers_history",
    comment="SCD2 history sourced only from customer rows that passed the Silver quality gate",
)

dp.create_auto_cdc_flow(
    target="customers_history",
    source="customers_validated",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    stored_as_scd_type="2",
    track_history_column_list=["first_name", "last_name", "email"],
    except_column_list=["_ingested_at", "_source_file"],
)
