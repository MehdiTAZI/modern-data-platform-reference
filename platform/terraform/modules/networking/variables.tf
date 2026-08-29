variable "resource_group_name" { type = string }
variable "location" { type = string }
variable "name_prefix" { type = string }
variable "address_space" {
  type    = list(string)
  default = ["10.20.0.0/16"]
}
