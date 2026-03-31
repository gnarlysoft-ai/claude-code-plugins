---
name: azure
description: Azure cloud infrastructure administration via Azure Resource Manager API. Use when the user wants to manage Azure subscriptions, resource groups, VMs, storage, networking, App Service, Key Vault, deployments, or any other Azure resource. Supports multiple tenants.
allowed-tools: Bash, Read
user-invocable: true
argument-hint: "<action> [--profile NAME] (e.g., 'list my subscriptions', 'create a VM in East US', 'list resource groups')"
---

# Azure Cloud Infrastructure Administration

<context>
This skill provides full access to Azure cloud resources via the Azure Resource Manager (ARM) REST API. It supports any ARM endpoint — not just a fixed set of operations. When Azure adds new resource providers, you can use them immediately.

Base URL: `https://management.azure.com`

Every ARM API call requires an `api-version` query parameter specifying the API version to use.

Authentication uses OAuth 2.0 client credentials flow with multi-tenant profile support (same profiles as m365). Each profile represents one Azure AD tenant.
</context>

<instructions>

## Setup Detection

On first use, check if profiles are configured and have Azure access:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py list-profiles
```

Then test Azure connectivity:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py test PROFILE_NAME --scope azure
```

- **No profiles found** → Read `${CLAUDE_PLUGIN_ROOT}/skills/m365/references/setup-tenant.md` to create the app registration first, then read `${CLAUDE_PLUGIN_ROOT}/skills/azure/references/setup-azure.md` to assign Azure RBAC roles.
- **Profiles exist but Azure test fails (403)** → The app registration exists but lacks Azure RBAC roles. Read `references/setup-azure.md` to guide the user through role assignment.
- **Profiles exist and Azure test passes** → Proceed normally.

## Authentication

Acquire a bearer token using the helper script with the `azure` scope:

```bash
TOKEN=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token PROFILE_NAME --scope azure)
```

Replace `PROFILE_NAME` with the profile to use. If there's only one profile, use it automatically. If multiple exist and the user hasn't specified, ask which one.

## Making Requests

Every ARM request **must** include `?api-version=YYYY-MM-DD` as a query parameter. There is no default — omitting it causes a 400 error.

### GET (read data)
```bash
curl -s 'https://management.azure.com/{scope}/providers/{resourceProvider}/{resourceType}?api-version=YYYY-MM-DD' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### PUT (create or update)
```bash
curl -s -X PUT 'https://management.azure.com/{resourceId}?api-version=YYYY-MM-DD' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "eastus", "properties": {}}' | python3 -m json.tool
```

### PATCH (partial update)
```bash
curl -s -X PATCH 'https://management.azure.com/{resourceId}?api-version=YYYY-MM-DD' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tags": {"env": "prod"}}' | python3 -m json.tool
```

### DELETE
```bash
curl -s -X DELETE 'https://management.azure.com/{resourceId}?api-version=YYYY-MM-DD' \
  -H "Authorization: Bearer $TOKEN"
```

### POST (actions)
```bash
curl -s -X POST 'https://management.azure.com/{resourceId}/{action}?api-version=YYYY-MM-DD' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

## Reference Routing

Read the appropriate reference file based on what the user needs:

| User wants to... | Read this reference |
|-------------------|-------------------|
| Set up Azure RBAC roles for the app registration | `references/setup-azure.md` |
| Manage subscriptions, resource groups, tags, deployments, providers | `references/resource-management.md` |
| Work with VMs, App Service, Functions, containers | `references/compute.md` |
| Manage storage accounts, virtual networks, NSGs, load balancers | `references/storage-networking.md` |
| Work with Key Vault secrets, keys, or certificates | `references/key-vault.md` |

Read the reference file using:
```
Read ${CLAUDE_PLUGIN_ROOT}/skills/azure/references/<filename>
```

For operations that span categories (e.g., "deploy a VM with a new VNet and NSG"), read multiple reference files.

## Constructing Unknown Endpoints

ARM follows a consistent URL pattern for all resource types:

### URL Pattern
```
https://management.azure.com/{scope}/providers/{resourceProvider}/{resourceType}/{resourceName}?api-version=YYYY-MM-DD
```

### Scope Levels
- **Tenant**: `/` (rare)
- **Subscription**: `/subscriptions/{subscriptionId}`
- **Resource group**: `/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}`
- **Resource**: full resource ID path

### Common Resource Providers
| Provider | Resources |
|----------|-----------|
| `Microsoft.Compute` | VMs, disks, images, availability sets |
| `Microsoft.Network` | VNets, NSGs, public IPs, load balancers |
| `Microsoft.Storage` | Storage accounts |
| `Microsoft.Web` | App Service, Functions |
| `Microsoft.KeyVault` | Key vaults |
| `Microsoft.ContainerInstance` | Container groups |
| `Microsoft.Resources` | Deployments, tags |

### HTTP Method Conventions
- **GET** = Read (list or get by ID)
- **PUT** = Create or fully replace a resource
- **PATCH** = Partial update
- **DELETE** = Remove resource
- **POST** = Trigger an action (start, stop, restart, listKeys, etc.)

### Discovering API Versions
If unsure of the api-version for a resource provider:
```bash
curl -s 'https://management.azure.com/subscriptions/{subId}/providers/{resourceProvider}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```
The response includes `resourceTypes[].apiVersions[]` listing all valid versions.

## Behavior Guidelines

1. **Always include api-version** — every ARM call requires `?api-version=YYYY-MM-DD`. Never omit it.
2. **Confirm destructive operations** — before DELETE on resource groups, VMs, storage accounts, or vaults, show what will be deleted and ask for confirmation.
3. **Format results** — present list results in markdown tables. For single-resource responses, use key-value format.
4. **Profile context** — always tell the user which profile/tenant you're operating against, especially when multiple profiles exist.
5. **Error guidance** — if a 403 occurs, explain that the app likely needs an Azure RBAC role assignment (separate from Graph API permissions). If a 400 occurs, check the api-version.
6. **Never print secrets** — mask client secrets, storage keys, and token values in output to the user.
7. **Long-running operations** — PUT and DELETE on some resources return 202 Accepted. Check the `Location` or `Azure-AsyncOperation` header for status polling.
8. **Resource group location** — when creating resources, always confirm the Azure region with the user.

</instructions>

<examples>

### List subscriptions
```
/azure list my subscriptions
```

### List resource groups
```
/azure list resource groups in my subscription --profile gnarlysoft
```

### Create a VM
```
/azure create an Ubuntu VM in East US with Standard_B2s size
```

### Manage Key Vault secrets
```
/azure list all secrets in my key-vault named prod-secrets
```

### Deploy an ARM template
```
/azure deploy an ARM template to create a storage account in resource group my-rg
```

</examples>
