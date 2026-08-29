# Terraform Platform Layer

Terraform owns foundational resources with a lifecycle independent from data applications.

The first reference implementation targets Azure + Databricks and is intentionally decomposed into modules so other cloud implementations can be added without changing the application structure.

## Target responsibilities

- networking and private connectivity;
- cloud storage;
- Databricks workspace;
- Unity Catalog metastore bindings / storage credentials / external locations;
- platform identities and groups;
- compute policies and baseline permissions;
- monitoring destinations and diagnostic settings.

The environment folders compose reusable modules and provide deployment-specific values.
