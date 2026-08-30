terraform {
  required_version = "~> 1.15.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.3"
    }
  }
}

provider "azurerm" {
  features {
    enhanced_validation {
      locations          = true
      resource_providers = true
    }
  }

  subscription_id = var.subscription_id

  resource_providers_to_register = [
    "Microsoft.Databricks",
    "Microsoft.EventHub",
    "Microsoft.Network",
    "Microsoft.OperationalInsights",
    "Microsoft.Storage",
  ]
}
