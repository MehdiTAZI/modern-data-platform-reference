import pytest

pytest.importorskip("pyspark")

from mdpr.retail.contracts import Contract, load_contract
from mdpr.retail.quality import (
    annotate_quality,
    processing_boundary_balance,
    quality_events,
    row_count_balance,
)
from mdpr.retail.transforms.orders import (
    enrich_orders_with_customer_as_of,
    revalidate_order_quarantine,
)

pytestmark = pytest.mark.spark


def test_quality_events_normalize_contract_metadata(spark):
    from pyspark.sql import functions as F

    contract = Contract(
        version=3,
        dataset="example",
        keys=("id",),
        fields={},
        metadata={"owner": "platform"},
        expectations={
            "id_required": {
                "severity": "quarantine",
                "category": "completeness",
                "expression": "id IS NOT NULL",
                "message": "Identifier is required",
            }
        },
    )
    checked = spark.createDataFrame(
        [("R1", "2026-01-01 00:00:00", ["id_required"])],
        ["id", "_ingested_at", "_dq_errors"],
    ).withColumn("_ingested_at", F.to_timestamp("_ingested_at"))

    event = quality_events(checked, contract, stage="silver_gate").collect()[0]

    assert event.dataset == "example"
    assert event.stage == "silver_gate"
    assert event.contract_version == 3
    assert event.rule_id == "id_required"
    assert event.category == "completeness"
    assert event.message == "Identifier is required"
    assert event.record_key == '{"id":"R1"}'
    assert len(event.record_fingerprint) == 64


def test_null_quality_expression_is_a_violation(spark):
    contract = Contract(
        version=1,
        dataset="example",
        keys=("id",),
        fields={},
        expectations={
            "positive_value": {
                "severity": "quarantine",
                "category": "business",
                "expression": "value > 0",
                "message": "Value must be positive",
            }
        },
    )
    checked = annotate_quality(
        spark.createDataFrame([("R1", None)], "id string, value int"),
        contract,
    ).collect()[0]

    assert checked._dq_errors == ["positive_value"]


def test_reference_quarantine_becomes_reprocessable_when_dimension_arrives(spark):
    from pyspark.sql import functions as F

    quarantined = spark.createDataFrame(
        [
            (
                "E1",
                "O1",
                "C-late",
                "P1",
                1,
                10.0,
                "2026-01-01 12:00:00",
                "2026-01-01 12:01:00",
                False,
                True,
                ["known_customer"],
            )
        ],
        [
            "event_id",
            "order_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "event_time",
            "_ingested_at",
            "_known_customer",
            "_known_product",
            "_dq_errors",
        ],
    ).withColumn("event_time", F.to_timestamp("event_time")).withColumn(
        "_ingested_at", F.to_timestamp("_ingested_at")
    )
    customers = spark.createDataFrame([("C-late",)], ["customer_id"])
    products = spark.createDataFrame([("P1",)], ["product_id"])

    revalidated = revalidate_order_quarantine(quarantined, customers, products)
    checked = annotate_quality(revalidated, load_contract("contracts/retail/orders.yml"))
    row = checked.collect()[0]

    assert row._known_customer is True
    assert row._known_product is True
    assert row._dq_errors == []


def test_reference_reprocessing_does_not_hide_other_business_errors(spark):
    from pyspark.sql import functions as F

    quarantined = spark.createDataFrame(
        [
            (
                "E1",
                "O1",
                "C1",
                "P1",
                -2,
                10.0,
                "2026-01-01 12:00:00",
                "2026-01-01 12:01:00",
                False,
                True,
                ["known_customer", "quantity_positive"],
            )
        ],
        [
            "event_id",
            "order_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "event_time",
            "_ingested_at",
            "_known_customer",
            "_known_product",
            "_dq_errors",
        ],
    ).withColumn("event_time", F.to_timestamp("event_time")).withColumn(
        "_ingested_at", F.to_timestamp("_ingested_at")
    )
    customers = spark.createDataFrame([("C1",)], ["customer_id"])
    products = spark.createDataFrame([("P1",)], ["product_id"])

    checked = annotate_quality(
        revalidate_order_quarantine(quarantined, customers, products),
        load_contract("contracts/retail/orders.yml"),
    ).collect()[0]

    assert checked._known_customer is True
    assert checked._dq_errors == ["quantity_positive"]


def test_temporal_join_resolves_customer_version_at_event_time(spark):
    from pyspark.sql import functions as F

    orders = spark.createDataFrame(
        [
            ("E1", "C1", "2026-01-15 10:00:00"),
            ("E2", "C1", "2026-02-15 10:00:00"),
        ],
        ["event_id", "customer_id", "event_time"],
    ).withColumn("event_time", F.to_timestamp("event_time"))
    history = spark.createDataFrame(
        [
            ("C1", "2026-01-01 00:00:00", "2026-02-01 00:00:00"),
            ("C1", "2026-02-01 00:00:00", None),
        ],
        ["customer_id", "__START_AT", "__END_AT"],
    ).withColumn("__START_AT", F.to_timestamp("__START_AT")).withColumn(
        "__END_AT", F.to_timestamp("__END_AT")
    )

    rows = {
        row.event_id: row
        for row in enrich_orders_with_customer_as_of(orders, history).collect()
    }

    assert str(rows["E1"].customer_version_start) == "2026-01-01 00:00:00"
    assert str(rows["E2"].customer_version_start) == "2026-02-01 00:00:00"
    assert rows["E2"].customer_version_end is None


def test_processing_boundary_reconciles_rows_and_amounts(spark):
    source = spark.createDataFrame(
        [("E1", 2, 5.0), ("E2", 1, 7.5)],
        ["event_id", "quantity", "unit_price"],
    )
    target = spark.createDataFrame(
        [("E1", 10.0), ("E2", 7.5)],
        ["event_id", "line_amount"],
    )

    balanced = processing_boundary_balance(
        source,
        target,
        source_expression="quantity * unit_price",
        target_expression="line_amount",
        tolerance=0.01,
    ).collect()[0]

    assert balanced.source_rows == balanced.target_rows == 2
    assert balanced.rows_balanced is True
    assert balanced.metrics_balanced is True
    assert balanced.is_balanced is True


def test_processing_boundary_detects_row_or_amount_drift(spark):
    source = spark.createDataFrame(
        [("E1", 2, 5.0), ("E2", 1, 7.5)],
        ["event_id", "quantity", "unit_price"],
    )
    target = spark.createDataFrame([("E1", 9.0)], ["event_id", "line_amount"])

    result = processing_boundary_balance(
        source,
        target,
        source_expression="quantity * unit_price",
        target_expression="line_amount",
        tolerance=0.01,
    ).collect()[0]

    assert result.rows_balanced is False
    assert result.metrics_balanced is False
    assert result.is_balanced is False


def test_row_accounting_makes_duplicate_disposition_explicit(spark):
    source = spark.createDataFrame([("E1",), ("E1",), ("E2",)], ["event_id"])
    accepted = spark.createDataFrame([("E1",)], ["event_id"])
    quarantined = spark.createDataFrame([("E2",)], ["event_id"])
    duplicates = spark.createDataFrame([("E1",)], ["event_id"])

    balance = row_count_balance(source, accepted, quarantined, duplicates).collect()[0]

    assert balance.source_rows == 3
    assert balance.accounted_rows == 3
    assert balance.row_delta == 0
    assert balance.is_balanced is True
