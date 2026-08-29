# ruff: noqa: F821

import sys
from pathlib import Path

from pyspark import pipelines as dp
from pyspark.sql import functions as F

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.contracts import load_contract  # noqa: E402
from mdpr.retail.quality import annotate_quality  # noqa: E402
from mdpr.retail.transforms.orders import (  # noqa: E402
    add_reference_validity,
    deduplicate_orders,
    late_reconciliation_candidates,
)

CATALOG = spark.conf.get("mdpr.catalog")
CONTRACTS = Path(spark.conf.get("mdpr.contract_root"))
ORDERS = load_contract(CONTRACTS / "orders.yml")


def _late_checked():
    candidates = late_reconciliation_candidates(
        spark.read.table(f"{CATALOG}.bronze.orders_raw"),
        spark.read.table("orders"),
        F.expr("current_timestamp() - INTERVAL 30 MINUTES"),
    )
    conformed = add_reference_validity(
        candidates,
        spark.read.table("customers"),
        spark.read.table("products"),
    )
    return annotate_quality(conformed, ORDERS)


@dp.materialized_view(
    name="orders_reconciliation_candidates",
    comment=(
        "Valid late events absent from the low-latency streaming result after the watermark horizon"
    ),
)
def orders_reconciliation_candidates():
    return _late_checked().filter(F.size("_dq_errors") == 0)


@dp.materialized_view(
    name="orders_reconciliation_quarantine",
    comment="Late raw events that still fail contract or referential checks during reconciliation",
)
def orders_reconciliation_quarantine():
    return _late_checked().filter(F.size("_dq_errors") > 0)


@dp.materialized_view(
    name="orders_canonical",
    comment=(
        "Canonical batch surface combining streaming delivery "
        "with validated late-event reconciliation"
    ),
)
def orders_canonical():
    delivered = spark.read.table("orders")
    reconciled = spark.read.table("orders_reconciliation_candidates")
    shared = [column for column in delivered.columns if column in reconciled.columns]
    return deduplicate_orders(delivered.select(shared).unionByName(reconciled.select(shared)))
