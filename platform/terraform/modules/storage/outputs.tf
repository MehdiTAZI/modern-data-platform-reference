output "storage_account_id" { value = azurerm_storage_account.lake.id }
output "storage_account_name" { value = azurerm_storage_account.lake.name }
output "filesystem_name" { value = azurerm_storage_data_lake_gen2_filesystem.data.name }
