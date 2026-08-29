resource "azurerm_eventhub_namespace" "this" {
  name                = "${var.name_prefix}-ehns"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
  capacity            = 1
  tags                = var.tags
}

resource "azurerm_eventhub" "orders" {
  name              = "orders"
  namespace_id      = azurerm_eventhub_namespace.this.id
  partition_count   = 4
  message_retention = 7
}

resource "azurerm_role_assignment" "receiver" {
  scope                = azurerm_eventhub_namespace.this.id
  role_definition_name = "Azure Event Hubs Data Receiver"
  principal_id         = var.consumer_principal_id
}
