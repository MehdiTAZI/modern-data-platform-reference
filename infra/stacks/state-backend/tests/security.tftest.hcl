mock_provider "azurerm" {}

variables {
  subscription_id = "00000000-0000-0000-0000-000000000000"
}

run "secure_state_defaults" {
  command = plan

  assert {
    condition     = azurerm_storage_account.state.shared_access_key_enabled == false
    error_message = "Terraform state must use identity-based access rather than shared keys"
  }

  assert {
    condition     = azurerm_storage_account.state.allow_nested_items_to_be_public == false
    error_message = "Terraform state storage must prohibit public nested items"
  }

  assert {
    condition     = azurerm_storage_account.state.cross_tenant_replication_enabled == false
    error_message = "Terraform state storage must disable cross-tenant replication"
  }

  assert {
    condition     = azurerm_storage_account.state.infrastructure_encryption_enabled == true
    error_message = "Terraform state storage must enable infrastructure encryption"
  }

  assert {
    condition     = azurerm_storage_account.state.blob_properties[0].versioning_enabled == true
    error_message = "Terraform state blobs must be versioned"
  }

  assert {
    condition     = azurerm_storage_container.state.container_access_type == "private"
    error_message = "Terraform state container must remain private"
  }
}

run "reject_short_retention" {
  command = plan

  variables {
    state_retention_days = 3
  }

  expect_failures = [var.state_retention_days]
}
