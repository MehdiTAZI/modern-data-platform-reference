# Pattern: Contract-driven Data Quality
Versioned YAML contracts classify checks as fail, quarantine or metric. Fail protects structural invariants, quarantine preserves recoverable bad rows, metrics capture non-blocking drift. Transformations consume the same contract definitions used by tests.
