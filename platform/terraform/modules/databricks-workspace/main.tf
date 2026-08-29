resource "azurerm_databricks_workspace" "this" {
  name                = var.workspace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku

  public_network_access_enabled = true # Reference default; harden with private connectivity in production.
}
