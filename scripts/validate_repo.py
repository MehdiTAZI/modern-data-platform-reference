from pathlib import Path

REQUIRED = [
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "databricks.yml",
    "pyproject.toml",
    "docs/adr/README.md",
    "docs/adr/ADR-025-classic-private-link-variant.md",
    "docs/adr/ADR-029-quality-telemetry-and-reprocessing.md",
    "docs/adr/ADR-030-temporal-dimensional-consistency.md",
    "docs/patterns/application-pipeline.md",
    "docs/patterns/schema-contract-migration.md",
    "docs/patterns/late-event-reconciliation.md",
    "docs/patterns/private-link.md",
    "docs/patterns/pii-abac.md",
    "docs/patterns/managed-dr.md",
    "pipelines/retail/history.py",
    "pipelines/retail/reconciliation.py",
    "pipelines/retail/quality_telemetry.py",
    "resources/ops.pipeline.yml",
    "observability/sql/data_quality.sql",
    "observability/sql/reconciliation.sql",
    "tests/spark/test_quality_and_reprocessing.py",
    "governance/sql/pii_abac.sql",
    "infra/modules/databricks-private-link/main.tf",
    "infra/stacks/azure-foundation/main.tf",
    "infra/stacks/azure-dr-secondary/main.tf",
]

if __name__ == "__main__":
    missing = [path for path in REQUIRED if not Path(path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    adrs = list(Path("docs/adr").glob("ADR-*.md"))
    if len(adrs) < 30:
        raise SystemExit("Expected at least 30 ADRs")

    print(f"Repository structure OK; {len(adrs)} ADRs")
