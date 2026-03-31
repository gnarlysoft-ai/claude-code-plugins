# Key Vault

Azure Key Vault management (vaults) and data plane operations (secrets, keys, certificates).

Key Vault uses **two separate APIs**:
- **Management plane** — create, delete, and configure vaults via ARM (`https://management.azure.com`)
- **Data plane** — read/write secrets, keys, and certificates via the vault's own endpoint (`https://{vault-name}.vault.azure.net`)

## Contents

- [Authentication](#authentication)
- [Management Plane: Vaults](#management-plane-vaults)
  - [Create a Key Vault](#create-a-key-vault)
  - [List Key Vaults](#list-key-vaults)
  - [Get a Key Vault](#get-a-key-vault)
  - [Delete a Key Vault](#delete-a-key-vault)
- [Data Plane: Secrets](#data-plane-secrets)
  - [List Secrets](#list-secrets)
  - [Get a Secret](#get-a-secret)
  - [Set a Secret](#set-a-secret)
  - [Delete a Secret](#delete-a-secret)
- [Data Plane: Keys](#data-plane-keys)
  - [List Keys](#list-keys)
  - [Create a Key](#create-a-key)
  - [Get a Key](#get-a-key)
- [Data Plane: Certificates](#data-plane-certificates)
  - [List Certificates](#list-certificates)
  - [Create a Certificate](#create-a-certificate)
  - [Get a Certificate](#get-a-certificate)
  - [Import a Certificate](#import-a-certificate)
- [Access Policies vs RBAC](#access-policies-vs-rbac)

## Authentication

Management and data plane use **different token scopes**:

| Plane | Base URL | Token Scope | auth.py Flag |
|-------|----------|-------------|-------------|
| Management | `https://management.azure.com` | `https://management.azure.com/.default` | `--scope azure` |
| Data | `https://{vault}.vault.azure.net` | `https://vault.azure.net/.default` | `--scope keyvault` |

```bash
# Management plane token (create/delete vaults)
MGMT_TOKEN=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token PROFILE --scope azure)

# Data plane token (secrets/keys/certs)
KV_TOKEN=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token PROFILE --scope keyvault)
```

## Management Plane: Vaults

Provider: `Microsoft.KeyVault/vaults`
api-version: `2023-07-01`

Base path:
```
/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults
```

### Create a Key Vault

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vaultName}?api-version=2023-07-01' \
  -H "Authorization: Bearer $MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "properties": {
      "tenantId": "{tenantId}",
      "sku": { "family": "A", "name": "standard" },
      "enableRbacAuthorization": true
    }
  }' | python3 -m json.tool
```

Setting `enableRbacAuthorization: true` uses Azure RBAC instead of vault access policies (recommended).

Vault names must be globally unique, 3-24 chars, alphanumeric and hyphens.

### List Key Vaults

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults?api-version=2023-07-01' \
  -H "Authorization: Bearer $MGMT_TOKEN" | python3 -m json.tool
```

### Get a Key Vault

```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vaultName}?api-version=2023-07-01' \
  -H "Authorization: Bearer $MGMT_TOKEN" | python3 -m json.tool
```

### Delete a Key Vault

```bash
curl -s -X DELETE 'https://management.azure.com/subscriptions/{subId}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vaultName}?api-version=2023-07-01' \
  -H "Authorization: Bearer $MGMT_TOKEN"
```

Deleted vaults enter a soft-delete state (recoverable for 90 days by default). To purge:
```bash
curl -s -X POST 'https://management.azure.com/subscriptions/{subId}/providers/Microsoft.KeyVault/locations/{location}/deletedVaults/{vaultName}/purge?api-version=2023-07-01' \
  -H "Authorization: Bearer $MGMT_TOKEN"
```

## Data Plane: Secrets

Base URL: `https://{vault-name}.vault.azure.net`
api-version: `7.4`

### List Secrets

```bash
curl -s 'https://{vault-name}.vault.azure.net/secrets?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

Returns secret metadata only (name, attributes, content type) — not secret values.

### Get a Secret

```bash
curl -s 'https://{vault-name}.vault.azure.net/secrets/{secret-name}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

Get a specific version:
```bash
curl -s 'https://{vault-name}.vault.azure.net/secrets/{secret-name}/{version}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

Never display the `value` field to the user — mask it in output.

### Set a Secret

```bash
curl -s -X PUT 'https://{vault-name}.vault.azure.net/secrets/{secret-name}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "my-secret-value",
    "attributes": { "enabled": true },
    "contentType": "text/plain",
    "tags": { "environment": "production" }
  }' | python3 -m json.tool
```

Setting a secret with an existing name creates a new version automatically.

### Delete a Secret

```bash
curl -s -X DELETE 'https://{vault-name}.vault.azure.net/secrets/{secret-name}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

Soft-deleted. Recover with:
```bash
curl -s -X POST 'https://{vault-name}.vault.azure.net/deletedsecrets/{secret-name}/recover?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

## Data Plane: Keys

Base URL: `https://{vault-name}.vault.azure.net`
api-version: `7.4`

### List Keys

```bash
curl -s 'https://{vault-name}.vault.azure.net/keys?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

### Create a Key

```bash
curl -s -X POST 'https://{vault-name}.vault.azure.net/keys/{key-name}/create?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "kty": "RSA",
    "key_size": 2048,
    "key_ops": ["encrypt", "decrypt", "sign", "verify", "wrapKey", "unwrapKey"]
  }' | python3 -m json.tool
```

Key types: `RSA`, `RSA-HSM`, `EC`, `EC-HSM`, `oct` (symmetric).

### Get a Key

```bash
curl -s 'https://{vault-name}.vault.azure.net/keys/{key-name}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

## Data Plane: Certificates

Base URL: `https://{vault-name}.vault.azure.net`
api-version: `7.4`

### List Certificates

```bash
curl -s 'https://{vault-name}.vault.azure.net/certificates?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

### Create a Certificate

```bash
curl -s -X POST 'https://{vault-name}.vault.azure.net/certificates/{cert-name}/create?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {
      "key_props": { "exportable": true, "kty": "RSA", "key_size": 2048, "reuse_key": false },
      "secret_props": { "contentType": "application/x-pkcs12" },
      "x509_props": {
        "subject": "CN=example.com",
        "sans": { "dns_names": ["example.com", "*.example.com"] },
        "validity_months": 12
      },
      "issuer": { "name": "Self" }
    }
  }' | python3 -m json.tool
```

Issuer `Self` creates a self-signed cert. For CA-signed certs, configure an issuer first.

### Get a Certificate

```bash
curl -s 'https://{vault-name}.vault.azure.net/certificates/{cert-name}?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" | python3 -m json.tool
```

### Import a Certificate

```bash
curl -s -X POST 'https://{vault-name}.vault.azure.net/certificates/{cert-name}/import?api-version=7.4' \
  -H "Authorization: Bearer $KV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "<base64-encoded-pfx>",
    "pwd": "<pfx-password-if-any>",
    "policy": {
      "key_props": { "exportable": true },
      "secret_props": { "contentType": "application/x-pkcs12" }
    }
  }' | python3 -m json.tool
```

## Access Policies vs RBAC

Key Vault supports two authorization models:

### RBAC (Recommended)
Set `enableRbacAuthorization: true` on the vault. Assign Azure RBAC roles:

| Role | Access |
|------|--------|
| Key Vault Administrator | Full access to all data plane operations |
| Key Vault Secrets Officer | Manage secrets |
| Key Vault Secrets User | Read secrets only |
| Key Vault Crypto Officer | Manage keys |
| Key Vault Certificates Officer | Manage certificates |
| Key Vault Reader | Read vault metadata only |

### Access Policies (Legacy)
Set `enableRbacAuthorization: false` and define access policies in vault properties:

```json
{
  "accessPolicies": [
    {
      "tenantId": "{tenantId}",
      "objectId": "{servicePrincipalObjectId}",
      "permissions": {
        "secrets": ["get", "list", "set", "delete"],
        "keys": ["get", "list", "create", "delete"],
        "certificates": ["get", "list", "create", "delete", "import"]
      }
    }
  ]
}
```

RBAC is preferred because it provides fine-grained access control, audit logging, and consistency with other Azure resources.
