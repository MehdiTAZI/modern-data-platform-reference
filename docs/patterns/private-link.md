# Pattern: Azure Databricks backend Private Link

Set `enable_private_link=true` on the Azure foundation to activate the classic-compute **backend-only** Private Link variant.

The variant creates a dedicated private-endpoint subnet, removes the explicit Databricks NAT Gateway, sets `network_security_group_rules_required = "NoAzureDatabricksRules"`, and creates a `databricks_ui_api` private endpoint integrated with the `privatelink.azuredatabricks.net` private DNS zone.

Public network access intentionally remains enabled. This is consistent with the backend-only profile: workspace users and APIs can still connect publicly while classic compute uses the private control-plane path.

## Not full private isolation

Do not describe this toggle as an end-to-end private workspace. Full inbound/private-user access requires additional Azure Databricks endpoint and DNS design, including `browser_authentication` and possibly `general_access`. Serverless private data access is a separate network-connectivity concern. Enterprise firewalls, routing and private access to storage/sources must also be designed explicitly.

The secondary DR stack exposes the same toggle because Managed DR requires the network security posture of primary and secondary workspaces to remain compatible.

See ADR-025 and current Azure Databricks Private Link documentation.
