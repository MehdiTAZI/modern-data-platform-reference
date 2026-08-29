from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def standardize_customers(df: DataFrame) -> DataFrame:
    return df.select(
        F.trim("customer_id").alias("customer_id"),
        F.initcap(F.trim("first_name")).alias("first_name"),
        F.initcap(F.trim("last_name")).alias("last_name"),
        F.lower(F.trim("email")).alias("email"),
        F.to_timestamp("updated_at").alias("updated_at"),
        *[F.col(column) for column in ("_ingested_at", "_source_file") if column in df.columns],
    )


def latest_customer_state(df: DataFrame) -> DataFrame:
    window = Window.partitionBy("customer_id").orderBy(
        F.col("updated_at").desc_nulls_last(), F.col("_ingested_at").desc_nulls_last()
    )
    return df.withColumn("_rn", F.row_number().over(window)).filter("_rn = 1").drop("_rn")
