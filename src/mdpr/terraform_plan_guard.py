import fnmatch
import json
from pathlib import Path
from typing import Any

DESTRUCTIVE_ACTION = "delete"


def destructive_changes(plan: dict[str, Any]) -> list[tuple[str, list[str]]]:
    findings: list[tuple[str, list[str]]] = []
    for resource in plan.get("resource_changes", []):
        address = resource.get("address", "<unknown>")
        actions = resource.get("change", {}).get("actions", [])
        if DESTRUCTIVE_ACTION in actions:
            findings.append((address, actions))
    return findings


def is_allowed(address: str, allow_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(address, pattern) for pattern in allow_patterns)


def evaluate_plan(plan: dict[str, Any], allow_patterns: list[str] | None = None) -> list[str]:
    allow_patterns = allow_patterns or []
    violations: list[str] = []
    for address, actions in destructive_changes(plan):
        if not is_allowed(address, allow_patterns):
            violations.append(f"{address}: destructive Terraform action {actions}")
    return violations


def load_plan(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read Terraform plan JSON from {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Terraform plan JSON root must be an object")
    return payload
