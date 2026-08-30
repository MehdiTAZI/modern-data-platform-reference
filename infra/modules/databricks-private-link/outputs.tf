output "private_endpoint_id" {
  value = azurerm_private_endpoint.workspace.id
}

output "browser_authentication_private_endpoint_id" {
  value = try(azurerm_private_endpoint.browser_authentication[0].id, null)
}

output "private_dns_zone_id" {
  value = azurerm_private_dns_zone.databricks.id
}
