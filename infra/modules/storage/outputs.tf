output "id" {
  value = azurerm_storage_account.this.id
}

output "name" {
  value = azurerm_storage_account.this.name
}

output "dfs_endpoint" {
  value = azurerm_storage_account.this.primary_dfs_endpoint
}

output "filesystem" {
  value = azurerm_storage_data_lake_gen2_filesystem.lake.name
}
