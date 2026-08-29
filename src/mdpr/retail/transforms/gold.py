from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def daily_sales(orders: DataFrame) -> DataFrame:
    return (
        orders.withColumn("order_date", F.to_date("event_time"))
        .groupBy("order_date")
        .agg(
            F.countDistinct("order_id").alias("orders"),
            F.countDistinct("customer_id").alias("customers"),
            F.sum(F.col("quantity") * F.col("unit_price")).alias("gross_sales"),
        )
    )


def customer_360(customers: DataFrame, orders: DataFrame) -> DataFrame:
    metrics = orders.groupBy("customer_id").agg(
        F.countDistinct("order_id").alias("orders"),
        F.sum(F.col("quantity") * F.col("unit_price")).alias("lifetime_value"),
    )
    return customers.join(metrics, "customer_id", "left").fillna({"orders": 0, "lifetime_value": 0})
