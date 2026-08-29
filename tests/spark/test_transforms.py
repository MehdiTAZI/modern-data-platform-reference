import pytest

pytest.importorskip("pyspark")

from mdpr.retail.transforms.customers import latest_customer_state, standardize_customers
from mdpr.retail.transforms.gold import (
    customer_360,
    customer_dimension,
    daily_sales,
    order_lines_fact,
    product_dimension,
)
from mdpr.retail.transforms.orders import (
    deduplicate_orders,
    late_reconciliation_candidates,
    parse_order_envelope,
)

pytestmark = pytest.mark.spark


def test_latest_customer_wins(spark):
    df = spark.createDataFrame(
        [
            ("C1", "a", "b", "A@X.COM", "2026-01-01 00:00:00", "2026-01-01 00:00:01"),
            ("C1", "a", "new", "a@x.com", "2026-01-02 00:00:00", "2026-01-02 00:00:01"),
        ],
        ["customer_id", "first_name", "last_name", "email", "updated_at", "_ingested_at"],
    )
    row = latest_customer_state(standardize_customers(df)).collect()[0]
    assert row.last_name == "New"


def test_order_dedup(spark):
    from pyspark.sql import functions as F

    df = spark.createDataFrame(
        [
            ("E1", "2026-01-01 00:00:00", "2026-01-01 00:00:01"),
            ("E1", "2026-01-01 00:00:00", "2026-01-01 00:00:02"),
        ],
        ["event_id", "event_time", "_ingested_at"],
    )
    df = df.withColumn("event_time", F.to_timestamp("event_time")).withColumn(
        "_ingested_at", F.to_timestamp("_ingested_at")
    )
    assert deduplicate_orders(df).count() == 1


def test_late_reconciliation_only_returns_missing_events_before_cutoff(spark):
    raw = spark.createDataFrame(
        [
            (
                '{"event_id":"E1","order_id":"O1","customer_id":"C1","product_id":"P1",'
                '"quantity":1,"unit_price":10.0,"event_time":"2026-01-01T00:00:00Z"}',
                "2026-01-01 00:05:00",
            ),
            (
                '{"event_id":"E2","order_id":"O2","customer_id":"C1","product_id":"P1",'
                '"quantity":1,"unit_price":10.0,"event_time":"2026-01-01T00:10:00Z"}',
                "2026-01-01 02:05:00",
            ),
            (
                '{"event_id":"E3","order_id":"O3","customer_id":"C1","product_id":"P1",'
                '"quantity":1,"unit_price":10.0,"event_time":"2026-01-01T02:00:00Z"}',
                "2026-01-01 02:05:00",
            ),
            ("not-json", "2026-01-01 02:05:00"),
        ],
        ["raw_payload", "_ingested_at"],
    )
    delivered = spark.createDataFrame([("E1",)], ["event_id"])

    rows = (
        late_reconciliation_candidates(raw, delivered, "2026-01-01 01:00:00")
        .select("event_id")
        .collect()
    )

    assert [row.event_id for row in rows] == ["E2"]


def test_product_latest_and_quality(spark):
    from mdpr.retail.contracts import load_contract
    from mdpr.retail.quality import annotate_quality, split_quarantine
    from mdpr.retail.transforms.products import latest_product_state, standardize_products

    df = spark.createDataFrame(
        [
            ("P1", "Old", "10.0", "2026-01-01 00:00:00", "2026-01-01 00:00:01"),
            ("P1", "New", "11.0", "2026-01-02 00:00:00", "2026-01-02 00:00:01"),
            ("P2", "Bad", "-1.0", "2026-01-01 00:00:00", "2026-01-01 00:00:01"),
        ],
        ["product_id", "name", "unit_price", "updated_at", "_ingested_at"],
    )
    checked = annotate_quality(
        standardize_products(df), load_contract("contracts/retail/products.yml")
    )
    valid, rejected = split_quarantine(checked)
    assert rejected.count() == 1
    assert latest_product_state(valid).filter("product_id = 'P1'").collect()[0].name == "New"


def test_parse_and_reference_validity(spark):
    from mdpr.retail.transforms.orders import add_reference_validity

    raw = spark.createDataFrame(
        [
            (
                '{"event_id":"E1","order_id":"O1","customer_id":"C1","product_id":"P1",'
                '"quantity":1,"unit_price":10.0,"event_time":"2026-01-01T00:00:00Z"}',
            )
        ],
        ["raw_payload"],
    )
    parsed = parse_order_envelope(raw)
    customers = spark.createDataFrame([("C1",)], ["customer_id"])
    products = spark.createDataFrame([("P1",)], ["product_id"])
    row = add_reference_validity(parsed, customers, products).collect()[0]
    assert row.event_id == "E1" and row._parse_ok and row._known_customer and row._known_product


def test_invalid_order_payload_is_explicitly_marked(spark):
    row = parse_order_envelope(spark.createDataFrame([("not-json",)], ["raw_payload"])).collect()[0]
    assert row._parse_ok is False
    assert row.event_id is None


def test_gold_outputs(spark):
    from pyspark.sql import functions as F

    orders = spark.createDataFrame(
        [("E1", "O1", "C1", "P1", 2, 5.0, "2026-01-01 10:00:00")],
        [
            "event_id",
            "order_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price",
            "event_time",
        ],
    ).withColumn("event_time", F.to_timestamp("event_time"))
    customers = spark.createDataFrame(
        [("C1", "Ada", "Lovelace", "ada@example.com", "2026-01-01 00:00:00")],
        ["customer_id", "first_name", "last_name", "email", "updated_at"],
    ).withColumn("updated_at", F.to_timestamp("updated_at"))
    products = spark.createDataFrame(
        [("P1", "Widget", 5.0, "2026-01-01 00:00:00")],
        ["product_id", "name", "unit_price", "updated_at"],
    ).withColumn("updated_at", F.to_timestamp("updated_at"))

    fact = order_lines_fact(orders)
    dim_customers = customer_dimension(customers)
    dim_products = product_dimension(products)

    assert fact.collect()[0].line_amount == 10.0
    assert daily_sales(fact).collect()[0].gross_sales == 10.0
    assert customer_360(dim_customers, fact).collect()[0].orders == 1
    assert dim_customers.collect()[0].full_name == "Ada Lovelace"
    assert dim_products.collect()[0].name == "Widget"
