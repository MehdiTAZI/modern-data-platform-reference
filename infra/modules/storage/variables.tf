variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "account_replication_type" {
  type    = string
  default = "ZRS"

  validation {
    condition = contains(
      ["LRS", "ZRS", "GRS", "RAGRS", "GZRS", "RAGZRS"],
      var.account_replication_type,
    )
    error_message = "account_replication_type must be a supported Azure Storage redundancy type"
  }
}

variable "tags" {
  type    = map(string)
  default = {}
}
