import argparse

from pyspark.sql import functions as F

from applications.retail.common.config import RetailConfig
from applications.retail.common.spark import get_spark


def ingest_customers(source_path: str, environment: str) -> None:
    spark = get_spark("retail-bronze-customers")
    cfg = RetailConfig.for_environment(environment)

    source = (
        spark.read.option("header", True)
        .option("inferSchema", False)
        .csv(source_path)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )

    target = f"{cfg.bronze_catalog}.{cfg.schema}.customers_raw"
    source.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--environment", default="dev")
    args = parser.parse_args()
    ingest_customers(args.source_path, args.environment)
