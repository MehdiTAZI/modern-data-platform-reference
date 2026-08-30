from functools import reduce

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from mdpr.retail.contracts import Contract, rule_metadata


def annotate_quality(df: DataFrame, contract: Contract) -> DataFrame:
    errors = [
        F.when(~F.expr(rule["expression"]), F.lit(name))
        for name, rule in contract.expectations.items()
        if rule["severity"] == "quarantine"
    ]
    if not errors:
        return df.withColumn("_dq_errors", F.array().cast("array<string>"))
    return df.withColumn("_dq_errors", F.array_compact(F.array(*errors)))


def split_quarantine(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    return df.filter(F.size("_dq_errors") == 0), df.filter(F.size("_dq_errors") > 0)


def _literal_map(values: dict[str, str]):
    items = []
    for key, value in values.items():
        items.extend([F.lit(key), F.lit(value)])
    return F.create_map(*items)


def quality_events(df: DataFrame, contract: Contract) -> DataFrame:
    """Turn row-level quarantine reasons into a stable, non-PII operational event model."""
    if "_dq_errors" not in df.columns:
        raise ValueError("quality_events requires an _dq_errors column")

    metadata = {
        name: rule_metadata(contract, name)
        for name, rule in contract.expectations.items()
        if rule["severity"] == "quarantine"
    }
    if not metadata:
        raise ValueError(f"Contract {contract.dataset} has no quarantine rules")

    categories = {name: str(values["category"]) for name, values in metadata.items()}
    messages = {name: str(values["message"]) for name, values in metadata.items()}
    expressions = {name: str(values["expression"]) for name, values in metadata.items()}

    key_columns = [column for column in contract.keys if column in df.columns]
    record_key = (
        F.to_json(F.struct(*[F.col(column) for column in key_columns]))
        if key_columns
        else F.lit(None).cast("string")
    )
    fingerprint_columns = [column for column in df.columns if column != "_dq_errors"]
    record_fingerprint = F.sha2(
        F.to_json(F.struct(*[F.col(column) for column in fingerprint_columns])), 256
    )
    source_observed_at = (
        F.col("_ingested_at").cast("timestamp")
        if "_ingested_at" in df.columns
        else F.current_timestamp()
    )

    return (
        df.filter(F.size("_dq_errors") > 0)
        .withColumn("rule_id", F.explode("_dq_errors"))
        .select(
            F.lit(contract.dataset).alias("dataset"),
            F.lit(contract.version).cast("int").alias("contract_version"),
            "rule_id",
            F.lit("quarantine").alias("severity"),
            _literal_map(categories)[F.col("rule_id")].alias("category"),
            _literal_map(messages)[F.col("rule_id")].alias("message"),
            _literal_map(expressions)[F.col("rule_id")].alias("expression"),
            record_key.alias("record_key"),
            record_fingerprint.alias("record_fingerprint"),
            source_observed_at.alias("source_observed_at"),
            F.current_timestamp().alias("materialized_at"),
        )
    )


def union_quality_events(events: list[DataFrame]) -> DataFrame:
    if not events:
        raise ValueError("At least one quality event DataFrame is required")
    return reduce(lambda left, right: left.unionByName(right), events)


def quality_summary(events: DataFrame) -> DataFrame:
    return events.groupBy(
        "dataset", "contract_version", "rule_id", "severity", "category", "message"
    ).agg(
        F.count("*").alias("failed_records"),
        F.min("source_observed_at").alias("first_observed_at"),
        F.max("source_observed_at").alias("last_observed_at"),
    )


def row_count_balance(
    source: DataFrame,
    accepted: DataFrame,
    quarantined: DataFrame,
    duplicates: DataFrame | None = None,
) -> DataFrame:
    """Return a one-row accounting control: source = accepted + quarantine + duplicate."""
    source_count = source.agg(F.count("*").alias("source_rows"))
    accepted_count = accepted.agg(F.count("*").alias("accepted_rows"))
    quarantine_count = quarantined.agg(F.count("*").alias("quarantined_rows"))
    if duplicates is None:
        duplicate_count = source.sparkSession.range(1).select(
            F.lit(0).cast("long").alias("duplicate_rows")
        )
    else:
        duplicate_count = duplicates.agg(F.count("*").alias("duplicate_rows"))

    return (
        source_count.crossJoin(accepted_count)
        .crossJoin(quarantine_count)
        .crossJoin(duplicate_count)
        .withColumn(
            "accounted_rows",
            F.col("accepted_rows") + F.col("quarantined_rows") + F.col("duplicate_rows"),
        )
        .withColumn("row_delta", F.col("source_rows") - F.col("accounted_rows"))
        .withColumn("is_balanced", F.col("row_delta") == 0)
    )


def metric_balance(
    source: DataFrame,
    target: DataFrame,
    source_expression: str,
    target_expression: str,
    tolerance: float = 0.0,
) -> DataFrame:
    """Compare one additive business metric between two processing boundaries."""
    source_metric = source.agg(
        F.coalesce(F.sum(F.expr(source_expression)), F.lit(0)).cast("decimal(38,6)").alias(
            "source_metric"
        )
    )
    target_metric = target.agg(
        F.coalesce(F.sum(F.expr(target_expression)), F.lit(0)).cast("decimal(38,6)").alias(
            "target_metric"
        )
    )
    return (
        source_metric.crossJoin(target_metric)
        .withColumn("metric_delta", F.col("source_metric") - F.col("target_metric"))
        .withColumn("tolerance", F.lit(tolerance).cast("decimal(38,6)"))
        .withColumn("is_balanced", F.abs("metric_delta") <= F.col("tolerance"))
    )
