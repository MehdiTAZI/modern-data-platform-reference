# ADR-034 — IaC policy gates and destructive Terraform plan guard

## Status
Accepted

## Context

Terraform syntax validation is necessary but does not protect the platform from insecure configuration or accidental destructive changes. A reference architecture should demonstrate layered IaC controls that run before cloud deployment while keeping runtime evidence distinct from static validation.

The repository also needs a clear response to storage-network exposure. A static security scan identified storage accounts whose public endpoint had no deny-by-default network rule.

## Decision

The CI pipeline uses complementary controls:

1. `terraform fmt`, locked-provider initialization and `terraform validate` for Terraform correctness.
2. TFLint for Terraform language quality and reusable-module version constraints.
3. Trivy configuration scanning as a blocking gate for HIGH and CRITICAL IaC misconfigurations.
4. Gitleaks and dependency auditing remain independent security gates.
5. `scripts/terraform_plan_guard.py` evaluates `terraform show -json` output and blocks any resource change containing a `delete` action. Terraform replacements are therefore treated as destructive as well.
6. Expected destructive changes require an explicit resource-address allowlist, using repeatable `--allow-address` patterns. There is no global "allow all deletes" switch.

Azure Storage used by the data platform is deny-by-default at the storage firewall and allows the Databricks host/container subnets through `Microsoft.Storage` service endpoints. The Terraform state storage account is also deny-by-default.

## Consequences

- New HIGH/CRITICAL IaC security findings fail CI instead of becoming documentation debt.
- Reusable Terraform modules declare compatible Terraform/provider versions, reducing implicit dependency drift.
- Accidental deletes and force-replacements can be rejected before apply when the guard is run against a real plan JSON.
- Runners that access the Terraform state backend must have an approved network path; deny-by-default state storage intentionally removes unrestricted public-network access.
- Static CI does not prove Azure deployment or connectivity. Real environment pipelines must still generate a Terraform plan, run the destructive-plan guard against that exact plan, obtain any required approval, and apply that reviewed plan artifact.

## Evidence boundary

Unit tests prove the destructive-plan classification and allowlist semantics. Trivy/TFLint prove static repository policy compliance. They do not prove that an Azure plan was generated or that a deployment was applied. Those remain runtime/environment evidence requirements.
