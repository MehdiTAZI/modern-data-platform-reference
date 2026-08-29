#!/usr/bin/env bash
set -euo pipefail

: "${AZURE_SUBSCRIPTION_ID:?AZURE_SUBSCRIPTION_ID is required}"
: "${AZURE_PRINCIPAL_OBJECT_ID:?AZURE_PRINCIPAL_OBJECT_ID is required}"
: "${STATE_PREFIX:?STATE_PREFIX is required}"
: "${LOCATION:=westeurope}"

if [[ ! "$STATE_PREFIX" =~ ^[a-z0-9]{3,17}$ ]]; then
  echo "STATE_PREFIX must contain 3-17 lowercase alphanumeric characters" >&2
  exit 2
fi

resource_group="${STATE_PREFIX}-tfstate-rg"
storage_account="${STATE_PREFIX}tfstate"
container="tfstate"

az account set --subscription "$AZURE_SUBSCRIPTION_ID"
az group create --name "$resource_group" --location "$LOCATION" --output none

if ! az storage account show --name "$storage_account" --resource-group "$resource_group" >/dev/null 2>&1; then
  az storage account create \
    --name "$storage_account" \
    --resource-group "$resource_group" \
    --location "$LOCATION" \
    --sku Standard_ZRS \
    --kind StorageV2 \
    --min-tls-version TLS1_2 \
    --allow-shared-key-access false \
    --output none
fi

scope=$(az storage account show \
  --name "$storage_account" \
  --resource-group "$resource_group" \
  --query id -o tsv)

assignment_count=$(az role assignment list \
  --assignee "$AZURE_PRINCIPAL_OBJECT_ID" \
  --scope "$scope" \
  --role "Storage Blob Data Contributor" \
  --query 'length(@)' -o tsv)

if [[ "$assignment_count" == "0" ]]; then
  az role assignment create \
    --assignee-object-id "$AZURE_PRINCIPAL_OBJECT_ID" \
    --assignee-principal-type ServicePrincipal \
    --role "Storage Blob Data Contributor" \
    --scope "$scope" \
    --output none
fi

for attempt in {1..12}; do
  if az storage container create \
    --name "$container" \
    --account-name "$storage_account" \
    --auth-mode login \
    --output none 2>/dev/null; then
    break
  fi
  if [[ "$attempt" == "12" ]]; then
    echo "Timed out waiting for state-storage RBAC propagation" >&2
    exit 1
  fi
  sleep 10
done

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "resource_group_name=$resource_group"
    echo "storage_account_name=$storage_account"
    echo "container_name=$container"
  } >> "$GITHUB_OUTPUT"
fi

echo "Remote state backend ready: $resource_group/$storage_account/$container"
