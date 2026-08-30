variable "workspace_host" {
  type = string
}

variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "stg", "prd"], var.environment)
    error_message = "environment must be dev, stg or prd"
  }
}

variable "storage_account_name" {
  type = string
}

variable "filesystem" {
  type    = string
  default = "lake"
}

variable "access_connector_id" {
  type = string
}

variable "platform_admin_group" {
  type    = string
  default = "data-platform-admins"
}

variable "engineer_group" {
  type    = string
  default = "retail-data-engineers"
}

variable "analyst_group" {
  type    = string
  default = "retail-data-analysts"
}

variable "enable_serverless_ncc" {
  description = "Create and bind an account-level Network Connectivity Configuration for serverless compute."
  type        = bool
  default     = false
}

variable "databricks_account_id" {
  description = "Databricks account ID used by account-level networking resources."
  type        = string
  default     = null
  nullable    = true
}

variable "workspace_id" {
  description = "Numeric Databricks workspace ID used for NCC binding."
  type        = string
  default     = null
  nullable    = true
}

variable "azure_region" {
  description = "Azure region used by the Databricks NCC. Must match the workspace region."
  type        = string
  default     = "westeurope"
}

variable "serverless_private_endpoint_rules" {
  description = "Azure Private Endpoint targets used by Databricks serverless compute."
  type = map(object({
    resource_id = string
    group_id    = string
  }))
  default = {}
}
