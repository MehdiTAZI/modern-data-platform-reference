variable "name" {
  type = string

  validation {
    condition     = can(regex("^[0-9A-Za-z_-]{3,30}$", var.name))
    error_message = "NCC name must be 3-30 characters using letters, numbers, hyphens, or underscores."
  }
}

variable "region" {
  type = string
}

variable "workspace_id" {
  type = string
}

variable "private_endpoint_rules" {
  description = "Azure resources that Databricks serverless compute reaches through NCC-managed Private Endpoints."
  type = map(object({
    resource_id = string
    group_id    = string
  }))
  default = {}
}
