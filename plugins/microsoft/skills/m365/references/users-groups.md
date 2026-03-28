# Users, Groups, Roles, and Licenses

## Contents

- [Users](#users) — CRUD, manager assignment
- [Groups](#groups) — Security groups, M365 groups, membership
- [Directory Roles](#directory-roles) — Role assignments
- [Licenses](#licenses) — License management

## Users

### List Users

```bash
curl 'https://graph.microsoft.com/v1.0/users?\$select=displayName,mail,userPrincipalName,accountEnabled&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

### Get User by ID or UPN

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id-or-userPrincipalName}?\$select=displayName,mail,jobTitle,department' \
  -H "Authorization: Bearer $TOKEN"
```

UPN example: `user@contoso.com`. URL-encode the `@` if needed: `user%40contoso.com`.

### Create User

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "accountEnabled": true,
    "displayName": "Jane Smith",
    "mailNickname": "janesmith",
    "userPrincipalName": "janesmith@contoso.com",
    "passwordProfile": {
      "forceChangePasswordNextSignIn": true,
      "password": "TempP@ssw0rd!"
    }
  }'
```

All five fields are required for user creation.

### Update User

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/users/{id}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"jobTitle": "Senior Engineer", "department": "Engineering"}'
```

### Delete User

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/users/{id}' \
  -H "Authorization: Bearer $TOKEN"
```

Deleted users are soft-deleted and recoverable for 30 days from the `deletedItems` collection.

### Get Manager

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/manager?\$select=displayName,mail' \
  -H "Authorization: Bearer $TOKEN"
```

### Set Manager

```bash
curl -X PUT 'https://graph.microsoft.com/v1.0/users/{id}/manager/$ref' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"@odata.id": "https://graph.microsoft.com/v1.0/users/{managerId}"}'
```

## Groups

### List Groups

```bash
curl 'https://graph.microsoft.com/v1.0/groups?\$select=displayName,groupTypes,mailEnabled,securityEnabled&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

Filter to Microsoft 365 groups only:

```bash
curl 'https://graph.microsoft.com/v1.0/groups?\$filter=groupTypes/any(g:g%20eq%20'\''Unified'\'')&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Security Group

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/groups' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Engineering Team",
    "description": "Security group for engineering",
    "mailEnabled": false,
    "mailNickname": "engineering-team",
    "securityEnabled": true
  }'
```

### Create Microsoft 365 Group

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/groups' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Marketing Team",
    "description": "M365 group with mailbox and shared resources",
    "mailEnabled": true,
    "mailNickname": "marketing-team",
    "securityEnabled": false,
    "groupTypes": ["Unified"]
  }'
```

### List Group Members

```bash
curl 'https://graph.microsoft.com/v1.0/groups/{groupId}/members?\$select=displayName,mail' \
  -H "Authorization: Bearer $TOKEN"
```

### Add Member to Group

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/groups/{groupId}/members/$ref' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"@odata.id": "https://graph.microsoft.com/v1.0/users/{userId}"}'
```

### Remove Member from Group

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/groups/{groupId}/members/{userId}/$ref' \
  -H "Authorization: Bearer $TOKEN"
```

## Directory Roles

### List Activated Roles

```bash
curl 'https://graph.microsoft.com/v1.0/directoryRoles?\$select=displayName,id,roleTemplateId' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Role Assignments for a User

```bash
curl 'https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments?\$filter=principalId%20eq%20'\''userId'\''&\$expand=roleDefinition' \
  -H "Authorization: Bearer $TOKEN"
```

### Assign Directory Role

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "principalId": "{userId}",
    "roleDefinitionId": "{roleDefinitionId}",
    "directoryScopeId": "/"
  }'
```

Common role template IDs:
- Global Administrator: `62e90394-69f5-4237-9190-012177145e10`
- User Administrator: `fe930be7-5e62-47db-91af-98c3a49a38b1`
- Application Administrator: `9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3`
- Security Administrator: `194ae4cb-b126-40b2-bd5b-6091b380977d`

## Licenses

### Get User's License Details

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/licenseDetails' \
  -H "Authorization: Bearer $TOKEN"
```

### Assign License

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/assignLicense' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "addLicenses": [
      {"skuId": "{sku-guid}", "disabledPlans": []}
    ],
    "removeLicenses": []
  }'
```

### Remove License

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/assignLicense' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "addLicenses": [],
    "removeLicenses": ["{sku-guid}"]
  }'
```

### List Available Licenses in Tenant

```bash
curl 'https://graph.microsoft.com/v1.0/subscribedSkus?\$select=skuId,skuPartNumber,consumedUnits,prepaidUnits' \
  -H "Authorization: Bearer $TOKEN"
```

Common SKU part numbers: `ENTERPRISEPACK` (E3), `SPE_E5` (E5), `FLOW_FREE` (Power Automate Free), `TEAMS_EXPLORATORY`.
