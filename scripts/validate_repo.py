from pathlib import Path

REQUIRED = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "databricks.yml",
    "pyproject.toml",
    ".github/workflows/deploy.yml",
    "docs/adr/README.md",
    "docs/deployment/cloud-evidence.md",
    "docs/evidence/README.md",
    "infra/stacks/azure-foundation/main.tf",
    "scripts/bootstrap_azure_state.sh",
    "scripts/upload_reference_data.sh",
]

if __name__ == "__main__":
    missing = [path for path in REQUIRED if not Path(path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    adrs = list(Path("docs/adr").glob("ADR-*.md"))
    if len(adrs) < 24:
        raise SystemExit("Expected at least 24 ADRs")

    print(f"Repository structure OK; {len(adrs)} ADRs")
