output "workspace_url" {
  value = module.workspace.workspace_url
}

output "workspace_host" {
  value = "https://${module.workspace.workspace_url}"
}

output "workspace_id" {
  value = module.workspace.workspace_id
}

output "storage_account_name" {
  value = module.storage.name
}

output "filesystem" {
  value = module.storage.filesystem
}

output "access_connector_id" {
  value = module.connector.id
}

output "kafka_bootstrap_servers" {
  value = module.event_hubs.kafka_bootstrap_servers
}

output "kafka_topic" {
  value = module.event_hubs.topic
}

output "deployment_profile" {
  value = var.deployment_profile
}

output "profile_controls" {
  value = {
    enable_private_link                    = local.profile.enable_private_link
    enable_browser_authentication_endpoint = local.profile.enable_browser_authentication_endpoint
    public_network_access_enabled          = local.profile.public_network_access_enabled
    enable_nat_gateway                     = local.profile.enable_nat_gateway
    nsg_rules_required                     = local.profile.nsg_rules_required
  }
}

output "private_endpoint_id" {
  value = try(module.private_link[0].private_endpoint_id, null)
}

output "browser_authentication_private_endpoint_id" {
  value = try(module.private_link[0].browser_authentication_private_endpoint_id, null)
}

output "private_dns_zone_id" {
  value = try(module.private_link[0].private_dns_zone_id, null)
}
