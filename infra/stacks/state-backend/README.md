# Terraform state backend

This stack describes the Azure resources used to hold Terraform remote state: a dedicated resource group, Storage account, `tfstate` container and optional Blob Data Contributor assignment for the deployment identity.

## Why the V1.1 GitHub workflow uses a bootstrap script

A stateless CI runner cannot safely use a Terraform backend that does not exist yet. The V1.1 workflow therefore bootstraps these few resources idempotently with `scripts/bootstrap_azure_state.sh`, then all platform and governance changes use normal Terraform with persistent Azure Blob state.

The script and this stack represent the **same architectural boundary**, but they are alternative bootstrap mechanisms. Do not apply this stack against resources already created by the script unless you first import the existing resources into Terraform state.

For the automated reference path, follow [`docs/deployment/cloud-evidence.md`](../../../docs/deployment/cloud-evidence.md).

## State keys

The evidence workflow deliberately separates state ownership:

```text
azure-foundation/dev.tfstate
workspace-governance/dev.tfstate
```

The state account disables shared-key authentication. GitHub Actions accesses Blob state with Microsoft Entra ID and OIDC.
