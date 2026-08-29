import pytest

from mdpr.retail.config import RetailConfig


def test_environment_mapping():
    assert RetailConfig.for_environment("dev").catalog == "retail_dev"
    assert RetailConfig.for_environment("staging").catalog == "retail_stg"
    assert RetailConfig.for_environment("prod").catalog == "retail_prd"


def test_invalid_environment():
    with pytest.raises(ValueError):
        RetailConfig.for_environment("qa")
