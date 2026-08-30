# ruff: noqa: F821

import sys
from pathlib import Path

from pyspark import pipelines as dp

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.contracts import load_contract  # noqa: E402
from mdpr.retail.quality import quality_events, quality_summary, union_quality_events  # noqa: E402

CATALOG = spark.conf.get("mdpr.catalog")
CONTRACTS = Path(spark.conf.get("mdpr.contract_root"))
CUSTOMERS = load_contract(CONTRACTS / "customers.yml")
PRODUCTS = load_contract(CONTRACTS / "products.yml")
ORDERS_INGEST = load_contract(CONTRACTS / "orders_ingest.yml")
ORDERS = load_contract(CONTRACTS / "orders.yml")


def _silver(name: str) -> str:
    return f"{CATALOG}.silver.{name}"


@dp.materialized_view(
    name="data_quality_events",
    comment=(
        "Payload-minimized quality events emitted from Silver quarantine surfaces with "
        "dataset, contract, rule and processing-stage context"
    ),
)
def data_quality_events():
    return union_quality_events(
        [
            quality_events(
                spark.read.table(_silver("customers_quarantine")),
                CUSTOMERS,
                stage="silver_customer_gate",
            ),
            quality_events(
                spark.read.table(_silver("products_quarantine")),
                PRODUCTS,
                stage="silver_product_gate",
            ),
            quality_events(
                spark.read.table(_silver("orders_parse_quarantine")),
                ORDERS_INGEST,
                stage="silver_order_shape_gate",
            ),
            quality_events(
                spark.read.table(_silver("orders_quarantine")),
                ORDERS,
                stage="silver_order_business_gate",
            ),
            quality_events(
                spark.read.table(_silver("orders_reconciliation_quarantine")),
                ORDERS,
                stage="silver_late_reconciliation",
            ),
            quality_events(
                spark.read.table(_silver("orders_reference_reprocess_remaining")),
                ORDERS,
                stage="silver_reference_reprocessing",
            ),
        ]
    )


@dp.materialized_view(
    name="data_quality_summary",
    comment="Aggregated quality failures by dataset, contract, rule and processing stage",
)
def data_quality_summary():
    return quality_summary(spark.read.table("data_quality_events"))
