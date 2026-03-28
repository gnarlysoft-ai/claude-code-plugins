# Tenant Onboarding Guide

How to register an Azure AD application and configure credentials for Microsoft Graph API access.

## Contents

- [Scenario 1: Own Tenant](#scenario-1-own-tenant) — You have admin access
- [Scenario 2: Client Tenant](#scenario-2-client-tenant-direct-admin-access) — Direct admin access to client
- [Scenario 3: Multi-Tenant App](#scenario-3-multi-tenant-app-register-once-consent-everywhere) — One app, many tenants
- [Environment Variable Format](#environment-variable-format) — Profile configuration

## Scenario 1: Own Tenant

You have admin access to your own Azure AD tenant.

### Step 1: Register the Application

1. Go to [Azure Portal App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
3. Name: `Claude Code M365 Admin`
4. Supported account types: **Accounts in this organizational directory only** (Single tenant)
5. Click **Register**

### Step 2: Copy Identifiers

From the app's **Overview** page, copy:
- **Application (client) ID** — the app's unique identifier
- **Directory (tenant) ID** — your Azure AD tenant identifier

### Step 3: Add API Permissions

Go to **API permissions** > **Add a permission** > **Microsoft Graph** > **Application permissions**.

Add permissions based on the access tier you need:

**Basic Tier** — Mail, calendar, and group management:
- `User.Read.All`
- `Mail.ReadWrite`
- `Mail.Send`
- `Calendars.ReadWrite`
- `Group.ReadWrite.All`

**Admin Tier** — Basic + app registration and directory management:
- All Basic permissions, plus:
- `Application.ReadWrite.All`
- `AppRoleAssignment.ReadWrite.All`
- `Directory.ReadWrite.All`

**Full Tier** — Admin + conditional access, SharePoint, OneDrive, and Teams:
- All Admin permissions, plus:
- `Policy.ReadWrite.ConditionalAccess`
- `Sites.ReadWrite.All`
- `Files.ReadWrite.All`
- `Team.ReadBasic.All`
- `Channel.ReadBasic.All`

### Step 4: Grant Admin Consent

Click **Grant admin consent for [your organization]** and confirm. All permissions should show a green checkmark.

### Step 5: Create Client Secret

1. Go to **Certificates & secrets** > **Client secrets** > **New client secret**
2. Description: `Claude Code`
3. Expires: **24 months**
4. Click **Add**
5. **Copy the VALUE immediately** — it is only displayed once

### Step 6: Set Environment Variables

```bash
export M365_PROFILES=gnarlysoft
export M365_GNARLYSOFT_TENANT_ID=your-tenant-id
export M365_GNARLYSOFT_CLIENT_ID=your-client-id
export M365_GNARLYSOFT_CLIENT_SECRET=your-client-secret
```

## Scenario 2: Client Tenant (Direct Admin Access)

You have admin access to a client's Azure AD tenant directly.

Follow the same steps as Scenario 1, but in the client's tenant. Switch Azure Portal context using the directory switcher (top right > **Switch directory**) or use a separate browser profile for each tenant.

Set environment variables with a distinct profile name:

```bash
export M365_PROFILES=gnarlysoft,clientname
export M365_GNARLYSOFT_TENANT_ID=your-tenant-id
export M365_GNARLYSOFT_CLIENT_ID=your-client-id
export M365_GNARLYSOFT_CLIENT_SECRET=your-client-secret
export M365_CLIENTNAME_TENANT_ID=client-tenant-id
export M365_CLIENTNAME_CLIENT_ID=client-app-client-id
export M365_CLIENTNAME_CLIENT_SECRET=client-app-client-secret
```

## Scenario 3: Multi-Tenant App (Register Once, Consent Everywhere)

Register one app in your own tenant and grant it access to multiple client tenants.

### Step 1: Register as Multi-Tenant

During app registration, select **Accounts in any organizational directory** (signInAudience: `AzureADMultipleOrgs`). Configure permissions as described in Scenario 1.

### Step 2: Build Admin Consent URL

For each client tenant, construct this URL and send it to the client's Azure AD admin:

```
https://login.microsoftonline.com/{client-tenant-id}/adminconsent?client_id={your-app-client-id}
```

The client admin visits the URL, reviews the requested permissions, and clicks **Accept**.

### Step 3: Configure Profiles

Each client gets its own profile with the client's tenant ID but your app's client ID and secret:

```bash
export M365_PROFILES=gnarlysoft,clientname
export M365_GNARLYSOFT_TENANT_ID=your-tenant-id
export M365_GNARLYSOFT_CLIENT_ID=your-app-client-id
export M365_GNARLYSOFT_CLIENT_SECRET=your-app-client-secret
export M365_CLIENTNAME_TENANT_ID=client-tenant-id
export M365_CLIENTNAME_CLIENT_ID=your-app-client-id
export M365_CLIENTNAME_CLIENT_SECRET=your-app-client-secret
```

Note: `CLIENT_ID` and `CLIENT_SECRET` are the same across profiles because it is the same app registration. Only `TENANT_ID` differs per client.

## Environment Variable Format

The multi-profile convention uses a comma-separated list of profile names, with each profile's credentials namespaced by the uppercase profile name:

```bash
M365_PROFILES=profile1,profile2
M365_PROFILE1_TENANT_ID=xxx
M365_PROFILE1_CLIENT_ID=xxx
M365_PROFILE1_CLIENT_SECRET=xxx
M365_PROFILE2_TENANT_ID=yyy
M365_PROFILE2_CLIENT_ID=yyy
M365_PROFILE2_CLIENT_SECRET=yyy
```
