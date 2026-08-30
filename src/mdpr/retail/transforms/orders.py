from datetime import datetime

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

ORDER_SCHEMA = T.StructType(
    [
        T.StructField("event_id", T.StringType()),
        T.StructField("order_id", T.StringType()),
        T.StructField("customer_id", T.StringType()),
        T.StructField("product_id", T.StringType()),
        T.StructField("quantity", T.IntegerType()),
        T.StructField("unit_price", T.DecimalType(18, 2)),
        T.StructField("event_time", T.TimestampType()),
    ]
)

ORDER_PARSE_SCHEMA = T.StructType(
    [*ORDER_SCHEMA.fields, T.StructField("_corrupt_record", T.StringType())]
)


def parse_order_envelope(df: DataFrame) -> DataFrame:
    parsed = F.from_json(
        F.col("raw_payload"),
        ORDER_PARSE_SCHEMA,
        {"mode": "PERMISSIVE", "columnNameOfCorruptRecord": "_corrupt_record"},
    )
    return (
        df.withColumn("_event", parsed)
        .withColumn("_parse_ok", F.col("_event._corrupt_record").isNull())
        .select("*", "_event.*")
        .drop("_event")
    )


def deduplicate_orders(df: DataFrame) -> DataFrame:
    window = Window.partitionBy("event_id").orderBy(
        F.col("event_time").desc_nulls_last(), F.col("_ingested_at").desc_nulls_last()
    )
    return df.withColumn("_rn", F.row_number().over(window)).filter("_rn = 1").drop("_rn")


def add_reference_validity(
    orders: DataFrame, customers: DataFrame, products: DataFrame
) -> DataFrame:
    customer_keys = (
        customers.select("customer_id").distinct().withColumn("_known_customer", F.lit(True))
    )
    product_keys = (
        products.select("product_id").distinct().withColumn("_known_product", F.lit(True))
    )
    return (
        orders.join(customer_keys, "customer_id", "left")
        .join(product_keys, "product_id", "left")
        .withColumn("_known_customer", F.coalesce("_known_customer", F.lit(False)))
        .withColumn("_known_product", F.coalesce("_known_product", F.lit(False)))
    )


def revalidate_order_quarantine(
    quarantined_orders: DataFrame, customers: DataFrame, products: DataFrame
) -> DataFrame:
    """Re-evaluate reference validity without mutating the original quarantined record."""
    technical_columns = [
        column
        for column in ("_dq_errors", "_known_customer", "_known_product")
        if column in quarantined_orders.columns
    ]
    return add_reference_validity(
        quarantined_orders.drop(*technical_columns),
        customers,
        products,
    )


def enrich_orders_with_customer_as_of(
    orders: DataFrame,
    customer_history: DataFrame,
    start_column: str = "__START_AT",
    end_column: str = "__END_AT",
) -> DataFrame:
    """Join each fact event to the SCD2 customer version valid at event time."""
    required_history = {"customer_id", start_column, end_column}
    missing = required_history - set(customer_history.columns)
    if missing:
        raise ValueError(f"Customer history is missing temporal columns: {sorted(missing)}")

    order = orders.alias("orders")
    history = customer_history.alias("history")
    condition = (
        (F.col("orders.customer_id") == F.col("history.customer_id"))
        & (F.col("orders.event_time") >= F.col(f"history.{start_column}"))
        & (
            F.col(f"history.{end_column}").isNull()
            | (F.col("orders.event_time") < F.col(f"history.{end_column}"))
        )
    )
    return order.join(history, condition, "left").select(
        "orders.*",
        F.col(f"history.{start_column}").alias("customer_version_start"),
        F.col(f"history.{end_column}").alias("customer_version_end"),
    )


def late_reconciliation_candidates(
    raw_orders: DataFrame,
    delivered_orders: DataFrame,
    watermark_cutoff: Column | datetime | str,
) -> DataFrame:
    if isinstance(watermark_cutoff, Column):
        cutoff = watermark_cutoff
    else:
        value = (
            watermark_cutoff.isoformat()
            if isinstance(watermark_cutoff, datetime)
            else watermark_cutoff
        )
        cutoff = F.to_timestamp(F.lit(value))

    delivered_ids = delivered_orders.select("event_id").filter("event_id IS NOT NULL").distinct()
    return (
        parse_order_envelope(raw_orders)
        .filter(F.col("_parse_ok"))
        .filter(F.col("event_id").isNotNull())
        .filter(F.col("event_time").isNotNull())
        .filter(F.col("event_time") < cutoff)
        .join(delivered_ids, "event_id", "left_anti")
    )
