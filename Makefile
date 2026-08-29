.PHONY: install lint test test-unit test-spark build data contracts docs repo-check policy audit sbom terraform-fmt terraform-validate ci

install:
	python -m pip install -e '.[dev]'

lint:
	ruff format --check .
	ruff check .

test:
	pytest -q --cov=mdpr --cov-report=term-missing

test-unit:
	pytest -q tests/unit

test-spark:
	pytest -q -m spark

build:
	python -m build --wheel

data:
	python scripts/generate_sample_data.py

contracts:
	python scripts/validate_contracts.py

repo-check:
	python scripts/validate_repo.py

policy:
	python scripts/validate_actions_pinned.py

audit:
	pip-audit . --strict --desc=off
	pip-audit --local --skip-editable --desc=off

sbom:
	mkdir -p dist
	pip-audit . --strict --desc=off --format cyclonedx-json --output dist/sbom.cdx.json

terraform-fmt:
	terraform fmt -check -recursive infra

terraform-validate:
	for d in infra/stacks/state-backend infra/stacks/azure-foundation infra/stacks/workspace-governance infra/stacks/azure-dr-secondary; do \
		terraform -chdir=$$d init -backend=false -input=false && terraform -chdir=$$d validate; \
	done

docs: repo-check

ci: policy lint contracts repo-check test build audit terraform-fmt terraform-validate
