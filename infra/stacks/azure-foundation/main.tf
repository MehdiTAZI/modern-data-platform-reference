resource "azurerm_resource_group" "this" {
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = var.tags
}

module "networking" {
  source              = "../../modules/networking"
  name_prefix         = var.name_prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

module "storage" {
  source              = "../../modules/storage"
  name                = var.storage_account_name
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}

module "connector" {
  source              = "../../modules/access-connector"
  name                = "${var.name_prefix}-dbc"
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  storage_account_id  = module.storage.id
  tags                = var.tags
}

module "workspace" {
  source                       = "../../modules/databricks-workspace"
  name                         = "${var.name_prefix}-dbw"
  location                     = var.location
  resource_group_name          = azurerm_resource_group.this.name
  vnet_id                      = module.networking.vnet_id
  host_subnet_name             = module.networking.host_subnet_name
  container_subnet_name        = module.networking.container_subnet_name
  host_nsg_association_id      = module.networking.host_nsg_association_id
  container_nsg_association_id = module.networking.container_nsg_association_id
  tags                         = var.tags
}

module "event_hubs" {
  source                = "../../modules/event-hubs"
  name_prefix           = var.name_prefix
  location              = var.location
  resource_group_name   = azurerm_resource_group.this.name
  consumer_principal_id = module.connector.principal_id
  tags                  = var.tags
}

module "logs" {
  source              = "../../modules/log-analytics"
  name                = "${var.name_prefix}-law"
  location            = var.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = var.tags
}
