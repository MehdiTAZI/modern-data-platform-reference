from pyspark.sql import DataFrame, functions as F


def require_not_null(df: DataFrame, columns: list[str]) -> tuple[DataFrame, DataFrame]:
    """Split a DataFrame into valid and rejected rows using required columns."""
    invalid = F.lit(False)
    for column in columns:
        invalid = invalid | F.col(column).isNull()

    rejected = df.filter(invalid).withColumn(
        "_quality_reason", F.lit(f"required_null:{','.join(columns)}")
    )
    valid = df.filter(~invalid)
    return valid, rejected
