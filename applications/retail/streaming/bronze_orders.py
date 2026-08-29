import argparse

from pyspark.sql import functions as F, types as T

from applications.retail.common.config import RetailConfig
from applications.retail.common.spark import get_spark

ORDER_SCHEMA = T.StructType(
    [
        T.StructField("order_id", T.StringType(), False),
        T.StructField("customer_id", T.StringType(), False),
        T.StructField("product_id", T.StringType(), False),
        T.StructField("quantity", T.IntegerType(), False),
        T.StructField("unit_price", T.DecimalType(18, 2), False),
        T.StructField("event_time", T.TimestampType(), False),
    ]
)


def stream_orders(source_table: str, checkpoint_path: str, environment: str) -> None:
    """Reference streaming pattern.

    `source_table` represents a normalized upstream stream/landing table. A Kafka/Event Hubs
    adapter can be added without changing Bronze/Silver contracts.
    """
    spark = get_spark("retail-bronze-orders")
    cfg = RetailConfig.for_environment(environment)

    events = (
        spark.readStream.table(source_table)
        .select(F.from_json(F.col("value").cast("string"), ORDER_SCHEMA).alias("event"))
        .select("event.*")
        .withColumn("_ingested_at", F.current_timestamp())
    )

    query = (
        events.writeStream.format("delta")
        .option("checkpointLocation", checkpoint_path)
        .outputMode("append")
        .toTable(f"{cfg.bronze_catalog}.{cfg.schema}.orders_raw")
    )
    query.awaitTermination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-table", required=True)
    parser.add_argument("--checkpoint-path", required=True)
    parser.add_argument("--environment", default="dev")
    args = parser.parse_args()
    stream_orders(args.source_table, args.checkpoint_path, args.environment)
