# SharePoint and OneDrive

## Contents

- [Sites](#sites) — Search, lists, items
- [Drives](#drives) — OneDrive and document libraries, file operations
- [Permissions](#permissions) — Sharing and access

## Sites

### Search Sites

```bash
curl 'https://graph.microsoft.com/v1.0/sites?\$search=marketing' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Site by Hostname and Path

```bash
curl 'https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/marketing' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Root Site

```bash
curl 'https://graph.microsoft.com/v1.0/sites/root' \
  -H "Authorization: Bearer $TOKEN"
```

### List SharePoint Lists

```bash
curl 'https://graph.microsoft.com/v1.0/sites/{siteId}/lists?\$select=displayName,id,list' \
  -H "Authorization: Bearer $TOKEN"
```

### List Items in a SharePoint List

```bash
curl 'https://graph.microsoft.com/v1.0/sites/{siteId}/lists/{listId}/items?\$expand=fields&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Item in a SharePoint List

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/sites/{siteId}/lists/{listId}/items' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "fields": {
      "Title": "New Item",
      "Status": "Active",
      "AssignedTo": "user@contoso.com"
    }
  }'
```

## Drives (OneDrive and Document Libraries)

### List Drives in a Site

```bash
curl 'https://graph.microsoft.com/v1.0/sites/{siteId}/drives?\$select=id,name,driveType' \
  -H "Authorization: Bearer $TOKEN"
```

### Get User's OneDrive

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/drive' \
  -H "Authorization: Bearer $TOKEN"
```

### List Items in Root

```bash
curl 'https://graph.microsoft.com/v1.0/drives/{driveId}/root/children?\$select=name,id,size,file,folder,lastModifiedDateTime' \
  -H "Authorization: Bearer $TOKEN"
```

### List Items in a Subfolder

```bash
curl 'https://graph.microsoft.com/v1.0/drives/{driveId}/root:/Documents/Projects:/children' \
  -H "Authorization: Bearer $TOKEN"
```

### Download File

```bash
curl -L 'https://graph.microsoft.com/v1.0/drives/{driveId}/root:/path/to/file.xlsx:/content' \
  -H "Authorization: Bearer $TOKEN" \
  -o file.xlsx
```

The `-L` flag follows the redirect to the download URL.

### Upload File (Under 4MB)

```bash
curl -X PUT 'https://graph.microsoft.com/v1.0/drives/{driveId}/root:/Documents/report.pdf:/content' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/pdf' \
  --data-binary @report.pdf
```

### Upload Large File (Over 4MB)

Create an upload session, then upload in chunks:

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/drives/{driveId}/root:/Documents/large-file.zip:/createUploadSession' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"item": {"@microsoft.graph.conflictBehavior": "rename"}}'
```

Response includes an `uploadUrl`. Upload bytes in 10MB chunks using PUT with `Content-Range` header:

```bash
curl -X PUT '{uploadUrl}' \
  -H 'Content-Range: bytes 0-10485759/52428800' \
  --data-binary @chunk1
```

## Permissions

### List Permissions on an Item

```bash
curl 'https://graph.microsoft.com/v1.0/drives/{driveId}/items/{itemId}/permissions' \
  -H "Authorization: Bearer $TOKEN"
```

### Share an Item

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/drives/{driveId}/items/{itemId}/invite' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "requireSignIn": true,
    "sendInvitation": true,
    "roles": ["write"],
    "recipients": [
      {"email": "colleague@contoso.com"}
    ],
    "message": "Here is the shared document."
  }'
```

Roles: `read`, `write`, `owner`.

### Create Sharing Link

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/drives/{driveId}/items/{itemId}/createLink' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "view",
    "scope": "organization"
  }'
```

Types: `view`, `edit`, `embed`. Scopes: `anonymous`, `organization`, `users`.
