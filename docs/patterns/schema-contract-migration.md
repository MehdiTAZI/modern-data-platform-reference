# Pattern: Versioned schema-contract migration

The active customer contract is `contracts/retail/customers.yml` (v1). `customers.v2.yml` is a backward-compatible candidate that adds nullable `loyalty_tier` plus a metric-only expectation.

## Expand → observe → enforce → contract

1. **Expand:** add new nullable fields without removing or changing existing fields or business keys.
2. **Observe:** publish new quality rules as `metric` while producers and consumers adopt the field.
3. **Enforce:** promote a rule to `quarantine` or `fail` only after measured compatibility and owner approval.
4. **Contract:** once all supported consumers have migrated, the candidate becomes the active contract in a normal reviewed change.

`validate_compatible_upgrade()` rejects candidate versions that do not increment the version, change the dataset/business keys, remove fields, change field types, or make a previously nullable field non-nullable. CI automatically checks versioned candidates such as `*.v2.yml` against their active contract.

This is intentionally conservative. Breaking changes require a new dataset/versioned consumer surface or an explicitly coordinated migration rather than silently redefining Silver.

See ADR-016.
