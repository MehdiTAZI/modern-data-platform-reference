# Data Engineering Standard

This standard defines the default engineering rules for application pipelines in this reference. Exceptions require an explicit design decision when they materially change correctness, recoverability, security or cost.

## 1. Keep business logic reusable

- Put deterministic transformation logic under `src/`, not only inside notebooks or pipeline decorators.
- Pipeline files should primarily declare sources, dependencies, quality behavior and materialization semantics.
- Prefer DataFrame-to-DataFrame functions that can be exercised with local Spark tests.
- Avoid hidden global state and side effects inside transformation functions.

## 2. Give each medallion layer one primary responsibility

### Bronze

- preserve source fidelity;
- retain replay/transport metadata;
- record schema drift rather than silently discarding it;
- do not repair business values;
- use observation expectations rather than destructive business filtering.

### Silver

- standardize types/representations;
- enforce explicit contracts;
- classify invalid records;
- make quarantine reason-preserving;
- define deduplication/event-time/reference semantics;
- publish trusted outputs only after quality gates.

### Gold

- model for consumption;
- derive facts, dimensions and aggregates from trusted/canonical data;
- fail on impossible post-trust invariants;
- do not compensate for upstream defects silently.

### Ops

- expose operational quality/reliability/cost signals in stable schemas;
- minimize payload replication;
- preserve enough identifiers/fingerprints for diagnosis under governance controls.

## 3. Make ingestion replayable and attributable

Where the source allows it, retain:

- ingestion timestamp/date;
- logical source system;
- source file or stream transport coordinates;
- immutable raw payload/envelope for event sources;
- deterministic payload fingerprint;
- rescued/unparsed data required for forensic recovery.

Do not call a pipeline idempotent merely because the storage engine is transactional. Define the event/business key and duplicate semantics explicitly.

## 4. Treat contracts as code

Contracts must be version-controlled and independently reviewable from transformation code.

Each rule should have:

- stable identifier;
- severity/disposition;
- category;
- executable expression;
- operational message.

Only `TRUE` satisfies a quality constraint. `FALSE` and `NULL` are violations unless a rule explicitly models nullable behavior.

Schema/contract changes must follow compatibility checks and documented migration semantics.

## 5. Separate observation, quarantine and failure

Use the weakest control that still protects the relevant trust boundary:

- **metric/observe** for signals that should not alter data availability;
- **quarantine** for source/business rows that must not enter trusted output;
- **fail** for invariants that should be impossible after a trust gate.

Never use fail-fast as a substitute for a source-data quarantine strategy, and never silently drop invalid records without a retained disposition when recovery/audit matters.

## 6. Make recovery paths explicit

Different failure modes require different recovery mechanisms:

- replay from Bronze for delivery/state-horizon loss;
- reference reprocessing for eventually-consistent dimensions;
- contract migration for intentional semantic evolution;
- code fix + replay for trusted transformation regressions.

Reprocessing must re-evaluate the complete current contract. Fixing the original failed rule is not sufficient proof that a row is now valid.

Original quarantine/rejection evidence remains immutable.

## 7. Bound streaming state deliberately

For stateful streaming operations define:

- event-time column;
- watermark/state horizon;
- duplicate key;
- late-data disposition;
- recovery/reconciliation path;
- expected throughput/backlog behavior.

Watermarks are availability/cost correctness decisions, not arbitrary tuning values.

## 8. Make temporal semantics explicit

For mutable dimensions distinguish:

- current-state validation semantics;
- SCD1 replacement semantics;
- SCD2 historical semantics;
- as-of joins where a fact must resolve the dimension version valid at event time.

Use half-open validity intervals `[start, end)` unless another convention is explicitly documented.

Do not silently join historical facts to today's dimension state when business meaning depends on historical context.

## 9. Test more than individual rows

The minimum test pyramid should include, as applicable:

1. pure/unit logic;
2. local Spark transformations;
3. contract/schema compatibility;
4. failure scenarios (null, corrupt, duplicate, late, unknown reference);
5. remediation/replay behavior;
6. temporal/SCD behavior;
7. dataset-level reconciliation;
8. runtime Lakeflow evidence in a real environment;
9. performance/state/skew tests for production-scale claims.

A row passing all rules does not prove that a transformation preserved the dataset.

## 10. Reconcile trusted boundaries

For critical facts, define accounting controls such as:

```text
source rows = accepted + quarantined + duplicate disposition
```

and, where economically meaningful:

```text
source additive metric ~= target additive metric
```

Tolerance must be explicit. Non-zero row or unexplained business-metric deltas at a trusted boundary are application/reconciliation incidents, not ordinary source DQ events.

## 11. Keep outputs deterministic

When multiple records compete for the same business/event key, specify deterministic ordering/tie-breaking.

Prefer stable source sequence/version fields. When those are unavailable, ingestion metadata and payload fingerprints may be used as documented tie-breakers; they must not be presented as source business ordering.

## 12. Design observability with the pipeline

Operational telemetry should cover:

- run/update state and duration;
- data quality by stage/rule;
- quarantine/recovery volume;
- freshness;
- streaming backlog/state where relevant;
- trusted reconciliation;
- cost attribution.

Observability is part of the application contract, not an afterthought added after production incidents.

## 13. Minimize sensitive-data duplication

Do not copy raw payloads or PII into operational tables merely for convenience. Prefer governed keys, fingerprints and aggregate metrics where sufficient.

Temporal Gold facts in this reference retain the resolved customer-version interval rather than copying customer PII into the fact.

## 14. Separate platform and application lifecycle

Terraform owns durable cloud/platform/governance boundaries. Databricks Bundles own application pipelines/jobs and their release lifecycle.

Application code must not opportunistically create enterprise IAM/storage/network policy as an implicit side effect of deployment.

## 15. Require evidence for production claims

Source code, static validation and unit tests prove implementation intent, not runtime behavior.

Production claims require environment evidence for the relevant mechanism: Lakeflow expectations, AUTO CDC, streaming state, Private Link, identity policy, scale/performance and failure/recovery behavior.
