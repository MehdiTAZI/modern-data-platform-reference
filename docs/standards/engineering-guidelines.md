# Data Engineering Guidelines

- Keep business logic in version-controlled Python/SQL modules rather than notebook-only code.
- Make ingestion idempotent or explicitly replayable.
- Treat schemas and business keys as contracts.
- Prefer deterministic transformations.
- Separate I/O from transformation logic to improve testability.
- Use built-in Spark functions before Python UDFs unless a UDF is justified and measured.
- Design joins with data size, skew and cardinality in mind.
- Avoid indiscriminate `repartition`, `cache` and `collect` calls.
- Persist only when reuse and cost justify it.
- Expose pipeline metrics for freshness, volume, quality and latency.
- Document non-obvious performance decisions in code or ADRs.
