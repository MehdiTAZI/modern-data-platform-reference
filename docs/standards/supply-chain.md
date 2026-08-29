# Software supply-chain standard

## GitHub Actions
External actions must use immutable full commit SHAs. Keep the upstream semantic version in an inline comment for readability and Dependabot review. Local actions (`./...`) are exempt because their implementation is versioned in this repository.

Run `python scripts/validate_actions_pinned.py` locally and in CI. Do not weaken the policy to permit mutable `@main`, `@master`, or major-version tags.

## Python dependencies
Runtime dependencies remain semver-ranged because this is a reference/library-style project. CI uses two complementary audits:

1. `pip-audit . --strict --desc=off` resolves and strictly audits the project dependency graph.
2. `pip-audit --local --skip-editable --desc=off` audits the resolved installed environment while excluding the intentionally editable local project distribution.

Both commands fail when known vulnerabilities are found. The second command is intentionally not collection-strict because an editable repository distribution is not itself a vulnerability. `pip-audit` remains a vulnerability signal, not a substitute for code review or threat modeling. Temporary vulnerability ignores require a documented rationale, advisory identifier, owner and removal condition.

## Releases
A `vX.Y.Z` tag must match `project.version` in `pyproject.toml`. The release workflow builds a wheel and sdist, produces `SHA256SUMS`, emits a CycloneDX JSON SBOM, creates GitHub artifact attestations, uploads the evidence artifact, and publishes the same files to the GitHub Release.

Consumers can verify GitHub artifact attestations with the GitHub CLI. Attestation confirms origin/build context; it does not certify runtime security.

## Terraform
Every executable Terraform root must declare provider constraints **and** commit its `.terraform.lock.hcl`. Terraform working directories (`.terraform/`), plans and state remain generated/secret-bearing artifacts and stay ignored.

Provider locks are generated from origin registries with:

```bash
terraform -chdir=<root> init -backend=false -input=false
terraform -chdir=<root> providers lock \
  -platform=linux_amd64 \
  -platform=darwin_amd64 \
  -platform=darwin_arm64
```

Normal validation uses `terraform init -backend=false -input=false -lockfile=readonly` followed by `terraform validate`. If the configuration can no longer initialize using the committed selection, CI fails rather than silently selecting or recording a different provider.

Provider upgrades are explicit review events. Dependabot may propose compatible constraint/provider changes, but the affected lockfile must be regenerated and its provider version/checksum diff reviewed in the same change. See ADR-027.
