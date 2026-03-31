# Azure RBAC Setup Guide

How to grant your app registration access to Azure resources via Role-Based Access Control (RBAC).

## Contents

- [Prerequisites](#prerequisites)
- [Understanding the Difference: Graph vs Azure](#understanding-the-difference-graph-vs-azure)
- [Scope Levels](#scope-levels)
- [Common Roles](#common-roles)
- [Option 1: Azure Portal](#option-1-azure-portal)
- [Option 2: Azure CLI](#option-2-azure-cli)
- [Verifying Access](#verifying-access)
- [Troubleshooting](#troubleshooting)

## Prerequisites

You must already have an app registration (service principal) created in Azure AD. If not, follow the m365 setup first:
```
Read ${CLAUDE_PLUGIN_ROOT}/skills/m365/references/setup-tenant.md
```

The same `client_id`, `client_secret`, and `tenant_id` are used for both Graph API and Azure Resource Manager. The difference is in **authorization** — Graph uses API permissions, Azure uses RBAC role assignments.

## Understanding the Difference: Graph vs Azure

| Aspect | Microsoft Graph API | Azure Resource Manager |
|--------|-------------------|----------------------|
| **Purpose** | Manage M365 (users, mail, apps) | Manage Azure infra (VMs, storage, networking) |
| **Authorization** | API permissions in app registration | RBAC role assignments on Azure resources |
| **Scope** | Tenant-wide | Per subscription/resource group/resource |
| **Token endpoint** | Same OAuth endpoint | Same OAuth endpoint |
| **Token scope** | `https://graph.microsoft.com/.default` | `https://management.azure.com/.default` |

Having Graph API permissions does **NOT** grant Azure access and vice versa. They are completely independent authorization systems.

## Scope Levels

RBAC roles can be assigned at different levels. Roles assigned at a higher scope are inherited by child resources.

```
Management Group
  └── Subscription
        └── Resource Group
              └── Individual Resource
```

- **Management group** — spans multiple subscriptions (enterprise scenarios)
- **Subscription** — most common starting point; grants access to everything in the subscription
- **Resource group** — limits access to resources within one group
- **Individual resource** — narrowest scope (e.g., one specific VM)

## Common Roles

| Role | Description | Use Case |
|------|-------------|----------|
| **Reader** | View all resources, no changes | Monitoring, auditing, reporting |
| **Contributor** | Create, update, delete resources. Cannot manage access (IAM) | Standard infrastructure management |
| **Owner** | Full access including IAM role assignments | Full admin (use sparingly) |
| **User Access Administrator** | Manage role assignments only | Delegating access without resource management |

For specific resource types, there are also scoped roles like `Virtual Machine Contributor`, `Storage Account Contributor`, `Network Contributor`, etc.

## Option 1: Azure Portal

### Step 1: Navigate to the Scope

Choose where to assign the role:

- **Subscription**: [Azure Portal](https://portal.azure.com) → **Subscriptions** → Select your subscription
- **Resource group**: **Subscriptions** → Select subscription → **Resource groups** → Select group
- **Resource**: Navigate to the specific resource

### Step 2: Open Access Control

Click **Access control (IAM)** in the left menu.

### Step 3: Add Role Assignment

1. Click **Add** → **Add role assignment**
2. Under **Role**, search for and select the desired role (e.g., `Contributor`)
3. Click **Next**
4. Under **Members**, select **User, group, or service principal**
5. Click **Select members**
6. Search for your app registration name (e.g., `Claude Code M365 Admin`)
7. Select the service principal and click **Select**
8. Click **Review + assign**

### Step 4: Verify

On the **Role assignments** tab of Access control (IAM), confirm the new assignment appears.

## Option 2: Azure CLI

If the Azure CLI (`az`) is installed, you can assign roles from the command line.

### Assign Contributor at Subscription Level

```bash
az role assignment create \
  --assignee <application-client-id> \
  --role "Contributor" \
  --scope "/subscriptions/<subscription-id>"
```

### Assign Reader at Resource Group Level

```bash
az role assignment create \
  --assignee <application-client-id> \
  --role "Reader" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>"
```

### Assign a Specific Role at Resource Level

```bash
az role assignment create \
  --assignee <application-client-id> \
  --role "Storage Account Contributor" \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<account-name>"
```

### List Current Assignments

```bash
az role assignment list --assignee <application-client-id> --output table
```

## Verifying Access

After assigning the role, test connectivity using auth.py:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py test PROFILE_NAME --scope azure
```

This calls `GET /subscriptions?api-version=2022-12-01` and confirms the app can list subscriptions.

If the test fails with 403:
- Role assignments can take up to **5 minutes** to propagate
- Wait and retry
- Verify the assignment was made to the correct service principal (check the Application ID matches)

## Troubleshooting

### "The client does not have authorization to perform action"
The app has a valid token but no RBAC role at the requested scope. Add a role assignment as described above.

### "No subscriptions found"
The role assignment may be at a resource group or resource level, not the subscription level. The `GET /subscriptions` endpoint requires at least Reader on one subscription.

### "AuthorizationFailed" on a specific resource
The app has subscription-level access but the specific resource may be in a different subscription, or the role doesn't cover that operation. Check the scope of the role assignment.

### Token works for Graph but not Azure
This is expected. Graph API permissions and Azure RBAC are independent. You need both configured separately. Use `--scope azure` when obtaining the token:
```bash
TOKEN=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token PROFILE --scope azure)
```
