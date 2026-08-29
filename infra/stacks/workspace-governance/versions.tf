terraform { required_version = "~> 1.15.0"
 required_providers { databricks = { source = "databricks/databricks" version = "~> 1.128.0" } } }
provider "databricks" { host = var.workspace_host }
