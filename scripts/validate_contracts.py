from pathlib import Path

from mdpr.retail.contracts import load_contract, validate_compatible_upgrade


def active_contract_for(candidate: Path) -> Path | None:
    stem = candidate.name.split(".v", maxsplit=1)[0]
    active = candidate.with_name(f"{stem}.yml")
    return active if active.exists() else None


if __name__ == "__main__":
    files = sorted(Path("contracts/retail").glob("*.yml"))
    assert files, "No contracts found"

    for path in files:
        contract = load_contract(path)
        assert contract.keys, f"{path}: keys must not be empty"
        print(
            f"OK {path}: v{contract.version}, "
            f"{len(contract.fields)} fields, {len(contract.expectations)} expectations"
        )

    for candidate in sorted(Path("contracts/retail").glob("*.v*.yml")):
        active = active_contract_for(candidate)
        if active is None:
            continue
        validate_compatible_upgrade(load_contract(active), load_contract(candidate))
        print(f"Compatible upgrade: {active} -> {candidate}")
