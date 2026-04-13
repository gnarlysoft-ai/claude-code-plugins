# OneDrive & SharePoint Files Reference

## Table of Contents

- [Endpoints](#endpoints)
- [Known SharePoint Drive IDs](#known-sharepoint-drive-ids)
- [List Files in Root](#list-files-in-root)
- [List Files in Subfolder](#list-files-in-subfolder)
- [Upload Small File (< 4MB)](#upload-small-file--4mb)
- [Upload Text Content](#upload-text-content)
- [Upload Large File (> 4MB)](#upload-large-file--4mb)
- [Upload to SharePoint](#upload-to-sharepoint)
- [Create Sharing Link](#create-sharing-link)
- [Download File](#download-file)
- [Delete File](#delete-file)
- [Check Storage Quota](#check-storage-quota)
- [List SharePoint Sites](#list-sharepoint-sites)
- [Full Workflow: Upload to SharePoint + Sharing Link](#full-workflow-upload-to-sharepoint--sharing-link)
- [Important Caveats](#important-caveats)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/drive/root/children | List files in OneDrive root |
| GET | /me/drive/root:/{path}:/children | List files in a subfolder |
| PUT | /me/drive/root:/{path}:/content | Upload file < 4MB |
| POST | /me/drive/root:/{path}:/createUploadSession | Create resumable upload session (> 4MB) |
| POST | /me/drive/items/{itemId}/createLink | Create a sharing link |
| DELETE | /me/drive/items/{itemId} | Delete a file |
| GET | /me/drive/items/{itemId} | Get file metadata (includes downloadUrl) |
| GET | /me/drive | Get drive info (quota) |
| GET | /drives/{driveId}/root/children | List files in a specific drive (e.g., SharePoint) |
| GET | /drives/{driveId}/root:/{path}:/children | List files in a subfolder of a specific drive |
| PUT | /drives/{driveId}/root:/{path}:/content | Upload to a specific drive |
| GET | /sites/{sitePath}:/drives | List drives for a SharePoint site |

## Known SharePoint Drive IDs

| Site | Drive ID |
|------|----------|
| All Company | `b!PMw4hWM4GkqxxjNxV6MCPdvAbeoHQN1MjSDuN9tmbW8XWDbGGaPcSa9cXkAmP_-0` |

## List Files in Root

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root/children" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data['value']:
    kind = 'folder' if 'folder' in item else 'file'
    size = item.get('size', 0)
    name = item['name']
    modified = item.get('lastModifiedDateTime', '')[:16]
    print(f\"[{kind:6s}] {size:>12,} bytes  {modified}  {name}\")
"
```

## List Files in Subfolder

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/Documents/Reports:/children" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data['value']:
    kind = 'folder' if 'folder' in item else 'file'
    print(f\"[{kind}] {item['name']}  ({item.get('size', 0):,} bytes)\")
"
```

## Upload Small File (< 4MB)

**IMPORTANT:** Use `curl` with an access token, NOT `m365 request --filePath`. The `m365 request` with `--filePath` and PUT returns empty output for binary files.

```bash
TOKEN=$(m365 util accesstoken get --resource https://graph.microsoft.com)
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/local/file.pdf \
  "https://graph.microsoft.com/v1.0/me/drive/root:/Documents/file.pdf:/content" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Uploaded: {data['name']} ({data['size']:,} bytes)\")
print(f\"ID: {data['id']}\")
print(f\"Web URL: {data['webUrl']}\")
"
```

## Upload Text Content

For text-based content, `m365 request --body` works fine:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/Documents/notes.txt:/content" --method put --body "These are my notes" --content-type "text/plain"
```

## Upload Large File (> 4MB)

Use a resumable upload session:

### Step 1: Create upload session

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/Documents/large-file.zip:/createUploadSession" --method post --body '{"item":{"@microsoft.graph.conflictBehavior":"rename"}}' --content-type "application/json"
```

This returns an `uploadUrl` in the response.

### Step 2: Upload chunks with curl

```bash
TOKEN=$(m365 util accesstoken get --resource https://graph.microsoft.com)
FILE_PATH="/path/to/large-file.zip"
UPLOAD_URL="UPLOAD_URL_FROM_STEP_1"
FILE_SIZE=$(stat -f%z "$FILE_PATH")

curl -s -X PUT \
  -H "Content-Range: bytes 0-$((FILE_SIZE - 1))/$FILE_SIZE" \
  -H "Content-Length: $FILE_SIZE" \
  --data-binary @"$FILE_PATH" \
  "$UPLOAD_URL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Uploaded: {data.get('name', 'unknown')} ({data.get('size', 0):,} bytes)\")
print(f\"ID: {data.get('id', 'N/A')}\")
"
```

For very large files, split into 10MB chunks and send multiple PUT requests with appropriate `Content-Range` headers.

## Upload to SharePoint

### Step 1: Get the drive ID for the SharePoint site

```bash
m365 request --url "https://graph.microsoft.com/v1.0/sites/gnarlysoft.sharepoint.com:/sites/AllCompany:/drives" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data['value']:
    print(f\"{d['name']}  ID: {d['id']}\")
"
```

### Step 2: Upload via the drive ID

```bash
TOKEN=$(m365 util accesstoken get --resource https://graph.microsoft.com)
DRIVE_ID="b!PMw4hWM4GkqxxjNxV6MCPdvAbeoHQN1MjSDuN9tmbW8XWDbGGaPcSa9cXkAmP_-0"
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/file.pdf \
  "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/root:/General/file.pdf:/content" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Uploaded: {data['name']} ({data['size']:,} bytes)\")
print(f\"Web URL: {data['webUrl']}\")
"
```

## Create Sharing Link

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/items/ITEM_ID_HERE/createLink" --method post --body '{"type":"view","scope":"organization"}' --content-type "application/json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
link = data['link']
print(f\"Share URL: {link['webUrl']}\")
print(f\"Type: {link['type']}  Scope: {link['scope']}\")
"
```

| Type | Description |
|------|-------------|
| view | Read-only access |
| edit | Read-write access |

| Scope | Description |
|-------|-------------|
| organization | Anyone in the organization |
| anonymous | Anyone with the link (external sharing) |

For SharePoint files, use the drive-specific endpoint:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/drives/DRIVE_ID_HERE/items/ITEM_ID_HERE/createLink" --method post --body '{"type":"view","scope":"organization"}' --content-type "application/json"
```

## Download File

### Step 1: Get the download URL

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/items/ITEM_ID_HERE" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['@microsoft.graph.downloadUrl'])
"
```

### Step 2: Download with curl

```bash
curl -sL "DOWNLOAD_URL_HERE" -o /tmp/downloaded-file.pdf
```

Combined in one step:

```bash
DOWNLOAD_URL=$(m365 request --url "https://graph.microsoft.com/v1.0/me/drive/items/ITEM_ID_HERE" --method get | python3 -c "import sys, json; print(json.load(sys.stdin)['@microsoft.graph.downloadUrl'])")
curl -sL "$DOWNLOAD_URL" -o /tmp/downloaded-file.pdf
```

## Delete File

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/items/ITEM_ID_HERE" --method delete
```

**IMPORTANT:** Use `--method delete` (lowercase). Returns empty body on success (HTTP 204).

## Check Storage Quota

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
q = data['quota']
total = q['total']
used = q['used']
remaining = q['remaining']
pct = (used / total) * 100
print(f\"Total:     {total / (1024**3):,.2f} GB\")
print(f\"Used:      {used / (1024**3):,.2f} GB ({pct:.1f}%)\")
print(f\"Remaining: {remaining / (1024**3):,.2f} GB\")
"
```

## List SharePoint Sites

Use the SPO command (works reliably, unlike `m365 teams team list`):

```bash
m365 spo site list --output json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data:
    print(f\"{s['Title']:40s}  {s['Url']}\")
"
```

**IMPORTANT:** Do NOT use `m365 request --url ".../sites?\$search=keyword"` for searching SharePoint sites — it requires `Sites.Read.All` permission. Use `m365 spo site list` instead.

## Full Workflow: Upload to SharePoint + Sharing Link

```bash
TOKEN=$(m365 util accesstoken get --resource https://graph.microsoft.com)
DRIVE_ID="b!PMw4hWM4GkqxxjNxV6MCPdvAbeoHQN1MjSDuN9tmbW8XWDbGGaPcSa9cXkAmP_-0"
FILE_PATH="/path/to/report.pdf"
REMOTE_PATH="General/Reports/report.pdf"

UPLOAD_RESULT=$(curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"$FILE_PATH" \
  "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/root:/$REMOTE_PATH:/content")

ITEM_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

m365 request --url "https://graph.microsoft.com/v1.0/drives/$DRIVE_ID/items/$ITEM_ID/createLink" --method post --body '{"type":"view","scope":"organization"}' --content-type "application/json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Share URL: {data['link']['webUrl']}\")
"
```

## Important Caveats

| Issue | Details |
|-------|---------|
| `m365 request --filePath` with PUT | Returns empty output for binary files — use `curl` with access token instead |
| Graph API sites `$search` | Requires `Sites.Read.All` permission — use `m365 spo site list` instead |
| File paths with spaces | URL-encode spaces as `%20` in Graph API paths |
| Conflict behavior | Use `@microsoft.graph.conflictBehavior` in upload session body: `rename`, `replace`, or `fail` |
| SharePoint drive discovery | Get drive ID via `/sites/{sitePath}:/drives` before uploading to SharePoint |
