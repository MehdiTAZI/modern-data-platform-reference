resource "azurerm_resource_group" "state" {
  name     = "${var.name_prefix}-tfstate-rg"
  location = var.location
}

resource "azurerm_storage_account" "state" {
  name                              = "${var.name_prefix}tfstate"
  resource_group_name               = azurerm_resource_group.state.name
  location                          = var.location
  account_tier                      = "Standard"
  account_replication_type          = "ZRS"
  min_tls_version                   = "TLS1_2"
  shared_access_key_enabled         = false
  allow_nested_items_to_be_public   = false
  cross_tenant_replication_enabled  = false
  infrastructure_encryption_enabled = true

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = var.state_retention_days
    }

    container_delete_retention_policy {
      days = var.state_retention_days
    }
  }
}

resource "azurerm_role_assignment" "state_blob_contributor" {
  count                = var.deployment_principal_object_id == null ? 0 : 1
  scope                = azurerm_storage_account.state.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.deployment_principal_object_id
}

resource "azurerm_storage_container" "state" {
  name                  = "tfstate"
  storage_account_id    = azurerm_storage_account.state.id
  container_access_type = "private"
}
