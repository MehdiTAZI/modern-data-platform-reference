import sys
from pathlib import Path

from pyspark import pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark: SparkSession

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
ORDERS = load_contract(CONTRACTS / "orders.yml")


@dp.materialized_view(name="customers")
@dp.expect_all_or_fail(expectation_map(CUSTOMERS, "fail"))
def customers():
    checked = annotate_quality(
        standardize_customers(spark.read.table(f"{CATALOG}.bronze.customers_raw")), CUSTOMERS
    )
    return latest_customer_state(checked).filter(F.size("_dq_errors") == 0)


@dp.materialized_view(name="customers_quarantine")
def customers_quarantine():
    checked = annotate_quality(
        standardize_customers(spark.read.table(f"{CATALOG}.bronze.customers_raw")), CUSTOMERS
    )
    return checked.filter(F.size("_dq_errors") > 0)


@dp.materialized_view(name="products")
@dp.expect_all_or_fail(expectation_map(PRODUCTS, "fail"))
def products():
    checked = annotate_quality(
        standardize_products(spark.read.table(f"{CATALOG}.bronze.products_raw")), PRODUCTS
    )
    return latest_product_state(checked).filter(F.size("_dq_errors") == 0)


@dp.materialized_view(name="products_quarantine")
def products_quarantine():
    checked = annotate_quality(
        standardize_products(spark.read.table(f"{CATALOG}.bronze.products_raw")), PRODUCTS
    )
    return checked.filter(F.size("_dq_errors") > 0)


@dp.table(name="orders_parsed", comment="Parsed order stream retaining raw envelope metadata")
def orders_parsed():
    return parse_order_envelope(spark.readStream.table(f"{CATALOG}.bronze.orders_raw"))


def _conformed_orders():
    deduplicated = (
        spark.readStream.table("orders_parsed")
        .withWatermark("event_time", "30 minutes")
        .dropDuplicates(["event_id"])
    )
    return add_reference_validity(
        deduplicated,
        spark.read.table("customers"),
        spark.read.table("products"),
    )


@dp.table(name="orders", comment="Valid order stream with event-time dedup and referential checks")
@dp.expect_all_or_fail(expectation_map(ORDERS, "fail"))
def orders():
    return annotate_quality(_conformed_orders(), ORDERS).filter(F.size("_dq_errors") == 0)


@dp.table(
    name="orders_quarantine", comment="Recoverable invalid order events with explicit DQ reasons"
)
def orders_quarantine():
    return annotate_quality(_conformed_orders(), ORDERS).filter(F.size("_dq_errors") > 0)
