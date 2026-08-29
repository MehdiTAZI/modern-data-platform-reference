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

output "private_endpoint_id" {
  value = try(module.private_link[0].private_endpoint_id, null)
}
