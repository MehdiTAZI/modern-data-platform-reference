from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

@dataclass(frozen=True)
class Contract:
    dataset: str
    keys: tuple[str, ...]
    expectations: dict[str, dict[str, str]]


def load_contract(path: str | Path) -> Contract:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    required = {"dataset", "keys", "expectations"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing contract fields: {sorted(missing)}")
    expectations = data["expectations"]
    for name, rule in expectations.items():
        if rule.get("severity") not in {"fail", "quarantine", "metric"}:
            raise ValueError(f"Invalid severity for {name}")
        if not rule.get("expression"):
            raise ValueError(f"Missing expression for {name}")
    return Contract(data["dataset"], tuple(data["keys"]), expectations)


def expectation_map(contract: Contract, severity: str) -> dict[str, str]:
    return {
        name: rule["expression"]
        for name, rule in contract.expectations.items()
        if rule["severity"] == severity
    }
