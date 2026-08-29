# ADR-004: Separate Terraform Platform IaC from Databricks Application Bundles

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Platform resources and data applications have different ownership, release cadence and blast radius.

## Decision

- **Terraform** owns long-lived infrastructure and platform configuration.
- **Databricks Declarative Automation Bundles** own application jobs, pipelines and deployment targets.

Application deployment must not recreate foundational workspace/network/governance resources.

## Consequences

The split clarifies responsibility and permits independent application releases. Interfaces between platform outputs and application configuration must be explicitly managed.
