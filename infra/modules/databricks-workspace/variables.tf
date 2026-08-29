variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "vnet_id" {
  type = string
}

variable "host_subnet_name" {
  type = string
}

variable "container_subnet_name" {
  type = string
}

variable "host_nsg_association_id" {
  type = string
}

variable "container_nsg_association_id" {
  type = string
}

variable "public_network_access_enabled" {
  type    = bool
  default = true
}

variable "network_security_group_rules_required" {
  type    = string
  default = "AllRules"

  validation {
    condition = contains(
      ["AllRules", "NoAzureDatabricksRules", "NoAzureServiceRules"],
      var.network_security_group_rules_required,
    )
    error_message = "network_security_group_rules_required has an unsupported value"
  }
}

variable "tags" {
  type    = map(string)
  default = {}
}
