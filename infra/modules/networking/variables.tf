variable "name_prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "address_space" {
  type    = list(string)
  default = ["10.40.0.0/20"]
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}

variable "enable_private_endpoint_subnet" {
  type    = bool
  default = false
}

variable "private_endpoint_subnet_prefixes" {
  type    = list(string)
  default = ["10.40.12.0/27"]
}

variable "tags" {
  type    = map(string)
  default = {}
}
