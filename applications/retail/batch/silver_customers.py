import argparse

from pyspark.sql import functions as F

from applications.retail.common.config import RetailConfig
from applications.retail.common.quality import require_not_null
from applications.retail.common.spark import get_spark


def build_customers(environment: str) -> None:
    spark = get_spark("retail-silver-customers")
    cfg = RetailConfig.for_environment(environment)

    source = spark.table(f"{cfg.bronze_catalog}.{cfg.schema}.customers_raw")
    standardized = source.select(
        F.trim("customer_id").alias("customer_id"),
        F.initcap(F.trim("first_name")).alias("first_name"),
        F.initcap(F.trim("last_name")).alias("last_name"),
        F.lower(F.trim("email")).alias("email"),
        F.col("_ingested_at"),
    )

    valid, rejected = require_not_null(standardized, ["customer_id", "email"])
    latest = valid.dropDuplicates(["customer_id"])

    latest.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(
        f"{cfg.silver_catalog}.{cfg.schema}.customers"
    )
    rejected.write.format("delta").mode("append").saveAsTable(
        f"{cfg.silver_catalog}.{cfg.schema}.customers_quarantine"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", default="dev")
    args = parser.parse_args()
    build_customers(args.environment)
