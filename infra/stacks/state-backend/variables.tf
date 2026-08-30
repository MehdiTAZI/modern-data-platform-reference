variable "subscription_id" {
  type = string
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "name_prefix" {
  type    = string
  default = "mdpr"
}

variable "state_retention_days" {
  description = "Soft-delete retention for Terraform state blobs and containers."
  type        = number
  default     = 30

  validation {
    condition     = var.state_retention_days >= 7 && var.state_retention_days <= 365
    error_message = "state_retention_days must be between 7 and 365 days."
  }
}

variable "deployment_principal_object_id" {
  type     = string
  default  = null
  nullable = true
}
