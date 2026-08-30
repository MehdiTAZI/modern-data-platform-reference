output "catalog_name" {
  value = module.uc.catalog_name
}

output "landing_volume" {
  value = module.uc.landing_volume
}

output "serverless_ncc_enabled" {
  value = length(module.serverless_ncc) == 1
}

output "serverless_ncc_id" {
  value = try(module.serverless_ncc[0].network_connectivity_config_id, null)
}

output "serverless_private_endpoint_rule_ids" {
  value = try(module.serverless_ncc[0].private_endpoint_rule_ids, {})
}
