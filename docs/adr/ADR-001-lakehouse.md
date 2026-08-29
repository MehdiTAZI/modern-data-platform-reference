# ADR-001: Adopt a Lakehouse Architecture

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

The platform must support large-scale engineering, SQL analytics, batch and streaming workloads while reducing copies and governance fragmentation between a data lake and separate analytical platforms.

## Decision

Use a lakehouse architecture in which governed open table storage is the system of record for analytical data and is accessed by engineering, analytics and advanced-data workloads.

## Alternatives considered

- Traditional Hadoop-style data lake plus separate warehouse.
- Warehouse-first architecture with external raw storage.
- Multiple purpose-specific analytical stores as primary persistence.

## Consequences

A common governed storage model simplifies lineage and reuse, but platform design must still account for workload isolation, performance, cost and consumer-specific serving needs.
