import pytest

from applications.retail.common.config import RetailConfig


def test_dev_catalogs() -> None:
    cfg = RetailConfig.for_environment("dev")
    assert cfg.bronze_catalog == "dev_bronze"
    assert cfg.silver_catalog == "dev_silver"
    assert cfg.gold_catalog == "dev_gold"


def test_prod_catalogs() -> None:
    cfg = RetailConfig.for_environment("prod")
    assert cfg.gold_catalog == "prd_gold"


def test_invalid_environment() -> None:
    with pytest.raises(ValueError):
        RetailConfig.for_environment("local")
