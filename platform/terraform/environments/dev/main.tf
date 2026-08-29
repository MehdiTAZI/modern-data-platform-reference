terraform {
  required_version = ">= 1.8.0"
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "this" {
  name     = "${var.name_prefix}-rg"
  location = var.location
}

module "networking" {
  source              = "../../modules/networking"
  resource_group_name = azurerm_resource_group.this.name
  location            = var.location
  name_prefix         = var.name_prefix
}

module "storage" {
  source               = "../../modules/storage"
  resource_group_name  = azurerm_resource_group.this.name
  location             = var.location
  storage_account_name = var.storage_account_name
}

module "workspace" {
  source              = "../../modules/databricks-workspace"
  resource_group_name = azurerm_resource_group.this.name
  location            = var.location
  workspace_name      = "${var.name_prefix}-dbw"
}
