terraform {
  required_version = "~> 1.15.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.2"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}
