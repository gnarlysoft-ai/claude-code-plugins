# Microsoft Graph API Patterns

Universal patterns that apply to all Graph API operations.

## Contents

- [URL Structure](#url-structure)
- [OData Query Parameters](#odata-query-parameters)
- [ConsistencyLevel Header](#consistencylevel-header)
- [Pagination](#pagination)
- [Batch Requests](#batch-requests)
- [Error Format](#error-format)

## URL Structure

```
https://graph.microsoft.com/{version}/{resource}[/{id}][/{relationship}]
```

- `v1.0` — stable, production-ready endpoints
- `beta` — preview features, may change without notice

Examples:
- `https://graph.microsoft.com/v1.0/users`
- `https://graph.microsoft.com/v1.0/users/{id}/messages`
- `https://graph.microsoft.com/beta/identity/conditionalAccess/policies`

## OData Query Parameters

Append query parameters to control response shape and filtering.

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `$select` | Choose fields | `$select=displayName,mail` |
| `$filter` | Filter results | `$filter=displayName eq 'John'` |
| `$expand` | Include related resources | `$expand=members` |
| `$top` | Page size (max varies by resource) | `$top=25` |
| `$skip` | Skip N records | `$skip=25` |
| `$orderby` | Sort results | `$orderby=displayName asc` |
| `$search` | Full-text search | `$search="marketing"` |
| `$count` | Include total count | `$count=true` |

### Filter Operators

- `eq` — equals: `$filter=displayName eq 'John Smith'`
- `ne` — not equals: `$filter=accountEnabled ne false`
- `gt`, `ge`, `lt`, `le` — comparison: `$filter=createdDateTime gt 2025-01-01T00:00:00Z`
- `startswith` — prefix match: `$filter=startswith(displayName,'John')`
- `endswith` — suffix match (requires ConsistencyLevel): `$filter=endswith(mail,'@example.com')`
- `contains` — substring match (limited support): `$filter=contains(displayName,'smith')`
- `in` — set membership: `$filter=id in ('id1','id2')`
- Logical: `and`, `or`, `not`

## ConsistencyLevel Header

Required for advanced queries including `endswith`, `$count`, `$search`, and certain `$filter` combinations on directory objects:

```bash
curl 'https://graph.microsoft.com/v1.0/users?\$count=true&\$search="displayName:john"&\$select=displayName,mail' \
  -H "Authorization: Bearer $TOKEN" \
  -H "ConsistencyLevel: eventual"
```

## Pagination

When more results exist than the current page, the response includes `@odata.nextLink`:

```json
{
  "value": [...],
  "@odata.nextLink": "https://graph.microsoft.com/v1.0/users?$skiptoken=..."
}
```

Follow the full URL from `@odata.nextLink` as-is to get the next page. Do not modify the URL or construct skip tokens manually.

## Batch Requests

Send up to 20 requests in a single HTTP call:

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/$batch' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "requests": [
      {"id": "1", "method": "GET", "url": "/users?$top=5"},
      {"id": "2", "method": "GET", "url": "/groups?$top=5"},
      {"id": "3", "method": "GET", "url": "/applications?$top=5"}
    ]
  }'
```

Response contains individual status codes for each request. Requests within a batch execute independently — one failure does not affect others.

For sequential dependencies, use `dependsOn`:

```json
{
  "requests": [
    {"id": "1", "method": "POST", "url": "/applications", "body": {...}},
    {"id": "2", "method": "POST", "url": "/servicePrincipals", "body": {...}, "dependsOn": ["1"]}
  ]
}
```

## Error Format

```json
{
  "error": {
    "code": "Request_BadRequest",
    "message": "A value is required for property 'displayName'.",
    "innerError": {
      "date": "2025-01-15T10:30:00",
      "request-id": "...",
      "client-request-id": "..."
    }
  }
}
```

Common HTTP status codes:
- **400** — Bad request (invalid query, missing fields)
- **401** — Unauthorized (expired or missing token)
- **403** — Forbidden (insufficient permissions)
- **404** — Resource not found
- **409** — Conflict (resource already exists)
- **429** — Too many requests (throttled — respect the `Retry-After` header value in seconds)

Note: For dollar sign escaping and authentication patterns, see the main SKILL.md.
