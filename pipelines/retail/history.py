# ruff: noqa: F821

import sys
from pathlib import Path

from pyspark import pipelines as dp
from pyspark.sql import functions as F

sys.path.insert(0, spark.conf.get("mdpr.src_root"))

from mdpr.retail.contracts import load_contract  # noqa: E402
from mdpr.retail.quality import annotate_quality  # noqa: E402
from mdpr.retail.transforms.customers import standardize_customers  # noqa: E402

CATALOG = spark.conf.get("mdpr.catalog")
CONTRACTS = Path(spark.conf.get("mdpr.contract_root"))
CUSTOMERS = load_contract(CONTRACTS / "customers.yml")


@dp.temporary_view(name="customers_scd2_source")
def customers_scd2_source():
    checked = annotate_quality(
        standardize_customers(spark.readStream.table(f"{CATALOG}.bronze.customers_raw")),
        CUSTOMERS,
    )
    return (
        checked.filter(F.size("_dq_errors") == 0)
        .filter(F.col("updated_at").isNotNull())
        .drop("_dq_errors", "_rescued_data")
    )


dp.create_streaming_table(
    "customers_history",
    comment="SCD2 customer history maintained declaratively by Lakeflow AUTO CDC",
)

dp.create_auto_cdc_flow(
    target="customers_history",
    source="customers_scd2_source",
    keys=["customer_id"],
    sequence_by=F.col("updated_at"),
    stored_as_scd_type="2",
    track_history_column_list=["first_name", "last_name", "email"],
    except_column_list=["_ingested_at", "_source_file"],
)
