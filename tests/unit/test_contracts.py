from dataclasses import replace

import pytest

from mdpr.retail.contracts import (
    compatibility_issues,
    expectation_map,
    load_contract,
    rule_metadata,
    validate_compatible_upgrade,
)


def test_contract_loads():
    contract = load_contract("contracts/retail/orders.yml")
    assert contract.version == 1
    assert contract.dataset == "orders" and contract.keys == ("event_id",)
    assert contract.metadata["domain"] == "retail"
    assert "event_id_not_null" in expectation_map(contract, "quarantine")
    assert expectation_map(contract, "fail") == {}

    metadata = rule_metadata(contract, "known_customer")
    assert metadata["category"] == "referential"
    assert metadata["message"] == "Order customer must exist in trusted customer state"


def test_contract_rejects_unknown_quality_category(tmp_path):
    contract_file = tmp_path / "invalid.yml"
    contract_file.write_text(
        """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule:
    severity: quarantine
    category: made_up
    expression: "id IS NOT NULL"
""".strip()
    )

    with pytest.raises(ValueError, match="Invalid category for bad_rule"):
        load_contract(contract_file)


def test_customer_v2_is_backward_compatible():
    current = load_contract("contracts/retail/customers.yml")
    candidate = load_contract("contracts/retail/customers.v2.yml")
    assert compatibility_issues(current, candidate) == []
    validate_compatible_upgrade(current, candidate)


def test_contract_upgrade_rejects_key_change():
    current = load_contract("contracts/retail/customers.yml")
    candidate = replace(current, version=2, keys=("legacy_customer_id",))
    assert "business keys changed" in compatibility_issues(current, candidate)
    with pytest.raises(ValueError, match="business keys changed"):
        validate_compatible_upgrade(current, candidate)


def test_contract_upgrade_rejects_removed_field():
    current = load_contract("contracts/retail/customers.yml")
    candidate = replace(
        current,
        version=2,
        fields={name: spec for name, spec in current.fields.items() if name != "email"},
    )
    with pytest.raises(ValueError, match="field removed: email"):
        validate_compatible_upgrade(current, candidate)
