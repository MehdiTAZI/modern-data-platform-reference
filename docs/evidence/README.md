# Deployment evidence

This directory contains **curated** evidence from successful V1.1 cloud runs. Raw output is first produced as a sanitized GitHub Actions artifact by `.github/workflows/deploy.yml`.

A curated evidence folder must contain, at minimum:

- the Git commit SHA;
- the GitHub Actions run ID or link;
- Azure region;
- dataset profile and row/event count;
- Terraform foundation/governance result summary;
- Databricks Bundle deployment/run result;
- Silver and Gold object inventory;
- measured end-to-end duration when a workload was executed;
- explicit caveats about the disposable environment and dataset profile.

Never commit Terraform state, plan binaries, access tokens, secrets, tenant/subscription IDs or application/client IDs.

Until a real credentialed run has succeeded, this directory intentionally contains no fabricated screenshots or performance numbers.
