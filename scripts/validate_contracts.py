from pathlib import Path
from mdpr.retail.contracts import load_contract

if __name__ == "__main__":
    files = sorted(Path("contracts/retail").glob("*.yml"))
    assert files, "No contracts found"
    for path in files:
        contract = load_contract(path)
        assert contract.keys, f"{path}: keys must not be empty"
        print(f"OK {path}: {len(contract.expectations)} expectations")
