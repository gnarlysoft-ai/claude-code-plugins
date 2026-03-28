# Core Resource Management

Subscriptions, resource groups, resources, tags, deployments, and providers via the Azure Resource Manager API.

## Contents

- [Subscriptions](#subscriptions)
- [Resource Groups](#resource-groups)
- [Resources](#resources)
- [Tags](#tags)
- [Deployments](#deployments)
- [Resource Providers](#resource-providers)

## Subscriptions

### List All Subscriptions

```bash
curl -s 'https://management.azure.com/subscriptions?api-version=2022-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a Subscription

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}?api-version=2022-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### List Locations for a Subscription

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/locations?api-version=2022-12-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Resource Groups

api-version: `2021-04-01`

### List Resource Groups

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a Resource Group

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Create or Update a Resource Group

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "eastus",
    "tags": {
      "environment": "production",
      "team": "engineering"
    }
  }' | python3 -m json.tool
```

Required fields: `location`. Tags are optional.

### Delete a Resource Group

```bash
curl -s -X DELETE 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN"
```

Returns 202 Accepted. The deletion is asynchronous — all resources in the group are deleted.

### Check Existence

```bash
curl -s -o /dev/null -w "%{http_code}" -X HEAD \
  'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN"
```

Returns 204 if exists, 404 if not.

## Resources

### List All Resources in a Subscription

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resources?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### List Resources in a Resource Group

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/resources?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Filter Resources by Type

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resources?\$filter=resourceType%20eq%20%27Microsoft.Compute/virtualMachines%27&api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a Resource by ID

```bash
curl -s 'https://management.azure.com/{resourceId}?api-version={resource-specific-version}' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

The `resourceId` is the full ARM path, e.g.:
```
/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vmName}
```

## Tags

### Update Tags on a Resource

Use the resource-specific PATCH endpoint with `tags` in the body:

```bash
curl -s -X PATCH 'https://management.azure.com/{resourceId}?api-version={resource-api-version}' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tags": {
      "environment": "staging",
      "cost-center": "12345",
      "owner": "platform-team"
    }
  }' | python3 -m json.tool
```

### Tag Operations API

For bulk tag operations, use the Tags resource provider (api-version: `2021-04-01`):

```bash
# Create or update tags at a scope (merges with existing)
curl -s -X PATCH 'https://management.azure.com/{scope}/providers/Microsoft.Resources/tags/default?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "Merge",
    "properties": {
      "tags": {
        "new-tag": "new-value"
      }
    }
  }' | python3 -m json.tool
```

## Deployments

api-version: `2021-04-01`

### Create a Deployment (ARM Template)

```bash
curl -s -X PUT 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.Resources/deployments/{deploymentName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "mode": "Incremental",
      "template": {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "resources": []
      },
      "parameters": {}
    }
  }' | python3 -m json.tool
```

Deployment modes:
- **Incremental** (default) — adds resources without deleting existing ones
- **Complete** — deletes resources not in the template (use with caution)

### Get Deployment Status

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.Resources/deployments/{deploymentName}?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Check `properties.provisioningState` — values: `Accepted`, `Running`, `Succeeded`, `Failed`.

### List Deployments in a Resource Group

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.Resources/deployments?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get Deployment Operations (Detailed Status)

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.Resources/deployments/{deploymentName}/operations?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

Shows the status of each individual resource in the deployment.

## Resource Providers

### List All Registered Providers

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/providers?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Get a Specific Provider (with API Versions)

```bash
curl -s 'https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Compute?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

The response includes `resourceTypes[].apiVersions[]` — use this to discover valid api-version values for any resource type.

### Register a Provider

Some providers must be registered before use:

```bash
curl -s -X POST 'https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.ContainerInstance/register?api-version=2021-04-01' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```
