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

variable "tags" {
  type    = map(string)
  default = {}
}
