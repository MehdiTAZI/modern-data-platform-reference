variable "name_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "workspace_id" {
  type = string
}

variable "vnet_id" {
  type = string
}

variable "private_endpoint_subnet_id" {
  type = string
}

variable "enable_browser_authentication_endpoint" {
  description = "Create the region-scoped browser_authentication endpoint required for private browser SSO."
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
