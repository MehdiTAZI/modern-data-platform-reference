check "serverless_ncc_inputs" {
  assert {
    condition = !var.enable_serverless_ncc || (
      var.databricks_account_id != null && var.databricks_account_id != "" &&
      var.workspace_id != null && var.workspace_id != ""
    )
    error_message = "databricks_account_id and workspace_id are required when enable_serverless_ncc is true."
  }
}

module "uc" {
  source               = "../../modules/unity-catalog"
  catalog_name         = "retail_${var.environment}"
  storage_account_name = var.storage_account_name
  filesystem           = var.filesystem
  access_connector_id  = var.access_connector_id
  platform_admin_group = var.platform_admin_group
  engineer_group       = var.engineer_group
  analyst_group        = var.analyst_group
}

module "serverless_ncc" {
  count = var.enable_serverless_ncc ? 1 : 0

  source = "../../modules/serverless-ncc"
  providers = {
    databricks = databricks.account
  }

  name                   = "mdpr-${var.environment}-ncc"
  region                 = var.azure_region
  workspace_id           = var.workspace_id
  private_endpoint_rules = var.serverless_private_endpoint_rules
}
