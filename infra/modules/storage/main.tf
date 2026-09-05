resource "azurerm_storage_account" "this" {
  name                          = var.name
  resource_group_name           = var.resource_group_name
  location                      = var.location
  account_tier                  = "Standard"
  account_replication_type      = var.account_replication_type
  is_hns_enabled                = true
  min_tls_version               = "TLS1_2"
  shared_access_key_enabled     = false
  public_network_access_enabled = true

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = var.allowed_subnet_ids
  }

  blob_properties {
    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = var.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "lake" {
  name               = "lake"
  storage_account_id = azurerm_storage_account.this.id
}
