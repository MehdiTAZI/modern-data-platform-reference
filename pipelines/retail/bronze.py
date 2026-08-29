# ruff: noqa: F821

from pyspark import pipelines as dp
from pyspark.sql import functions as F
from pyspark.sql import types as T

CATALOG = spark.conf.get("mdpr.catalog")
LANDING = spark.conf.get("mdpr.landing_volume", "landing")
SOURCE_MODE = spark.conf.get("mdpr.orders_source_mode", "files")
KAFKA_SERVICE_CREDENTIAL = spark.conf.get("mdpr.kafka_service_credential", "")


@dp.table(
    name="customers_raw",
    comment="Source-faithful customer snapshots with ingestion metadata and rescued schema drift",
)
@dp.expect("customer_identifier_observed", "customer_id IS NOT NULL")
@dp.expect("no_rescued_customer_fields", "_rescued_data IS NULL")
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


@dp.table(
    name="products_raw",
    comment="Source-faithful product snapshots with ingestion metadata and rescued schema drift",
)
@dp.expect("product_identifier_observed", "product_id IS NOT NULL")
@dp.expect("no_rescued_product_fields", "_rescued_data IS NULL")
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
    name="orders_raw",
    comment="Immutable raw order envelope retaining payload and source transport metadata",
)
@dp.expect("raw_payload_present", "raw_payload IS NOT NULL AND length(trim(raw_payload)) > 0")
@dp.expect("supported_source", "source IN ('file', 'kafka')")
def orders_raw():
    source = _kafka_orders() if SOURCE_MODE == "kafka" else _file_orders()
    return source.withColumn("_ingested_at", F.current_timestamp())
