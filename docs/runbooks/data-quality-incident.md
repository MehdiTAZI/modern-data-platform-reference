# Runbook: Data Quality Incident

Use this runbook when a quality rule spikes, a trusted invariant fails, or a reconciliation control reports missing/duplicated rows or metric drift.

## 1. Classify the incident before changing anything

Determine which boundary failed:

| Boundary | Typical signal | Default response |
|---|---|---|
| Bronze observation | rescued fields, missing raw identifiers | inspect source/schema drift; preserve raw data |
| Silver shape gate | parse/missing-envelope quarantine | source/schema investigation |
| Silver business gate | business/reference quarantine | source fix, reference catch-up or approved contract change |
| Silver reprocessing | row remains invalid after retry | inspect remaining rules; do not force promotion |
| Gold trusted invariant | fail expectation | application/contract regression investigation |
| Gold reconciliation | row/amount delta | stop downstream trust claim and trace transformation loss/duplication |

A source-data defect and a trusted-code regression have different blast radius and remediation paths.

## 2. Quantify impact

Use `observability/sql/data_quality.sql` to identify:

- affected dataset and stage;
- contract version;
- rule/category;
- failed-record count;
- first/last observation time;
- impacted business keys/fingerprints where access policy permits.

For trusted-boundary incidents, use `observability/sql/reconciliation.sql` and record:

- source/target row counts;
- row delta;
- source/target additive metric;
- metric delta and configured tolerance.

## 3. Establish the source and contract timeline

Capture:

- source schema/version or producer release if known;
- first affected ingestion timestamp;
- active contract version;
- relevant deployment commit/release;
- whether the incident began after a code, contract, source or reference-data change.

Do not weaken a rule simply to restore green status.

## 4. Choose the remediation path

### Source defect

Fix the producer or source data, retain the original Bronze/quarantine evidence, then replay/reprocess only the affected scope where possible.

### Reference data arrived late

Use the reference-reprocessing path. It re-evaluates the **complete current contract** against current trusted references. The original quarantine row remains immutable.

A row is recovered only when `_dq_errors` becomes empty.

### Event arrived beyond streaming state horizon

Use Bronze late-event reconciliation. Events already owned by the business-quarantine path are excluded so recovery mechanisms do not compete for the same disposition.

### Contract genuinely changed

Create a versioned contract migration, run compatibility checks and document the decision. Do not silently edit semantics without review/evidence.

### Trusted transformation regression

Fix code/configuration, rerun tests, replay the affected trusted boundary and require reconciliation to return to zero delta before declaring recovery.

## 5. Validate recovery

Recovery is complete only when all relevant checks pass:

1. expected records are present in the trusted/canonical output;
2. invalid records remain quarantined with explicit reasons;
3. recovered reference-late records pass the complete current contract;
4. canonical deduplication has not duplicated recovered events;
5. Silver-to-Gold row reconciliation is balanced;
6. additive metric reconciliation is within tolerance;
7. temporal facts resolve a valid SCD2 interval where required;
8. DQ summary returns to the accepted operating range.

## 6. Preserve evidence

Record:

- incident start/end;
- affected datasets/rules;
- source and contract versions;
- root cause;
- remediation action;
- replay/reprocessing scope;
- before/after reconciliation values;
- deployment/run identifiers available from Lakeflow/system tables;
- follow-up preventive action.

Never delete the original Bronze or quarantine evidence merely because the canonical output has been repaired.

## 7. Escalation examples

Escalate to the platform/application owner when:

- a trusted fail expectation fires;
- reconciliation delta is non-zero;
- quarantine exceeds the agreed SLO threshold;
- the same rule repeatedly recurs after remediation;
- a contract change would weaken a business/security invariant;
- replay scope risks breaching retention, cost or SLA limits.

See [ADR-028](../adr/ADR-028-silver-quality-gates-and-invariants.md), [ADR-029](../adr/ADR-029-quality-telemetry-and-reprocessing.md) and [ADR-030](../adr/ADR-030-temporal-dimensional-consistency.md).
