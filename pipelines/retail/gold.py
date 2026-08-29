# ruff: noqa: F821

import sys

from pyspark import pipelines as dp
from pyspark.sql import functions as F

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.transforms.gold import customer_360, daily_sales  # noqa: E402

CATALOG = spark.conf.get("mdpr.catalog")


@dp.materialized_view(name="daily_sales", cluster_by_auto=True)
def daily_sales_mv():
    return daily_sales(spark.read.table(f"{CATALOG}.silver.orders_canonical"))


@dp.materialized_view(name="customer_360", cluster_by_auto=True)
def customer_360_mv():
    return customer_360(
        spark.read.table(f"{CATALOG}.silver.customers"),
        spark.read.table(f"{CATALOG}.silver.orders_canonical"),
    )


@dp.table(name="realtime_sales_5m", cluster_by_auto=True)
def realtime_sales_5m():
    return (
        spark.readStream.table(f"{CATALOG}.silver.orders")
        .withWatermark("event_time", "30 minutes")
        .groupBy(F.window("event_time", "5 minutes").alias("window"))
        .agg(
            F.sum(F.col("quantity") * F.col("unit_price")).alias("gross_sales"),
            F.countDistinct("order_id").alias("orders"),
        )
    )
