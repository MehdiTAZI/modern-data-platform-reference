import argparse

from pyspark.sql import functions as F

from applications.retail.common.config import RetailConfig
from applications.retail.common.spark import get_spark


def build_daily_sales(environment: str) -> None:
    spark = get_spark("retail-gold-daily-sales")
    cfg = RetailConfig.for_environment(environment)

    orders = spark.table(f"{cfg.silver_catalog}.{cfg.schema}.orders")
    daily = (
        orders.withColumn("order_date", F.to_date("event_time"))
        .groupBy("order_date")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.countDistinct("customer_id").alias("customers"),
            F.sum(F.col("quantity") * F.col("unit_price")).alias("gross_sales"),
        )
    )

    daily.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(
        f"{cfg.gold_catalog}.{cfg.schema}.daily_sales"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", default="dev")
    args = parser.parse_args()
    build_daily_sales(args.environment)
