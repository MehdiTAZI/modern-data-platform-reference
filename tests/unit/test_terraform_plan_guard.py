import json

import pytest

from mdpr.terraform_plan_guard import evaluate_plan, load_plan


def plan_with(address: str, actions: list[str]) -> dict:
    return {
        "resource_changes": [
            {
                "address": address,
                "change": {"actions": actions},
            }
        ]
    }


def test_safe_actions_are_allowed() -> None:
    for actions in (["no-op"], ["read"], ["create"], ["update"]):
        assert evaluate_plan(plan_with("azurerm_resource_group.this", actions)) == []


def test_delete_is_blocked() -> None:
    violations = evaluate_plan(plan_with("azurerm_storage_account.lake", ["delete"]))
    assert violations == ["azurerm_storage_account.lake: destructive Terraform action ['delete']"]


def test_replacement_is_blocked() -> None:
    violations = evaluate_plan(plan_with("azurerm_databricks_workspace.this", ["delete", "create"]))
    assert len(violations) == 1
    assert "azurerm_databricks_workspace.this" in violations[0]


def test_exact_or_glob_allowlist_can_approve_expected_destruction() -> None:
    plan = {
        "resource_changes": [
            {
                "address": "module.logs.azurerm_log_analytics_workspace.this",
                "change": {"actions": ["delete", "create"]},
            }
        ]
    }
    assert evaluate_plan(plan, ["module.logs.*"]) == []


def test_allowlist_does_not_hide_other_deletions() -> None:
    plan = {
        "resource_changes": [
            {"address": "module.logs.one", "change": {"actions": ["delete"]}},
            {"address": "module.storage.one", "change": {"actions": ["delete"]}},
        ]
    }
    violations = evaluate_plan(plan, ["module.logs.*"])
    assert len(violations) == 1
    assert "module.storage.one" in violations[0]


def test_load_plan_rejects_invalid_json(tmp_path) -> None:
    path = tmp_path / "plan.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="Unable to read Terraform plan JSON"):
        load_plan(path)


def test_load_plan_rejects_non_object_root(tmp_path) -> None:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError, match="root must be an object"):
        load_plan(path)
