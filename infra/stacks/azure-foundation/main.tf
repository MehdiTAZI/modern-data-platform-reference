locals {
  profile = {
    managed = {
      enable_private_link                    = false
      enable_browser_authentication_endpoint = false
      public_network_access_enabled          = true
      enable_nat_gateway                     = true
      nsg_rules_required                     = "AllRules"
    }
    enterprise = {
      enable_private_link                    = true
      enable_browser_authentication_endpoint = false
      public_network_access_enabled          = true
      enable_nat_gateway                     = false
      nsg_rules_required                     = "NoAzureDatabricksRules"
    }
    isolated = {
      enable_private_link                    = true
      enable_browser_authentication_endpoint = true
      public_network_access_enabled          = false
      enable_nat_gateway                     = false
      nsg_rules_required                     = "NoAzureDatabricksRules"
    }
  }[var.deployment_profile]
}

resource "azurerm_resource_group" "this" {
  name     = "${var.name_prefix}-rg"
  location = var.location
  tags     = merge(var.tags, { deployment_profile = var.deployment_profile })
}

module "networking" {
  source                           = "../../modules/networking"
  name_prefix                      = var.name_prefix
  location                         = var.location
  resource_group_name              = azurerm_resource_group.this.name
  enable_nat_gateway               = local.profile.enable_nat_gateway
  enable_private_endpoint_subnet   = local.profile.enable_private_link
  private_endpoint_subnet_prefixes = var.private_endpoint_subnet_prefixes
  tags                             = var.tags
}

module "storage" {
  source                   = "../../modules/storage"
  name                     = var.storage_account_name
  location                 = var.location
  resource_group_name      = azurerm_resource_group.this.name
  account_replication_type = var.storage_replication_type
  tags                     = var.tags
}

resource "azurerm_role_assignment" "evidence_data_contributor" {
  count                = var.deployment_principal_object_id == null ? 0 : 1
  scope                = module.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.deployment_principal_object_id
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
  source                                = "../../modules/databricks-workspace"
  name                                  = "${var.name_prefix}-dbw"
  location                              = var.location
  resource_group_name                   = azurerm_resource_group.this.name
  vnet_id                               = module.networking.vnet_id
  host_subnet_name                      = module.networking.host_subnet_name
  container_subnet_name                 = module.networking.container_subnet_name
  host_nsg_association_id               = module.networking.host_nsg_association_id
  container_nsg_association_id          = module.networking.container_nsg_association_id
  public_network_access_enabled         = local.profile.public_network_access_enabled
  network_security_group_rules_required = local.profile.nsg_rules_required
  tags                                  = var.tags
}

module "private_link" {
  count = local.profile.enable_private_link ? 1 : 0

  source                                 = "../../modules/databricks-private-link"
  name_prefix                            = var.name_prefix
  location                               = var.location
  resource_group_name                    = azurerm_resource_group.this.name
  workspace_id                           = module.workspace.id
  vnet_id                                = module.networking.vnet_id
  private_endpoint_subnet_id             = module.networking.private_endpoint_subnet_id
  enable_browser_authentication_endpoint = local.profile.enable_browser_authentication_endpoint
  tags                                   = var.tags
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
