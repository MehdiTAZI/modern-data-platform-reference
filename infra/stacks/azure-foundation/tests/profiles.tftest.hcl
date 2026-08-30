mock_provider "azurerm" {}

variables {
  subscription_id      = "00000000-0000-0000-0000-000000000000"
  storage_account_name = "mdprtestlake001"
}

run "managed_profile" {
  command = plan

  variables {
    deployment_profile = "managed"
  }

  assert {
    condition     = output.profile_controls.enable_private_link == false
    error_message = "managed profile must not create Private Link"
  }

  assert {
    condition     = output.profile_controls.public_network_access_enabled == true
    error_message = "managed profile must keep public workspace access enabled"
  }

  assert {
    condition     = output.profile_controls.enable_nat_gateway == true
    error_message = "managed profile must provide deterministic NAT egress"
  }
}

run "enterprise_profile" {
  command = plan

  variables {
    deployment_profile = "enterprise"
  }

  assert {
    condition     = output.profile_controls.enable_private_link == true
    error_message = "enterprise profile must enable back-end Private Link"
  }

  assert {
    condition     = output.profile_controls.enable_browser_authentication_endpoint == false
    error_message = "enterprise profile keeps browser/API access public"
  }

  assert {
    condition     = output.profile_controls.public_network_access_enabled == true
    error_message = "enterprise profile must keep public workspace access enabled"
  }

  assert {
    condition     = output.profile_controls.nsg_rules_required == "NoAzureDatabricksRules"
    error_message = "enterprise profile must use private classic-compute connectivity rules"
  }
}

run "isolated_profile" {
  command = plan

  variables {
    deployment_profile = "isolated"
  }

  assert {
    condition     = output.profile_controls.enable_private_link == true
    error_message = "isolated profile must enable Private Link"
  }

  assert {
    condition     = output.profile_controls.enable_browser_authentication_endpoint == true
    error_message = "isolated profile must provide private browser authentication"
  }

  assert {
    condition     = output.profile_controls.public_network_access_enabled == false
    error_message = "isolated profile must disable public workspace access"
  }

  assert {
    condition     = output.profile_controls.enable_nat_gateway == false
    error_message = "isolated profile must not expose NAT egress"
  }
}
