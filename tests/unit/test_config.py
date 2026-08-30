import pytest

from mdpr.retail.config import RetailConfig


def test_environment_mapping():
    assert RetailConfig.for_environment("DEV").catalog == "retail_dev"
    assert RetailConfig.for_environment("staging").catalog == "retail_stg"
    assert RetailConfig.for_environment("prod").catalog == "retail_prd"


def test_invalid_environment():
    with pytest.raises(ValueError, match="Unsupported environment: qa"):
        RetailConfig.for_environment("qa")


def test_table_name_accepts_only_medallion_and_ops_layers():
    config = RetailConfig.for_environment("dev")
    assert config.table("silver", "orders") == "retail_dev.silver.orders"
    assert config.table("ops", "data_quality_events") == "retail_dev.ops.data_quality_events"

    with pytest.raises(ValueError, match="Unsupported layer: staging"):
        config.table("staging", "orders")
