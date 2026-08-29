# ADR-026: Software supply-chain and release provenance

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The reference implementation is itself software. A production-oriented repository should make third-party workflow execution, dependency vulnerability exposure, package contents and build provenance reviewable rather than relying on mutable action tags or opaque release artifacts.

## Decision
1. Pin every external GitHub Action to a full 40-character commit SHA and retain the human-readable release tag as an inline comment.
2. Let Dependabot propose action and package updates; SHA changes are reviewed through the normal PR/CI path.
3. Audit Python in two complementary scopes: resolve/audit the project dependency graph with `pip-audit . --strict`, then audit the installed CI environment while skipping the intentionally editable repository distribution. Both checks fail on known vulnerabilities; strict collection semantics apply to the project graph where the repository itself is not an editable-environment false positive.
4. On release tags, build wheel and source distribution, generate SHA-256 checksums and a CycloneDX JSON SBOM, and create GitHub/Sigstore artifact attestations for package provenance plus the wheel SBOM.
5. Publish release artifacts only from the dedicated release workflow. The workflow never publishes to PyPI automatically; repository releases remain reference artifacts rather than an implied supported product distribution.
6. Treat attestations and SBOMs as verifiable evidence of origin/composition, not as proof that an artifact is secure.

## Alternatives considered
- Mutable major-version action tags only: simpler, but an upstream tag movement can change executed code without a repository diff.
- Vendoring third-party Actions: stronger control but disproportionate maintenance for this reference repository.
- Auditing an editable CI environment with `--strict`: rejected because `pip-audit` correctly reports the editable local distribution as an uncollectable dependency target, which would turn a packaging characteristic into a false security failure.
- No release artifacts because the project is a reference: rejected because reproducible review of the packaged code is part of demonstrating software-engineering maturity.
- Automatic PyPI publishing: rejected because this repository is not positioned as a supported installable SDK/product.

## Consequences
Action upgrades generate explicit diffs, CI gains a network-dependent vulnerability gate, and tagged builds produce auditable package evidence. Dependency advisories can make previously green commits fail later; that is intentional and should trigger remediation or an explicitly documented temporary exception.

## Reconsider when
The repository becomes an externally supported package, adopts an internal artifact registry, requires offline/hermetic builds, or enterprise policy mandates a different SLSA/SBOM/signing system.
