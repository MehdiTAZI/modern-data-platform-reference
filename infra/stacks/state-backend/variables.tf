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

variable "deployment_principal_object_id" {
  type     = string
  default  = null
  nullable = true
}
