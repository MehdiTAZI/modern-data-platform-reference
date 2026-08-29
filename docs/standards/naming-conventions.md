# Naming Conventions

The examples use a simple convention that makes environment, domain and purpose visible.

## Unity Catalog

```text
Catalog: <environment>_<layer>
Schema:  <domain>
Table:   <business_entity_or_product>
```

Examples:

```text
prd_bronze.retail.orders_raw
prd_silver.retail.orders
prd_gold.retail.daily_sales
```

## Workload identities

```text
dbx-<environment>-<domain>-<purpose>-sp
```

## Terraform

Resource names should be generated from explicit variables for environment, region, domain/project and component. Avoid meaningful production identifiers hard-coded inside reusable modules.
