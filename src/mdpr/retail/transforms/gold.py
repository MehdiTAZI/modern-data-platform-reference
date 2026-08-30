from collections.abc import Sequence

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def customer_dimension(customers: DataFrame) -> DataFrame:
    return customers.select(
        "customer_id",
        "first_name",
        "last_name",
        F.concat_ws(" ", "first_name", "last_name").alias("full_name"),
        "email",
        "updated_at",
    )


def product_dimension(products: DataFrame) -> DataFrame:
    return products.select("product_id", "name", "unit_price", "updated_at")


def order_lines_fact(orders: DataFrame, passthrough: Sequence[str] = ()) -> DataFrame:
    return orders.select(
        "event_id",
        "order_id",
        "customer_id",
        "product_id",
        F.to_date("event_time").alias("order_date"),
        "event_time",
        "quantity",
        "unit_price",
        (F.col("quantity") * F.col("unit_price")).alias("line_amount"),
        *passthrough,
    )


def daily_sales(order_lines: DataFrame) -> DataFrame:
    return order_lines.groupBy("order_date").agg(
        F.countDistinct("order_id").alias("orders"),
        F.countDistinct("customer_id").alias("customers"),
        F.sum("line_amount").alias("gross_sales"),
    )


def customer_360(customers: DataFrame, order_lines: DataFrame) -> DataFrame:
    metrics = order_lines.groupBy("customer_id").agg(
        F.countDistinct("order_id").alias("orders"),
        F.sum("line_amount").alias("lifetime_value"),
    )
    return customers.join(metrics, "customer_id", "left").fillna({"orders": 0, "lifetime_value": 0})
