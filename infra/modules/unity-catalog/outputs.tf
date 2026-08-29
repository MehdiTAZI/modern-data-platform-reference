output "catalog_name" {
  value = databricks_catalog.this.name
}

output "landing_volume" {
  value = databricks_volume.landing.name
}

output "event_hubs_service_credential" {
  value = databricks_credential.event_hubs.name
}
