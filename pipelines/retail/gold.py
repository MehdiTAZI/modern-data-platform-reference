# ruff: noqa: F821

import sys

from pyspark import pipelines as dp
from pyspark.sql import functions as F

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.transforms.gold import (  # noqa: E402
    customer_360,
    customer_dimension,
    daily_sales,
    order_lines_fact,
    product_dimension,
)

CATALOG = spark.conf.get("mdpr.catalog")


@dp.materialized_view(name="dim_customers", cluster_by_auto=True)
@dp.expect_or_fail("customer_dimension_key", "customer_id IS NOT NULL")
def dim_customers():
    return customer_dimension(spark.read.table(f"{CATALOG}.silver.customers"))


@dp.materialized_view(name="dim_products", cluster_by_auto=True)
@dp.expect_all_or_fail(
    {
        "product_dimension_key": "product_id IS NOT NULL",
        "product_dimension_price": "unit_price >= 0",
    }
)
def dim_products():
    return product_dimension(spark.read.table(f"{CATALOG}.silver.products"))


@dp.materialized_view(name="fact_order_lines", cluster_by_auto=True)
@dp.expect_all_or_fail(
    {
        "fact_event_key": "event_id IS NOT NULL",
        "fact_order_key": "order_id IS NOT NULL",
        "fact_customer_key": "customer_id IS NOT NULL",
        "fact_product_key": "product_id IS NOT NULL",
        "fact_order_date": "order_date IS NOT NULL",
        "fact_line_amount": "line_amount >= 0",
    }
)
def fact_order_lines():
    return order_lines_fact(spark.read.table(f"{CATALOG}.silver.orders_canonical"))


@dp.materialized_view(name="daily_sales", cluster_by_auto=True)
@dp.expect_all_or_fail(
    {
        "sales_date_present": "order_date IS NOT NULL",
        "sales_orders_non_negative": "orders >= 0",
        "sales_customers_non_negative": "customers >= 0",
        "sales_amount_non_negative": "gross_sales >= 0",
    }
)
def daily_sales_mv():
    return daily_sales(spark.read.table("fact_order_lines"))


@dp.materialized_view(name="customer_360", cluster_by_auto=True)
@dp.expect_all_or_fail(
    {
        "customer_360_key": "customer_id IS NOT NULL",
        "customer_360_orders_non_negative": "orders >= 0",
        "customer_360_value_non_negative": "lifetime_value >= 0",
    }
)
def customer_360_mv():
    return customer_360(
        spark.read.table("dim_customers"),
        spark.read.table("fact_order_lines"),
    )


@dp.table(name="realtime_sales_5m", cluster_by_auto=True)
@dp.expect_all_or_fail(
    {
        "realtime_window_present": "window IS NOT NULL",
        "realtime_order_lines_positive": "order_lines > 0",
        "realtime_sales_non_negative": "gross_sales >= 0",
    }
)
def realtime_sales_5m():
    return (
        spark.readStream.table(f"{CATALOG}.silver.orders")
        .withWatermark("event_time", "30 minutes")
        .groupBy(F.window("event_time", "5 minutes").alias("window"))
        .agg(
            F.sum(F.col("quantity") * F.col("unit_price")).alias("gross_sales"),
            F.count("*").alias("order_lines"),
            F.approx_count_distinct("order_id").alias("approx_orders"),
            F.approx_count_distinct("customer_id").alias("approx_customers"),
        )
    )
