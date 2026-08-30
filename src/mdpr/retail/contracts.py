import dataclasses
import pathlib
import typing
import yaml


VALID_SEVERITIES = {"fail", "quarantine", "metric"}
VALID_CATEGORIES = {
    "schema",
    "completeness",
    "validity",
    "uniqueness",
    "referential",
    "temporal",
    "business",
    "operational",
}


@dataclasses.dataclass(frozen=True)
class Contract:
    version: int
    dataset: str
    keys: tuple[str, ...]
    expectations: dict[str, dict[str, typing.Any]]
    fields: dict[str, dict[str, typing.Any]]
    metadata: dict[str, typing.Any] = dataclasses.field(default_factory=dict)


def _validate_expectation(name: str, rule: dict[str, typing.Any]) -> None:
    severity = rule.get("severity")
    if severity not in VALID_SEVERITIES:
        raise ValueError(f"Invalid severity for {name}")
    if not rule.get("expression"):
        raise ValueError(f"Missing expression for {name}")

    category = rule.get("category")
    if category is not None and category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category for {name}")

    message = rule.get("message")
    if message is not None and not isinstance(message, str):
        raise ValueError(f"message must be a string for {name}")


def load_contract(path: str | pathlib.Path) -> Contract:
    data: dict[str, typing.Any] = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    required = {"version", "dataset", "keys", "expectations"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing contract fields: {sorted(missing)}")

    version = data["version"]
    if not isinstance(version, int) or version < 1:
        raise ValueError("Contract version must be a positive integer")

    expectations = data["expectations"]
    if not isinstance(expectations, dict):
        raise ValueError("Contract expectations must be a mapping")
    for name, rule in expectations.items():
        if not isinstance(rule, dict):
            raise ValueError(f"Expectation {name} must be a mapping")
        _validate_expectation(name, rule)

    fields = data.get("fields", {})
    for name, spec in fields.items():
        if not spec.get("type"):
            raise ValueError(f"Missing type for field {name}")
        if "nullable" in spec and not isinstance(spec["nullable"], bool):
            raise ValueError(f"nullable must be boolean for field {name}")

    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("Contract metadata must be a mapping")

    return Contract(
        version=version,
        dataset=data["dataset"],
        keys=tuple(data["keys"]),
        expectations=expectations,
        fields=fields,
        metadata=metadata,
    )


def expectation_map(contract: Contract, severity: str) -> dict[str, str]:
    return {
        name: rule["expression"]
        for name, rule in contract.expectations.items()
        if rule["severity"] == severity
    }


def rule_metadata(contract: Contract, rule_name: str) -> dict[str, typing.Any]:
    rule = contract.expectations[rule_name]
    return {
        "dataset": contract.dataset,
        "contract_version": contract.version,
        "rule_id": rule_name,
        "severity": rule["severity"],
        "category": rule.get("category", "business"),
        "message": rule.get("message", rule_name.replace("_", " ")),
        "expression": rule["expression"],
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
