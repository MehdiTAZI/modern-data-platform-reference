output "vnet_id" {
  value = azurerm_virtual_network.this.id
}

output "vnet_name" {
  value = azurerm_virtual_network.this.name
}

output "host_subnet_name" {
  value = azurerm_subnet.host.name
}

output "container_subnet_name" {
  value = azurerm_subnet.container.name
}

output "host_nsg_association_id" {
  value = azurerm_subnet_network_security_group_association.host.id
}

output "container_nsg_association_id" {
  value = azurerm_subnet_network_security_group_association.container.id
}
