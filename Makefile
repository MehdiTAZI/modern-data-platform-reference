.PHONY: test lint format terraform-fmt

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .
	terraform fmt -recursive platform/terraform

terraform-fmt:
	terraform fmt -check -recursive platform/terraform
