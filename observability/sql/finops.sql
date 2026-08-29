SELECT usage_metadata.job_id, sku_name, sum(usage_quantity) AS dbus FROM system.billing.usage WHERE usage_date >= current_date() - 30 GROUP BY ALL ORDER BY dbus DESC;
