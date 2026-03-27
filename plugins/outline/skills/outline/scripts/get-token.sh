#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: .env file not found at $ENV_FILE" >&2
    echo "Please create it with OUTLINE_BASE_URL and OUTLINE_API_TOKEN" >&2
    exit 1
fi

VAR_NAME="${1}"

VALUE=$(grep -E "^${VAR_NAME}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")

if [[ -z "$VALUE" ]]; then
    echo "Error: ${VAR_NAME} not found or empty in .env" >&2
    exit 1
fi

echo "$VALUE"
