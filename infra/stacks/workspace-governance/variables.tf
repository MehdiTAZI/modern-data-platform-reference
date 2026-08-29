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
