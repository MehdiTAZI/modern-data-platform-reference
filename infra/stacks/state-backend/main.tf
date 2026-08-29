resource "azurerm_resource_group" "state" { name = "${var.name_prefix}-tfstate-rg"; location = var.location }
resource "azurerm_storage_account" "state" { name = "${var.name_prefix}tfstate"; resource_group_name = azurerm_resource_group.state.name; location = var.location; account_tier = "Standard"; account_replication_type = "ZRS"; min_tls_version = "TLS1_2"; shared_access_key_enabled = false }
resource "azurerm_storage_container" "state" { name = "tfstate"; storage_account_id = azurerm_storage_account.state.id }
