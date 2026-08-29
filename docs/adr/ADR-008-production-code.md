# ADR-008: Prefer Modular Source Code over Notebook-Centric Production Applications

- **Status:** Accepted
- **Date:** 2026-08-29

## Decision

Production transformations should live primarily in reusable Python/SQL modules with tests. Notebooks remain appropriate for exploration, demonstrations and operational investigation.

## Consequences

Code review, packaging and testing improve. Engineers must maintain a clean distinction between exploratory assets and deployable application code.
