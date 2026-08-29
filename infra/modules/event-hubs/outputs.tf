output "kafka_bootstrap_servers" { value = "${azurerm_eventhub_namespace.this.name}.servicebus.windows.net:9093" }
output "topic" { value = azurerm_eventhub.orders.name }
