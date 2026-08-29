resource "databricks_storage_credential" "azure" {
  name = "${var.catalog_name}_storage"

  azure_managed_identity {
    access_connector_id = var.access_connector_id
  }

  comment = "Managed identity storage credential for ${var.catalog_name}"
}

resource "databricks_credential" "event_hubs" {
  name    = "${var.catalog_name}_event_hubs"
  purpose = "SERVICE"

  azure_managed_identity {
    access_connector_id = var.access_connector_id
  }

  comment = "Managed identity service credential for Azure Event Hubs"
}

resource "databricks_external_location" "root" {
  name            = "${var.catalog_name}_root"
  url             = "abfss://${var.filesystem}@${var.storage_account_name}.dfs.core.windows.net/${var.catalog_name}"
  credential_name = databricks_storage_credential.azure.id
  comment         = "Governed storage root for ${var.catalog_name}"
}

resource "databricks_catalog" "this" {
  name         = var.catalog_name
  storage_root = "${databricks_external_location.root.url}/managed"
  comment      = "Retail reference catalog"
}

resource "databricks_schema" "layer" {
  for_each     = toset(["bronze", "silver", "gold", "ops"])
  catalog_name = databricks_catalog.this.name
  name         = each.key
}

resource "databricks_volume" "landing" {
  name             = "landing"
  catalog_name     = databricks_catalog.this.name
  schema_name      = databricks_schema.layer["bronze"].name
  volume_type      = "EXTERNAL"
  storage_location = "${databricks_external_location.root.url}/landing"
  comment          = "Externally-owned replayable landing area"
}

resource "databricks_grants" "catalog" {
  catalog = databricks_catalog.this.name

  grant {
    principal  = var.platform_admin_group
    privileges = ["ALL_PRIVILEGES"]
  }

  grant {
    principal  = var.engineer_group
    privileges = ["USE_CATALOG"]
  }

  grant {
    principal  = var.analyst_group
    privileges = ["USE_CATALOG"]
  }
}

resource "databricks_grants" "event_hubs" {
  credential = databricks_credential.event_hubs.id

  grant {
    principal  = var.platform_admin_group
    privileges = ["ALL_PRIVILEGES"]
  }

  grant {
    principal  = var.engineer_group
    privileges = ["ACCESS"]
  }
}

resource "databricks_grants" "silver" {
  schema = "${databricks_catalog.this.name}.silver"

  grant {
    principal  = var.engineer_group
    privileges = ["USE_SCHEMA", "CREATE_TABLE", "SELECT", "MODIFY"]
  }
}

resource "databricks_grants" "gold" {
  schema = "${databricks_catalog.this.name}.gold"

  grant {
    principal  = var.engineer_group
    privileges = ["USE_SCHEMA", "CREATE_TABLE", "SELECT", "MODIFY"]
  }

  grant {
    principal  = var.analyst_group
    privileges = ["USE_SCHEMA", "SELECT"]
  }
}
