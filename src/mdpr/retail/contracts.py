from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Contract:
    version: int
    dataset: str
    keys: tuple[str, ...]
    expectations: dict[str, dict[str, str]]
    fields: dict[str, dict[str, Any]]


def load_contract(path: str | Path) -> Contract:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    required = {"version", "dataset", "keys", "expectations"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing contract fields: {sorted(missing)}")

    version = data["version"]
    if not isinstance(version, int) or version < 1:
        raise ValueError("Contract version must be a positive integer")

    expectations = data["expectations"]
    for name, rule in expectations.items():
        if rule.get("severity") not in {"fail", "quarantine", "metric"}:
            raise ValueError(f"Invalid severity for {name}")
        if not rule.get("expression"):
            raise ValueError(f"Missing expression for {name}")

    fields = data.get("fields", {})
    for name, spec in fields.items():
        if not spec.get("type"):
            raise ValueError(f"Missing type for field {name}")
        if "nullable" in spec and not isinstance(spec["nullable"], bool):
            raise ValueError(f"nullable must be boolean for field {name}")

    return Contract(
        version=version,
        dataset=data["dataset"],
        keys=tuple(data["keys"]),
        expectations=expectations,
        fields=fields,
    )


def expectation_map(contract: Contract, severity: str) -> dict[str, str]:
    return {
        name: rule["expression"]
        for name, rule in contract.expectations.items()
        if rule["severity"] == severity
    }


def compatibility_issues(previous: Contract, current: Contract) -> list[str]:
    issues: list[str] = []

    if current.dataset != previous.dataset:
        issues.append("dataset changed")
    if current.version <= previous.version:
        issues.append("version must increase")
    if current.keys != previous.keys:
        issues.append("business keys changed")

    for name, old in previous.fields.items():
        new = current.fields.get(name)
        if new is None:
            issues.append(f"field removed: {name}")
            continue
        if new.get("type") != old.get("type"):
            issues.append(f"field type changed: {name}")
        if old.get("nullable", True) and not new.get("nullable", True):
            issues.append(f"field became non-nullable: {name}")

    return issues


def validate_compatible_upgrade(previous: Contract, current: Contract) -> None:
    issues = compatibility_issues(previous, current)
    if issues:
        raise ValueError("Incompatible contract upgrade: " + "; ".join(issues))
