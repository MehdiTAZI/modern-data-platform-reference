#!/usr/bin/env bash
set -euo pipefail

: "${STORAGE_ACCOUNT:?STORAGE_ACCOUNT is required}"
: "${FILESYSTEM:?FILESYSTEM is required}"
: "${CATALOG:?CATALOG is required}"
: "${SOURCE_DIR:?SOURCE_DIR is required}"
: "${RUN_SUFFIX:?RUN_SUFFIX is required}"

base="${CATALOG}/landing"

upload_file() {
  local source=$1
  local directory=$2
  local filename=$3

  az storage fs directory create \
    --account-name "$STORAGE_ACCOUNT" \
    --file-system "$FILESYSTEM" \
    --name "${base}/${directory}" \
    --auth-mode login \
    --output none

  az storage fs file upload \
    --account-name "$STORAGE_ACCOUNT" \
    --file-system "$FILESYSTEM" \
    --path "${base}/${directory}/${filename}" \
    --source "$source" \
    --auth-mode login \
    --overwrite true \
    --output none
}

for attempt in {1..12}; do
  if az storage fs show \
    --account-name "$STORAGE_ACCOUNT" \
    --name "$FILESYSTEM" \
    --auth-mode login >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" == "12" ]]; then
    echo "Timed out waiting for data-storage RBAC propagation" >&2
    exit 1
  fi
  sleep 10
done

upload_file "$SOURCE_DIR/customers.csv" customers "customers-${RUN_SUFFIX}.csv"
upload_file "$SOURCE_DIR/products.csv" products "products-${RUN_SUFFIX}.csv"
upload_file "$SOURCE_DIR/orders.jsonl" orders "orders-${RUN_SUFFIX}.jsonl"

echo "Uploaded reference data under abfss://${FILESYSTEM}@${STORAGE_ACCOUNT}.dfs.core.windows.net/${base}/"
