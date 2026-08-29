resource "azurerm_databricks_workspace" "this" {
  name = var.name; resource_group_name = var.resource_group_name; location = var.location; sku = "premium"; tags = var.tags
  public_network_access_enabled = true
  custom_parameters {
    virtual_network_id = var.vnet_id
    public_subnet_name = var.host_subnet_name
    private_subnet_name = var.container_subnet_name
    public_subnet_network_security_group_association_id = var.host_nsg_association_id
    private_subnet_network_security_group_association_id = var.container_nsg_association_id
    no_public_ip = true
  }
}
