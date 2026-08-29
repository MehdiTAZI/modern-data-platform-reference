from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from mdpr.retail.contracts import Contract

def annotate_quality(df: DataFrame, contract: Contract) -> DataFrame:
    errors = [F.when(~F.expr(rule["expression"]), F.lit(name)) for name, rule in contract.expectations.items() if rule["severity"] == "quarantine"]
    if not errors: return df.withColumn("_dq_errors", F.array().cast("array<string>"))
    return df.withColumn("_dq_errors", F.array_compact(F.array(*errors)))

def split_quarantine(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    return df.filter(F.size("_dq_errors") == 0), df.filter(F.size("_dq_errors") > 0)
