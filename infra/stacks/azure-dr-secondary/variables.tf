variable "subscription_id" {
  type = string
}

variable "location" {
  type    = string
  default = "northeurope"
}

variable "name_prefix" {
  type    = string
  default = "mdpr-dr"
}

variable "storage_account_name" {
  type = string
}

variable "storage_replication_type" {
  type    = string
  default = "GZRS"
}

variable "enable_private_link" {
  type    = bool
  default = false
}

variable "address_space" {
  type    = list(string)
  default = ["10.50.0.0/20"]
}

variable "private_endpoint_subnet_prefixes" {
  type    = list(string)
  default = ["10.50.12.0/27"]
}

variable "tags" {
  type = map(string)
  default = {
    managed_by = "terraform"
    project    = "mdpr"
    role       = "dr-secondary"
  }
}
