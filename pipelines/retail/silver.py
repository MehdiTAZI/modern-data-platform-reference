# ruff: noqa: F821

import sys
from pathlib import Path

from pyspark import pipelines as dp
from pyspark.sql import functions as F

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.contracts import expectation_map, load_contract  # noqa: E402
from mdpr.retail.quality import annotate_quality  # noqa: E402
from mdpr.retail.transforms.customers import (  # noqa: E402
    latest_customer_state,
    standardize_customers,
)
from mdpr.retail.transforms.orders import add_reference_validity, parse_order_envelope  # noqa: E402
from mdpr.retail.transforms.products import (  # noqa: E402
    latest_product_state,
    standardize_products,
)

CATALOG = spark.conf.get("mdpr.catalog")
CONTRACTS = Path(spark.conf.get("mdpr.contract_root"))
CUSTOMERS = load_contract(CONTRACTS / "customers.yml")
PRODUCTS = load_contract(CONTRACTS / "products.yml")
ORDERS_INGEST = load_contract(CONTRACTS / "orders_ingest.yml")
ORDERS = load_contract(CONTRACTS / "orders.yml")


# Customer path: standardize -> measure -> drop/quarantine -> latest trusted state.
@dp.temporary_view(name="customers_checked")
@dp.expect_all(expectation_map(CUSTOMERS, "metric"))
def customers_checked():
    return annotate_quality(
        standardize_customers(spark.readStream.table(f"{CATALOG}.bronze.customers_raw")),
        CUSTOMERS,
    )


@dp.table(name="customers_validated", comment="Customer rows that pass the Silver quality gate")
@dp.expect_all_or_drop(expectation_map(CUSTOMERS, "quarantine"))
def customers_validated():
    return spark.readStream.table("customers_checked").drop("_dq_errors")


@dp.table(name="customers_quarantine", comment="Rejected customer rows with explicit DQ reasons")
def customers_quarantine():
    return spark.readStream.table("customers_checked").filter(F.size("_dq_errors") > 0)


@dp.materialized_view(name="customers", comment="Latest valid conformed customer state")
@dp.expect_all_or_fail(
    {
        "trusted_customer_key": "customer_id IS NOT NULL",
        "trusted_customer_sequence": "updated_at IS NOT NULL",
    }
)
def customers():
    return latest_customer_state(spark.read.table("customers_validated"))


# Product path: standardize -> measure -> drop/quarantine -> latest trusted state.
@dp.temporary_view(name="products_checked")
@dp.expect_all(expectation_map(PRODUCTS, "metric"))
def products_checked():
    return annotate_quality(
        standardize_products(spark.readStream.table(f"{CATALOG}.bronze.products_raw")),
        PRODUCTS,
    )


@dp.table(name="products_validated", comment="Product rows that pass the Silver quality gate")
@dp.expect_all_or_drop(expectation_map(PRODUCTS, "quarantine"))
def products_validated():
    return spark.readStream.table("products_checked").drop("_dq_errors")


@dp.table(name="products_quarantine", comment="Rejected product rows with explicit DQ reasons")
def products_quarantine():
    return spark.readStream.table("products_checked").filter(F.size("_dq_errors") > 0)


@dp.materialized_view(name="products", comment="Latest valid conformed product state")
@dp.expect_all_or_fail(
    {
        "trusted_product_key": "product_id IS NOT NULL",
        "trusted_product_price": "unit_price >= 0",
    }
)
def products():
    return latest_product_state(spark.read.table("products_validated"))


# Orders use two gates. Shape/parse validation happens before watermarking and deduplication so
# malformed records cannot disappear inside stateful processing. Business/reference validation
# happens after event-time deduplication and enrichment.
@dp.table(name="orders_parsed", comment="Parsed order stream retaining the immutable raw envelope")
@dp.expect("json_parseable", "_parse_ok = true")
def orders_parsed():
    return parse_order_envelope(spark.readStream.table(f"{CATALOG}.bronze.orders_raw"))


@dp.temporary_view(name="orders_ingest_checked")
@dp.expect_all(expectation_map(ORDERS_INGEST, "metric"))
def orders_ingest_checked():
    return annotate_quality(spark.readStream.table("orders_parsed"), ORDERS_INGEST)


@dp.table(
    name="orders_parsed_validated",
    comment="Parseable order events with required event envelope fields",
)
@dp.expect_all_or_drop(expectation_map(ORDERS_INGEST, "quarantine"))
def orders_parsed_validated():
    return spark.readStream.table("orders_ingest_checked").drop("_dq_errors")


@dp.table(
    name="orders_parse_quarantine",
    comment="Malformed or structurally incomplete order events rejected before stateful processing",
)
def orders_parse_quarantine():
    return spark.readStream.table("orders_ingest_checked").filter(F.size("_dq_errors") > 0)


def _conformed_orders():
    deduplicated = (
        spark.readStream.table("orders_parsed_validated")
        .withWatermark("event_time", "30 minutes")
        .dropDuplicates(["event_id"])
    )
    return add_reference_validity(
        deduplicated,
        spark.read.table("customers"),
        spark.read.table("products"),
    )


@dp.temporary_view(name="orders_checked")
@dp.expect_all(expectation_map(ORDERS, "metric"))
def orders_checked():
    return annotate_quality(_conformed_orders(), ORDERS)


@dp.table(
    name="orders_validated",
    comment="Deduplicated and referentially valid order events after business quality rules",
)
@dp.expect_all_or_drop(expectation_map(ORDERS, "quarantine"))
def orders_validated():
    return spark.readStream.table("orders_checked").drop("_dq_errors")


@dp.table(
    name="orders_quarantine",
    comment="Business-invalid or reference-invalid order events with explicit DQ reasons",
)
def orders_quarantine():
    return spark.readStream.table("orders_checked").filter(F.size("_dq_errors") > 0)


@dp.table(name="orders", comment="Trusted Silver order stream consumed by downstream products")
@dp.expect_all_or_fail(
    {
        "trusted_event_key": "event_id IS NOT NULL",
        "trusted_order_key": "order_id IS NOT NULL",
        "trusted_customer_key": "customer_id IS NOT NULL",
        "trusted_product_key": "product_id IS NOT NULL",
        "trusted_event_time": "event_time IS NOT NULL",
        "trusted_quantity": "quantity > 0",
        "trusted_price": "unit_price >= 0",
    }
)
def orders():
    return spark.readStream.table("orders_validated")
