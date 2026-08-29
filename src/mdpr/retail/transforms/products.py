from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def standardize_products(df: DataFrame) -> DataFrame:
    return df.select(
        F.trim("product_id").alias("product_id"),
        F.trim("name").alias("name"),
        F.col("unit_price").cast("decimal(18,2)").alias("unit_price"),
        F.to_timestamp("updated_at").alias("updated_at"),
        *[F.col(c) for c in ("_ingested_at", "_source_file") if c in df.columns],
    )


def latest_product_state(df: DataFrame) -> DataFrame:
    window = Window.partitionBy("product_id").orderBy(F.col("updated_at").desc_nulls_last(), F.col("_ingested_at").desc_nulls_last())
    return df.withColumn("_rn", F.row_number().over(window)).filter("_rn = 1").drop("_rn")
