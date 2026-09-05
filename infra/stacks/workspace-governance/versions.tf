terraform {
  required_version = "~> 1.15.0"

  backend "azurerm" {}

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.130.0"
    }
  }
}

provider "databricks" {
  host = var.workspace_host
}

provider "databricks" {
  alias      = "account"
  host       = "https://accounts.azuredatabricks.net"
  account_id = var.databricks_account_id
}
