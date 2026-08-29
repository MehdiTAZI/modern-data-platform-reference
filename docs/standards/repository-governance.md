# Repository governance

The repository is designed for pull-request-based changes with CI as the merge gate. GitHub repository settings are intentionally outside Terraform because they govern this source repository rather than the data platform itself.

## Recommended `main` ruleset

Configure a GitHub ruleset or branch protection rule for `main` with these controls:

- require a pull request before merging;
- require the CI jobs for Python, Terraform and secret scanning to pass;
- require conversations to be resolved before merge;
- block force pushes and branch deletion;
- prefer squash merges so iterative validation commits do not pollute the public history;
- restrict bypass to repository administrators for recovery only;
- optionally require signed commits when all contributors can support the policy.

Do not enable a status-check name until it has run at least once on the repository; GitHub only allows existing checks to be selected reliably.

## Deployment environment

Use the GitHub `dev` environment as the trust boundary for V1.1 cloud evidence. Store Azure/Databricks identifiers as environment secrets and bind both Azure and Databricks federated identities to the environment subject rather than to every branch in the repository.

See [V1.1 cloud deployment evidence](../deployment/cloud-evidence.md) for the required identities and lifecycle.

## Public-repository metadata

Keep the repository description, topics, license and README aligned with the implemented scope. Recommended topics include:

```text
databricks lakehouse azure terraform unity-catalog pyspark kafka
streaming data-engineering data-platform architecture medallion lakeflow
```

Repository settings are not evidence of platform deployment; they are source-governance controls and should be reviewed separately from the V1.1 cloud evidence artifact.
