#!/usr/bin/env bash
set -euo pipefail

: "${STORAGE_ACCOUNT:?STORAGE_ACCOUNT is required}"
: "${FILESYSTEM:?FILESYSTEM is required}"
: "${CATALOG:?CATALOG is required}"
: "${SOURCE_DIR:?SOURCE_DIR is required}"
: "${RUN_SUFFIX:?RUN_SUFFIX is required}"

source_file="$SOURCE_DIR/recovery/customers-reference-catchup.csv"
target_dir="${CATALOG}/landing/customers"
target_file="customers-reference-catchup-${RUN_SUFFIX}.csv"

az storage fs directory create \
  --account-name "$STORAGE_ACCOUNT" \
  --file-system "$FILESYSTEM" \
  --name "$target_dir" \
  --auth-mode login \
  --output none

az storage fs file upload \
  --account-name "$STORAGE_ACCOUNT" \
  --file-system "$FILESYSTEM" \
  --path "${target_dir}/${target_file}" \
  --source "$source_file" \
  --auth-mode login \
  --overwrite true \
  --output none

echo "Uploaded reference catch-up file to ${target_dir}/${target_file}"
