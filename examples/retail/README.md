# Retail / E-commerce Reference Scenario

The repository evolves around one coherent domain rather than disconnected examples.

## Sources

| Dataset | Mode | Purpose |
|---|---|---|
| Customers | Batch | Customer master snapshot/increment |
| Products | Batch | Product catalogue |
| Orders | Streaming / CDC | Transaction events |
| Clickstream | Streaming | Behavioral events |
| Inventory | Incremental | Stock position |

## Target products

- `silver.retail.customers`
- `silver.retail.orders`
- `gold.retail.daily_sales`
- future: `gold.retail.customer_360`
- future: `gold.retail.realtime_sales_kpi`

## Engineering scenarios to demonstrate next

1. schema drift and quarantine;
2. event-time watermarking;
3. duplicate order events;
4. late-arriving data;
5. CDC merge and SCD Type 2;
6. replay from Bronze;
7. skewed joins and performance optimisation;
8. data-quality SLIs and reconciliation;
9. lineage and access-control examples;
10. cost attribution and compute-policy enforcement.
