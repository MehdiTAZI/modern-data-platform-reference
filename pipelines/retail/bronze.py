# ruff: noqa: F821

import sys

from pyspark import pipelines as dp
from pyspark.sql import functions as F
from pyspark.sql import types as T

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

CATALOG = spark.conf.get("mdpr.catalog")
LANDING = spark.conf.get("mdpr.landing_volume", "landing")
SOURCE_MODE = spark.conf.get("mdpr.orders_source_mode", "files")
KAFKA_SERVICE_CREDENTIAL = spark.conf.get("mdpr.kafka_service_credential", "")


@dp.table(name="customers_raw", comment="Replayable customer snapshots with ingestion metadata")
def customers_raw():
    path = f"/Volumes/{CATALOG}/bronze/{LANDING}/customers"
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .option("rescuedDataColumn", "_rescued_data")
        .load(path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )


@dp.table(name="products_raw", comment="Replayable product snapshots with ingestion metadata")
def products_raw():
    path = f"/Volumes/{CATALOG}/bronze/{LANDING}/products"
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .option("rescuedDataColumn", "_rescued_data")
        .load(path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )


def _file_orders():
    path = f"/Volumes/{CATALOG}/bronze/{LANDING}/orders"
    schema = T.StructType([T.StructField("value", T.StringType())])
    return (
        spark.readStream.format("text")
        .schema(schema)
        .load(path)
        .select(
            F.col("value").alias("raw_payload"),
            F.lit("file").alias("source"),
            F.input_file_name().alias("source_file"),
            F.lit(None).cast("string").alias("topic"),
            F.lit(None).cast("long").alias("partition"),
            F.lit(None).cast("long").alias("offset"),
            F.lit(None).cast("timestamp").alias("source_timestamp"),
        )
    )


def _kafka_orders():
    if not KAFKA_SERVICE_CREDENTIAL:
        raise ValueError("mdpr.kafka_service_credential is required when orders_source_mode=kafka")

    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", spark.conf.get("mdpr.kafka_bootstrap_servers"))
        .option("subscribe", spark.conf.get("mdpr.kafka_topic", "orders"))
        .option("databricks.serviceCredential", KAFKA_SERVICE_CREDENTIAL)
        .load()
        .select(
            F.col("value").cast("string").alias("raw_payload"),
            F.lit("kafka").alias("source"),
            F.lit(None).cast("string").alias("source_file"),
            "topic",
            "partition",
            "offset",
            F.col("timestamp").alias("source_timestamp"),
        )
    )


@dp.table(
    name="orders_raw", comment="Raw immutable order envelope retaining payload and source metadata"
)
def orders_raw():
    source = _kafka_orders() if SOURCE_MODE == "kafka" else _file_orders()
    return source.withColumn("_ingested_at", F.current_timestamp())
