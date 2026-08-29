from pathlib import Path
REQUIRED = ["README.md","LICENSE","SECURITY.md","CONTRIBUTING.md","databricks.yml","pyproject.toml","docs/adr/README.md","infra/stacks/azure-foundation/main.tf"]
if __name__ == "__main__":
    missing=[p for p in REQUIRED if not Path(p).exists()]
    if missing: raise SystemExit(f"Missing required files: {missing}")
    adrs=list(Path("docs/adr").glob("ADR-*.md"))
    if len(adrs) < 20: raise SystemExit("Expected at least 20 ADRs")
    print(f"Repository structure OK; {len(adrs)} ADRs")
