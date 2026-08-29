# Software supply-chain standard

## GitHub Actions
External actions must use immutable full commit SHAs. Keep the upstream semantic version in an inline comment for readability and Dependabot review. Local actions (`./...`) are exempt because their implementation is versioned in this repository.

Run `python scripts/validate_actions_pinned.py` locally and in CI. Do not weaken the policy to permit mutable `@main`, `@master`, or major-version tags.

## Python dependencies
Runtime dependencies remain semver-ranged because this is a reference/library-style project, while CI resolves and audits the actual environment. `pip-audit` is a vulnerability signal, not a substitute for code review or threat modeling. Temporary vulnerability ignores require a documented rationale, advisory identifier, owner and removal condition.

## Releases
A `vX.Y.Z` tag must match `project.version` in `pyproject.toml`. The release workflow builds a wheel and sdist, produces `SHA256SUMS`, emits a CycloneDX JSON SBOM, creates GitHub artifact attestations, uploads the evidence artifact, and publishes the same files to the GitHub Release.

Consumers can verify GitHub artifact attestations with the GitHub CLI. Attestation confirms origin/build context; it does not certify runtime security.

## Terraform
Provider constraints remain in every executable root and Dependabot monitors each root independently. Provider-aware `terraform init -backend=false` + `validate` remains mandatory in CI.
