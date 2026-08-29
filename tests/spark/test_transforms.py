import pytest

pytest.importorskip("pyspark")

from mdpr.retail.transforms.customers import latest_customer_state, standardize_customers
from mdpr.retail.transforms.gold import daily_sales
from mdpr.retail.transforms.orders import deduplicate_orders

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
    from mdpr.retail.transforms.orders import add_reference_validity, parse_order_envelope

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
    assert row.event_id == "E1" and row._known_customer and row._known_product


def test_gold_outputs(spark):
    from pyspark.sql import functions as F

    from mdpr.retail.transforms.gold import customer_360

    orders = spark.createDataFrame(
        [("O1", "C1", 2, 5.0, "2026-01-01 10:00:00")],
        ["order_id", "customer_id", "quantity", "unit_price", "event_time"],
    ).withColumn("event_time", F.to_timestamp("event_time"))
    customers = spark.createDataFrame([("C1", "A")], ["customer_id", "first_name"])
    assert daily_sales(orders).collect()[0].gross_sales == 10.0
    assert customer_360(customers, orders).collect()[0].orders == 1
