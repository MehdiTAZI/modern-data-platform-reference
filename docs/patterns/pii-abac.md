# Pattern: Governed-tag PII masking with Unity Catalog ABAC

The reference uses a governed tag named `pii` with controlled classification values such as `email` and `name`. Classification labels contain no personal data themselves.

`governance/sql/pii_abac.sql` demonstrates the DEV policy lifecycle:

1. account governance creates the governed-tag taxonomy once;
2. the customer email column is tagged `pii=email`;
3. a Unity Catalog SQL UDF defines the masking transformation;
4. a schema-level ABAC `COLUMN MASK` policy matches columns with that governed tag;
5. platform admins and retail data engineers are exempt, while ordinary account users see masked values.

ABAC queries require serverless or a supported Databricks Runtime. Creating governed tags through SQL currently requires Databricks Runtime 18.1+ and account-level governed-tag CREATE permission. Tag assignment and policy management require their corresponding Unity Catalog privileges.

In production, use enterprise-owned principal names, tag taxonomy, approval workflows and privacy rules. The example is deliberately scoped to the DEV retail catalog and is not legal/compliance advice.

See ADR-021 and the Unity Catalog ABAC documentation.
