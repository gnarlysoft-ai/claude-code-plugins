#!/bin/bash
set -euo pipefail

VAR_NAME="${1}"

# Check env var first (set via settings.local.json, survives cache rebuilds)
VALUE="${!VAR_NAME:-}"

if [[ -z "$VALUE" ]]; then
    # Fall back to .env file
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    ENV_FILE="$SCRIPT_DIR/../.env"
    if [[ -f "$ENV_FILE" ]]; then
        VALUE=$(grep -E "^${VAR_NAME}=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

if [[ -z "$VALUE" ]]; then
    echo "Error: ${VAR_NAME} not set as env var or found in .env" >&2
    exit 1
fi

echo "$VALUE"
