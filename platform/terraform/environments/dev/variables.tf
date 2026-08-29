variable "subscription_id" { type = string }
variable "location" {
  type    = string
  default = "westeurope"
}
variable "name_prefix" {
  type    = string
  default = "mdpr-dev"
}
variable "storage_account_name" {
  type        = string
  description = "Globally unique Azure storage account name"
}
