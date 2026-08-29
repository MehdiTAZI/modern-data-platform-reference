from pyspark.sql import DataFrame, Window
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


def parse_order_envelope(df: DataFrame) -> DataFrame:
    parsed = F.from_json(F.col("raw_payload"), ORDER_SCHEMA)
    return df.withColumn("_event", parsed).select("*", "_event.*").drop("_event")


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
