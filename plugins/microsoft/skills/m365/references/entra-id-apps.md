# Entra ID: App Registrations, Service Principals, and SSO

## Contents

- [App Registrations](#app-registrations) — Create, list, update, delete apps
- [Service Principals](#service-principals) — Create and manage SPs
- [SAML SSO Configuration](#saml-sso-configuration-complete-recipe) — Complete 6-step recipe
- [OIDC SSO Configuration](#oidc-sso-configuration-complete-recipe) — Complete 4-step recipe
- [API Permissions](#api-permissions) — Look up GUIDs, set permissions, grant consent
- [Credential Management](#credential-management) — Secrets and certificates

## App Registrations

### Create Application

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/applications' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "My Application",
    "signInAudience": "AzureADMyOrg",
    "web": {
      "redirectUris": ["https://app.example.com/auth/callback"]
    }
  }'
```

Response includes `id` (object ID) and `appId` (client ID). Use `id` for Graph API calls on the application object. Use `appId` when referencing the app in service principals and consent flows.

### List Applications

```bash
curl 'https://graph.microsoft.com/v1.0/applications?\$select=id,appId,displayName&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

Filter by display name:

```bash
curl 'https://graph.microsoft.com/v1.0/applications?\$filter=displayName%20eq%20'\''My%20Application'\''' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Application

```bash
curl 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN"
```

### Update Application

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"displayName": "Updated Name"}'
```

### Delete Application

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN"
```

## Service Principals

A service principal is the local representation of an application in a tenant. It must exist before users can sign in or permissions can be granted.

### Create Service Principal

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/servicePrincipals' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"appId": "your-application-client-id"}'
```

### Find Service Principal by App ID

```bash
curl 'https://graph.microsoft.com/v1.0/servicePrincipals?\$filter=appId%20eq%20'\''your-application-client-id'\''' \
  -H "Authorization: Bearer $TOKEN"
```

### Update Service Principal

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/servicePrincipals/{spId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"tags": ["WindowsAzureActiveDirectoryIntegratedApp"]}'
```

## SAML SSO Configuration (Complete Recipe)

### Step 1: Instantiate from Non-Gallery Template

The non-gallery enterprise app template ID is `8adf8e6e-67b2-4cf2-a259-e3dc5476c621`.

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/applicationTemplates/8adf8e6e-67b2-4cf2-a259-e3dc5476c621/instantiate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"displayName": "My SAML App"}'
```

Response contains `application.id` (app object ID) and `servicePrincipal.id` (SP object ID). Save both.

### Step 2: Set SSO Mode on Service Principal

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/servicePrincipals/{spId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"preferredSingleSignOnMode": "saml"}'
```

### Step 3: Set Identifier URIs

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{appId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"identifierUris": ["https://app.example.com"]}'
```

### Step 4: Set Reply URLs (ACS Endpoint)

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{appId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"web": {"redirectUris": ["https://app.example.com/saml/acs"]}}'
```

### Step 5: Generate and Upload Signing Certificate

Generate a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 -keyout saml-key.pem -out saml-cert.pem \
  -days 365 -nodes -subj "/CN=My SAML App"
```

Base64-encode the PFX and upload via `keyCredentials` on the application object.

### Step 6: Assign Users or Groups

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/servicePrincipals/{spId}/appRoleAssignments' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "principalId": "{userId-or-groupId}",
    "resourceId": "{spId}",
    "appRoleId": "00000000-0000-0000-0000-000000000000"
  }'
```

Use `appRoleId` of all zeros for the default access role.

## OIDC SSO Configuration (Complete Recipe)

### Step 1: Create Application with Redirect URIs

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/applications' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "My OIDC App",
    "signInAudience": "AzureADMyOrg",
    "web": {
      "redirectUris": ["https://app.example.com/auth/callback"],
      "implicitGrantSettings": {"enableIdTokenIssuance": true}
    }
  }'
```

### Step 2: Create Service Principal

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/servicePrincipals' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"appId": "{appId-from-step-1}"}'
```

### Step 3: Add Client Secret

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/applications/{id}/addPassword' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "passwordCredential": {
      "displayName": "OIDC Client Secret",
      "endDateTime": "2027-01-01T00:00:00Z"
    }
  }'
```

### Step 4: Configure Optional Token Claims

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "optionalClaims": {
      "idToken": [
        {"name": "email", "essential": true},
        {"name": "upn", "essential": true}
      ]
    }
  }'
```

## API Permissions

### Look Up Microsoft Graph Permission GUIDs

First, get the Microsoft Graph service principal (well-known appId `00000003-0000-0000-c000-000000000000`):

```bash
curl 'https://graph.microsoft.com/v1.0/servicePrincipals?\$filter=appId%20eq%20'\''00000003-0000-0000-c000-000000000000'\''&\$select=id,appRoles,oauth2PermissionScopes' \
  -H "Authorization: Bearer $TOKEN"
```

- `appRoles` — application permissions (used with client credentials flow)
- `oauth2PermissionScopes` — delegated permissions (used with user sign-in)

Search the returned arrays for the permission `value` field (e.g., `User.Read.All`) to find the corresponding GUID.

### Set Required Permissions on Application

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "requiredResourceAccess": [
      {
        "resourceAppId": "00000003-0000-0000-c000-000000000000",
        "resourceAccess": [
          {"id": "{permission-guid}", "type": "Role"},
          {"id": "{permission-guid-2}", "type": "Role"}
        ]
      }
    ]
  }'
```

Use `"type": "Role"` for application permissions, `"type": "Scope"` for delegated.

### Grant Admin Consent (Application Permissions)

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/servicePrincipals/{spId}/appRoleAssignments' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "principalId": "{spId}",
    "resourceId": "{graphSpId}",
    "appRoleId": "{permission-guid}"
  }'
```

Where `{graphSpId}` is the object ID of the Microsoft Graph service principal in your tenant.

## Credential Management

### Add Password (Client Secret)

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/applications/{id}/addPassword' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "passwordCredential": {
      "displayName": "Production Secret",
      "endDateTime": "2028-01-01T00:00:00Z"
    }
  }'
```

Response includes `secretText` — the actual secret value. This is only returned once.

### Add Certificate

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/applications/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "keyCredentials": [
      {
        "displayName": "Production Cert",
        "type": "AsymmetricX509Cert",
        "usage": "Verify",
        "key": "base64-encoded-cert-data",
        "endDateTime": "2027-01-01T00:00:00Z"
      }
    ]
  }'
```

### List Credentials

```bash
curl 'https://graph.microsoft.com/v1.0/applications/{id}?\$select=passwordCredentials,keyCredentials' \
  -H "Authorization: Bearer $TOKEN"
```

Note: `passwordCredentials` never returns the secret value after creation — only metadata (hint, expiry, keyId).
