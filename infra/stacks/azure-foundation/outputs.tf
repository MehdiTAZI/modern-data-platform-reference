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
