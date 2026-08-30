resource "azurerm_private_dns_zone" "databricks" {
  name                = "privatelink.azuredatabricks.net"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "databricks" {
  name                 = "${var.name_prefix}-databricks"
  private_dns_zone_id  = azurerm_private_dns_zone.databricks.id
  virtual_network_id   = var.vnet_id
  registration_enabled = false
  tags                 = var.tags
}

resource "azurerm_private_endpoint" "workspace" {
  name                = "${var.name_prefix}-dbw-backend-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id
  tags                = var.tags

  private_service_connection {
    name                           = "${var.name_prefix}-dbw-backend"
    private_connection_resource_id = var.workspace_id
    subresource_names              = ["databricks_ui_api"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "databricks"
    private_dns_zone_ids = [azurerm_private_dns_zone.databricks.id]
  }
}

resource "azurerm_private_endpoint" "browser_authentication" {
  count = var.enable_browser_authentication_endpoint ? 1 : 0

  name                = "${var.name_prefix}-dbw-browser-auth-pe"
  location            = var.location
  resource_group_name = var.resource_group_name
  subnet_id           = var.private_endpoint_subnet_id
  tags                = var.tags

  private_service_connection {
    name                           = "${var.name_prefix}-dbw-browser-auth"
    private_connection_resource_id = var.workspace_id
    subresource_names              = ["browser_authentication"]
    is_manual_connection           = false
  }

  private_dns_zone_group {
    name                 = "databricks"
    private_dns_zone_ids = [azurerm_private_dns_zone.databricks.id]
  }
}
