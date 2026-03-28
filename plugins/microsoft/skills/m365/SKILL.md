---
name: m365
description: Microsoft 365 and Entra ID administration via Microsoft Graph API. Use when the user wants to manage Azure AD apps, SSO, users, groups, email, calendar, SharePoint, Teams, conditional access, or any other M365 operation. Supports multiple tenants.
allowed-tools: Bash, Read
user-invocable: true
argument-hint: "<action> [--profile NAME] (e.g., 'create SAML app for docs.example.com', 'list users', 'send email as jacob@gnarlysoft.com', 'setup new tenant')"
---

# Microsoft 365 & Entra ID Administration

<context>
This skill provides full access to Microsoft 365 and Entra ID (Azure AD) via the Microsoft Graph REST API. It supports any Graph API endpoint — not just a fixed set of operations. When Microsoft adds new APIs, you can use them immediately.

Base URL: `https://graph.microsoft.com/v1.0` (stable) or `https://graph.microsoft.com/beta` (preview)

Authentication uses OAuth 2.0 client credentials flow with multi-tenant profile support. Each profile represents one M365 tenant.
</context>

<instructions>

## Setup Detection

On first use, check if profiles are configured:

```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py list-profiles
```

- **No profiles found** → Read `${CLAUDE_PLUGIN_ROOT}/skills/m365/references/setup-tenant.md` and guide the user through tenant onboarding.
- **User asks about a new tenant or client** → Same: read `setup-tenant.md` for the appropriate scenario (own tenant, client tenant, or multi-tenant app).
- **Profiles exist and user has an operational request** → Proceed normally.

## Configuration

Environment variables (same pattern as mcp-365-admin):

```
M365_PROFILES=gnarlysoft,clientname
M365_GNARLYSOFT_TENANT_ID=<directory-id>
M365_GNARLYSOFT_CLIENT_ID=<application-id>
M365_GNARLYSOFT_CLIENT_SECRET=<secret-value>
```

### Permission Tiers

| Tier | Use Case | Key Permissions |
|------|----------|----------------|
| **Basic** | Email, calendar, users | User.Read.All, Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, Group.ReadWrite.All |
| **Admin** | + App registrations, SSO | Basic + Application.ReadWrite.All, AppRoleAssignment.ReadWrite.All, Directory.ReadWrite.All |
| **Full** | + Conditional access, everything | Admin + Policy.ReadWrite.ConditionalAccess, Sites.ReadWrite.All, Files.ReadWrite.All, Team.ReadBasic.All |

If a request fails with 403 Forbidden, check which tier is needed and guide the user to add permissions.

## Authentication

Acquire a bearer token using the helper script:

```bash
TOKEN=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token PROFILE_NAME)
```

Replace `PROFILE_NAME` with the profile to use. If there's only one profile, use it automatically. If multiple exist and the user hasn't specified, ask which one.

To test connectivity:
```bash
cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py test PROFILE_NAME
```

## Making Requests

### GET (read data)
```bash
curl -s 'https://graph.microsoft.com/v1.0/{endpoint}?\$select=field1,field2&\$top=25' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool
```

### POST (create / action)
```bash
curl -s -X POST 'https://graph.microsoft.com/v1.0/{endpoint}' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' | python3 -m json.tool
```

### PATCH (update)
```bash
curl -s -X PATCH 'https://graph.microsoft.com/v1.0/{endpoint}' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "newValue"}' | python3 -m json.tool
```

### DELETE
```bash
curl -s -X DELETE 'https://graph.microsoft.com/v1.0/{endpoint}' \
  -H "Authorization: Bearer $TOKEN"
```

### Important: Dollar Sign Escaping

OData query parameters use `$` which bash interprets as variable expansion. Always escape with backslash:

```bash
# Double quotes: escape $ with backslash (allows $TOKEN to expand)
curl -s "https://graph.microsoft.com/v1.0/users?\$select=displayName,mail&\$top=10" ...

# Single quotes: no escaping needed (but can't use $TOKEN inline)
curl -s 'https://graph.microsoft.com/v1.0/users?$select=displayName,mail&$top=10' ...
```

### Advanced Queries

For `$search`, `$count`, `endsWith`, and certain `$filter` operators, add the ConsistencyLevel header:

```bash
curl -s 'https://graph.microsoft.com/v1.0/users?\$search="displayName:john"&\$count=true' \
  -H "Authorization: Bearer $TOKEN" \
  -H "ConsistencyLevel: eventual" | python3 -m json.tool
```

## Reference Routing

Read the appropriate reference file based on what the user needs:

| User wants to... | Read this reference |
|-------------------|-------------------|
| Set up a new tenant, add a client, configure credentials | `references/setup-tenant.md` |
| Create app registrations, service principals, configure SSO (SAML/OIDC), manage certificates/secrets, set API permissions | `references/entra-id-apps.md` |
| Manage users, groups, roles, licenses | `references/users-groups.md` |
| Send/read email, manage calendar, schedule meetings | `references/mail-calendar.md` |
| Work with SharePoint sites, OneDrive files, lists | `references/sharepoint-onedrive.md` |
| Manage Teams, channels, chat messages | `references/teams.md` |
| Configure conditional access policies | `references/conditional-access.md` |
| Manage Exchange: shared mailboxes, transport rules, mail flow, message tracing | `references/exchange-powershell.md` |
| Understand pagination, filtering, batch requests, errors | `references/graph-api-patterns.md` |

Read the reference file using:
```
Read ${CLAUDE_PLUGIN_ROOT}/skills/m365/references/<filename>
```

For complex operations that span categories (e.g., "create an app and assign it to a group"), read multiple reference files.

## Multi-Tenant Operations

### Profile Switching

Each curl command uses the token from a specific profile. To work across tenants in the same session:

```bash
# Get tokens for both tenants
TOKEN_GS=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token gnarlysoft)
TOKEN_CLIENT=$(cd ${CLAUDE_PLUGIN_ROOT}/scripts && uv run python auth.py get-token clientname)

# Now use the appropriate token for each call
curl -s 'https://graph.microsoft.com/v1.0/users' -H "Authorization: Bearer $TOKEN_GS" ...
curl -s 'https://graph.microsoft.com/v1.0/users' -H "Authorization: Bearer $TOKEN_CLIENT" ...
```

### Cross-Tenant App Registration

To create an app in your tenant that works in a client's tenant:
1. Read `references/entra-id-apps.md` for the app creation flow
2. Read `references/setup-tenant.md` Scenario 3 for the multi-tenant consent pattern
3. Create the app with `signInAudience: AzureADMultipleOrgs`
4. Build the admin consent URL for the client tenant

## Constructing Unknown Endpoints

The Graph API follows consistent patterns. For any endpoint not covered in the reference files:

### URL Pattern
```
https://graph.microsoft.com/v1.0/{resource}[/{id}][/{relationship}]
```

### HTTP Method Conventions
- **GET** = Read (list or get by ID)
- **POST** = Create new resource or trigger an action
- **PATCH** = Update existing resource
- **DELETE** = Remove resource
- **PUT** = Replace resource or set a reference

### Action Endpoints
Actions use POST with a function-style URL:
```
POST /users/{id}/microsoft.graph.revokeSignInSessions
POST /servicePrincipals/{id}/microsoft.graph.addTokenSigningCertificate
```

### Beta Endpoints
For features not yet in v1.0, try the beta API:
```
https://graph.microsoft.com/beta/{same-path}
```

### Discovering Endpoints
If unsure about an endpoint's exact shape, try a GET on the parent resource to see available relationships, or check the `@odata.type` in responses for the entity type.

## Behavior Guidelines

1. **Never print secrets** — mask client_secret values, token values, and passwords in output to the user.
2. **Confirm destructive operations** — before DELETE on apps, users, groups, or policies, show what will be deleted and ask for confirmation.
3. **Default pagination** — use `$top=25` for list operations unless the user asks for more.
4. **Format results** — present list results in markdown tables. For single-resource responses, use key-value format.
5. **Profile context** — always tell the user which profile/tenant you're operating against, especially when multiple profiles exist.
6. **Error guidance** — if a 403 occurs, explain which permission is likely missing and which tier it belongs to. If 429 (throttled), respect the Retry-After header.
7. **App registration safety** — when creating app registrations, always confirm the display name, account type, and permissions before proceeding.
8. **SSO confirmation** — when configuring SSO, confirm the identifier URI, reply URL, and SSO mode before making changes.

</instructions>

<examples>

### List users in default tenant
```
/m365 list all users with their email addresses
```

### Create a SAML SSO app for a self-hosted service
```
/m365 create a SAML SSO app for my wiki at wiki.gnarlysoft.com --profile gnarlysoft
```

### Set up a new client tenant
```
/m365 setup a new tenant for our client Acme Corp
```

### Send email
```
/m365 send an email from jacob@gnarlysoft.com to partner@acme.com about the project kickoff
```

### Create conditional access policy
```
/m365 create a conditional access policy requiring MFA for all users --profile gnarlysoft
```

### Cross-tenant operation
```
/m365 create an app registration in our tenant and set it up for SSO in the client's tenant
```

</examples>
