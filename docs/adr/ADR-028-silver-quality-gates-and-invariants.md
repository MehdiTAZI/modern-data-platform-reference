# ADR-028: Silver quality gates and trusted invariants

- **Status:** Accepted
- **Date:** 2026-08-29

## Context
The application must demonstrate a complete Medallion workflow without confusing bad source records with application failures. Bronze must remain replayable, malformed events must not disappear inside stateful streaming operations, Silver must expose why records were rejected, and Gold should never silently repair data that has already been declared trusted.

Using fail expectations for ordinary row-level defects would stop an entire flow because of expected source-quality problems. Conversely, relying only on warn/drop behavior after conformance would allow transformation regressions to pass silently.

## Decision
Use three distinct quality behaviors aligned to the Medallion boundary.

1. **Bronze observes and preserves.** Bronze retains source payloads, transport metadata and rescued fields. Expectations are warn/metric controls only; Bronze does not apply business cleansing, deduplication or destructive filtering.
2. **Silver quarantines row-level defects.** Customer/product/order contract rules classify invalid rows, preserve `_dq_errors` in quarantine datasets and exclude those rows from validated/trusted outputs.
3. **Orders have a pre-stateful gate.** JSON parseability and required event-envelope fields are validated before watermarking and deduplication. This prevents malformed/null-event-time records from being hidden by stateful processing.
4. **Orders have a conformance gate.** After event-time deduplication and reference enrichment, quantity, price, business-time and customer/product integrity rules determine validated versus quarantine output.
5. **Fail expectations protect trusted surfaces.** `expect_or_fail` / `expect_all_or_fail` are used only after the quality gate on conditions that should be impossible if the transformation and contracts are functioning correctly.
6. **Gold consumes trusted Silver.** Gold models dimensions, facts and business aggregates and fails on broken downstream invariants rather than performing source-data repair.
7. **Python assertions belong in tests.** Reusable transformation functions are exercised with pytest/Spark tests independently from Lakeflow decorators.

## Alternatives considered
- Fail the pipeline for every invalid source row. Rejected because ordinary source-quality defects should not create avoidable platform incidents.
- Drop invalid rows without quarantine. Rejected because it creates silent data loss and weakens operability/replay.
- Apply all order quality checks after watermarking/deduplication. Rejected because malformed or null-event-time records can interact poorly with stateful streaming and become harder to account for.
- Put cleansing logic in Bronze. Rejected because it weakens source fidelity and replayability.
- Let Gold re-clean Silver data. Rejected because it obscures ownership of the trust boundary and creates inconsistent consumer semantics.

## Consequences
The application graph contains more intermediate datasets, but each has a clear operational purpose: observed raw input, validated input, quarantine, trusted conformed state and consumer products. Quarantine volumes and reasons become measurable, replay remains possible from Bronze, and fail expectations become strong regression signals instead of source-data alarms.

Static/Spark CI validates transformation and contract behavior. Lakeflow-specific expectation metrics, streaming state behavior and AUTO CDC execution still require runtime validation in a Databricks environment.

## Reconsider when
Reconsider the split if source SLAs require fail-closed ingestion, a source contract guarantees zero invalid rows, Lakeflow runtime semantics materially change, or a different streaming/state model provides equivalent replay and quarantine guarantees with less complexity.
