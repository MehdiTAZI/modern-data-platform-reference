output "network_connectivity_config_id" {
  value = databricks_mws_network_connectivity_config.this.network_connectivity_config_id
}

output "private_endpoint_rule_ids" {
  value = {
    for name, rule in databricks_mws_ncc_private_endpoint_rule.this : name => rule.rule_id
  }
}
