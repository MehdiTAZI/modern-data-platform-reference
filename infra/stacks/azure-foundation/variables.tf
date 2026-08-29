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
