mock_provider "databricks" {}

mock_provider "databricks" {
  alias = "account"
}

variables {
  workspace_host       = "https://adb-0000000000000000.0.azuredatabricks.net"
  environment          = "dev"
  storage_account_name = "mdprdevlake001"
  access_connector_id  = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mdpr/providers/Microsoft.Databricks/accessConnectors/mdpr-dev-dbc"
}

run "serverless_ncc_disabled_by_default" {
  command = plan

  assert {
    condition     = output.serverless_ncc_id == null
    error_message = "serverless NCC must remain opt-in"
  }
}

run "serverless_ncc_requires_account_context" {
  command = plan

  variables {
    enable_serverless_ncc = true
  }

  expect_failures = [check.serverless_ncc_inputs]
}

run "serverless_ncc_can_be_enabled" {
  command = plan

  variables {
    enable_serverless_ncc             = true
    databricks_account_id             = "00000000-0000-0000-0000-000000000000"
    workspace_id                      = "1234567890123456"
    serverless_private_endpoint_rules = {
      lake_blob = {
        resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mdpr/providers/Microsoft.Storage/storageAccounts/mdprdevlake001"
        group_id    = "blob"
      }
      lake_dfs = {
        resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mdpr/providers/Microsoft.Storage/storageAccounts/mdprdevlake001"
        group_id    = "dfs"
      }
    }
  }

  assert {
    condition     = output.serverless_ncc_id != null
    error_message = "enabled serverless NCC must expose its configuration ID"
  }
}
