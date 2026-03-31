# Conditional Access Policies

Requires `Policy.ReadWrite.ConditionalAccess` permission (Full tier).

## Contents

- [Policies](#policies) — CRUD, states
- [Named Locations](#named-locations) — IP and country-based
- [Common Policy Templates](#common-policy-templates) — Ready-to-use JSON recipes

## Policies

### List Policies

```bash
curl 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies?\$select=id,displayName,state' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Policy

```bash
curl 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{id}' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Policy

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d @policy.json
```

### Update Policy

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"state": "enabled"}'
```

### Delete Policy

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/{id}' \
  -H "Authorization: Bearer $TOKEN"
```

### Policy States

- `enabled` — actively enforced
- `disabled` — not enforced
- `enabledForReportingButNotEnforced` — report-only mode (logs sign-in impact without blocking)

Always create new policies in `enabledForReportingButNotEnforced` state first to evaluate impact before enabling.

## Named Locations

### List Named Locations

```bash
curl 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations' \
  -H "Authorization: Bearer $TOKEN"
```

### Create IP-Based Named Location

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "@odata.type": "#microsoft.graph.ipNamedLocation",
    "displayName": "Corporate Office",
    "isTrusted": true,
    "ipRanges": [
      {"@odata.type": "#microsoft.graph.iPv4CidrRange", "cidrAddress": "203.0.113.0/24"},
      {"@odata.type": "#microsoft.graph.iPv4CidrRange", "cidrAddress": "198.51.100.0/24"}
    ]
  }'
```

### Create Country-Based Named Location

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/identity/conditionalAccess/namedLocations' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "@odata.type": "#microsoft.graph.countryNamedLocation",
    "displayName": "Blocked Countries",
    "countriesAndRegions": ["RU", "CN", "KP", "IR"],
    "includeUnknownCountriesAndRegions": false
  }'
```

## Common Policy Templates

### 1. Block Legacy Authentication

```json
{
  "displayName": "Block legacy authentication",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "clientAppTypes": ["exchangeActiveSync", "other"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

### 2. Require MFA for All Users

```json
{
  "displayName": "Require MFA for all users",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"],
      "excludeUsers": ["breakGlassAccountId1", "breakGlassAccountId2"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

Always exclude at least two break-glass (emergency access) accounts from MFA policies to prevent lockout.

### 3. Require MFA for Admins

```json
{
  "displayName": "Require MFA for admin roles",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeRoles": [
        "62e90394-69f5-4237-9190-012177145e10",
        "fe930be7-5e62-47db-91af-98c3a49a38b1",
        "194ae4cb-b126-40b2-bd5b-6091b380977d",
        "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3",
        "29232cdf-9323-42fd-ade2-1d097af3e4de",
        "f28a1f50-f6e7-4571-818b-6a12f2af6b6c"
      ]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

Role IDs included: Global Admin, User Admin, Security Admin, Application Admin, Exchange Admin, SharePoint Admin.

### 4. Block Access from Untrusted Locations

```json
{
  "displayName": "Block access from untrusted locations",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"],
      "excludeUsers": ["breakGlassAccountId1"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "locations": {
      "includeLocations": ["All"],
      "excludeLocations": ["AllTrusted"]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
```

This blocks all access except from IP ranges marked as trusted in named locations. Ensure your corporate IPs are added as trusted named locations before enabling.
