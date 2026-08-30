from dataclasses import replace

import pytest

from mdpr.retail.contracts import (
    compatibility_issues,
    expectation_map,
    load_contract,
    rule_metadata,
    validate_compatible_upgrade,
)


def _write_contract(tmp_path, body: str):
    path = tmp_path / "contract.yml"
    path.write_text(body.strip(), encoding="utf-8")
    return path


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


def test_contract_rule_metadata_defaults_are_deterministic(tmp_path):
    path = _write_contract(
        tmp_path,
        """
version: 1
dataset: example
keys: [id]
expectations:
  id_required:
    severity: quarantine
    expression: "id IS NOT NULL"
""",
    )
    metadata = rule_metadata(load_contract(path), "id_required")
    assert metadata["category"] == "business"
    assert metadata["message"] == "id required"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (
            """
dataset: invalid
keys: [id]
expectations: {}
""",
            "Missing contract fields",
        ),
        (
            """
version: 0
dataset: invalid
keys: [id]
expectations: {}
""",
            "Contract version must be a positive integer",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations: []
""",
            "Contract expectations must be a mapping",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule: not-a-mapping
""",
            "Expectation bad_rule must be a mapping",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule:
    severity: unknown
    expression: "id IS NOT NULL"
""",
            "Invalid severity for bad_rule",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule:
    severity: quarantine
""",
            "Missing expression for bad_rule",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule:
    severity: quarantine
    category: made_up
    expression: "id IS NOT NULL"
""",
            "Invalid category for bad_rule",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
expectations:
  bad_rule:
    severity: quarantine
    expression: "id IS NOT NULL"
    message: 42
""",
            "message must be a string for bad_rule",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
fields:
  id: {nullable: false}
expectations: {}
""",
            "Missing type for field id",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
fields:
  id: {type: string, nullable: no}
expectations: {}
""",
            "nullable must be boolean for field id",
        ),
        (
            """
version: 1
dataset: invalid
keys: [id]
metadata: []
expectations: {}
""",
            "Contract metadata must be a mapping",
        ),
    ],
)
def test_contract_validation_rejects_malformed_contracts(tmp_path, body, message):
    with pytest.raises(ValueError, match=message):
        load_contract(_write_contract(tmp_path, body))


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


def test_contract_upgrade_reports_dataset_version_and_field_breaks():
    current = load_contract("contracts/retail/customers.yml")
    fields = {name: dict(spec) for name, spec in current.fields.items()}
    fields["email"]["type"] = "int"
    fields["first_name"]["nullable"] = False
    candidate = replace(
        current,
        dataset="customers_v2",
        fields=fields,
    )

    issues = compatibility_issues(current, candidate)
    assert "dataset changed" in issues
    assert "version must increase" in issues
    assert "field type changed: email" in issues
    assert "field became non-nullable: first_name" in issues


def test_contract_upgrade_rejects_removed_field():
    current = load_contract("contracts/retail/customers.yml")
    candidate = replace(
        current,
        version=2,
        fields={name: spec for name, spec in current.fields.items() if name != "email"},
    )
    with pytest.raises(ValueError, match="field removed: email"):
        validate_compatible_upgrade(current, candidate)
