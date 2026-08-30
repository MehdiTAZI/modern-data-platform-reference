variable "subscription_id" {
  type = string
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "name_prefix" {
  type    = string
  default = "mdpr-dev"
}

variable "storage_account_name" {
  type = string
}

variable "storage_replication_type" {
  type    = string
  default = "ZRS"
}

variable "deployment_profile" {
  description = "Platform connectivity profile: managed, enterprise, or isolated."
  type        = string
  default     = "managed"

  validation {
    condition     = contains(["managed", "enterprise", "isolated"], var.deployment_profile)
    error_message = "deployment_profile must be one of: managed, enterprise, isolated."
  }
}

variable "private_endpoint_subnet_prefixes" {
  type    = list(string)
  default = ["10.40.12.0/27"]
}

variable "deployment_principal_object_id" {
  type     = string
  default  = null
  nullable = true
}

variable "tags" {
  type = map(string)
  default = {
    managed_by = "terraform"
    project    = "mdpr"
  }
}
