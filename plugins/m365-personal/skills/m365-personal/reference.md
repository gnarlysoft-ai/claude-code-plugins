# M365 Query - Graph API Reference

## Graph API Base URL

`https://graph.microsoft.com/v1.0/`

---

## Outlook / Mail Endpoints

### Messages

| Endpoint | Description |
|----------|-------------|
| `GET /me/messages` | All messages across all folders |
| `GET /me/mailFolders/{folder}/messages` | Messages in a specific folder |
| `GET /me/messages/{id}` | Single message by ID |
| `GET /me/mailFolders` | List all mail folders |

### Supported OData Query Params (via `m365 request`)

| Param | Example | Notes |
|-------|---------|-------|
| `$top` | `$top=20` | Max messages to return |
| `$orderby` | `$orderby=receivedDateTime desc` | Sort order |
| `$filter` | `$filter=isRead eq false` | Filter expression |
| `$skip` | `$skip=20` | Pagination offset |
| `$select` | **DO NOT USE** | Causes 400 errors with `m365 request` |

### Filter Examples

```
# Unread only
$filter=isRead eq false

# From specific sender
$filter=from/emailAddress/address eq 'user@example.com'

# Subject contains
$filter=contains(subject,'meeting')

# Date range (combine with $orderby)
$filter=receivedDateTime ge 2026-02-01T00:00:00Z and receivedDateTime le 2026-02-18T23:59:59Z

# Has attachments
$filter=hasAttachments eq true
```

### Message Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique message ID |
| `subject` | string | Email subject |
| `receivedDateTime` | ISO 8601 | When received |
| `sentDateTime` | ISO 8601 | When sent |
| `from` | object | `{emailAddress: {name, address}}` |
| `toRecipients` | array | List of `{emailAddress: {name, address}}` |
| `body` | object | `{contentType: "html"/"text", content: "..."}` |
| `isRead` | bool | Read status |
| `hasAttachments` | bool | Has file attachments |
| `importance` | string | `low`, `normal`, `high` |
| `conversationId` | string | Thread conversation ID |

### Mail Folder Names (use with `--folderName`)

| Folder Name | Description |
|-------------|-------------|
| `Inbox` | Primary inbox |
| `Sent Items` | Sent messages |
| `Drafts` | Draft messages |
| `Deleted Items` | Trash |
| `Junk Email` | Spam folder |
| `Archive` | Archived messages |

---

## Calendar Endpoints

Accessed via `m365 request` (no dedicated CLI commands).

| Endpoint | Description |
|----------|-------------|
| `GET /me/calendarView?startDateTime=...&endDateTime=...` | Events in date range (expands recurring) |
| `GET /me/events` | All events (no recurring expansion) |
| `GET /me/events/{id}` | Single event by ID |
| `GET /me/calendars` | List all calendars |
| `GET /me/calendars/{id}/events` | Events from a specific calendar |

### Event Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique event ID |
| `subject` | string | Event title |
| `start` | object | `{dateTime, timeZone}` (UTC) |
| `end` | object | `{dateTime, timeZone}` (UTC) |
| `isAllDay` | bool | All-day event flag |
| `location` | object | `{displayName, locationType}` |
| `organizer` | object | `{emailAddress: {name, address}}` |
| `attendees` | array | List of `{emailAddress, type, status}` |
| `body` | object | `{contentType, content}` |
| `webLink` | string | URL to open in Outlook |

### Notes
- Use `calendarView` (not `events`) for date-range queries — it expands recurring events
- `startDateTime` and `endDateTime` are required for `calendarView`
- All datetimes are UTC — convert for display
- `$select` works on calendar endpoints (unlike mail)

---

## Teams / Chat Endpoints

### Chats

| Endpoint | Description |
|----------|-------------|
| `GET /me/chats` | All chats for current user |
| `GET /chats/{chatId}` | Specific chat info |
| `GET /chats/{chatId}/messages` | Messages in a chat |
| `GET /chats/{chatId}/messages/{messageId}` | Single message |
| `GET /chats/{chatId}/members` | Chat members |

### Chat Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Chat ID (e.g., `19:...@thread.v2`) |
| `topic` | string | Chat topic/name (may be null for 1:1) |
| `chatType` | string | `oneOnOne`, `group`, `meeting` |
| `createdDateTime` | ISO 8601 | Chat creation time |
| `lastUpdatedDateTime` | ISO 8601 | Last activity |
| `members` | array | Chat participants (when expanded) |

### Chat Message Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Message ID |
| `createdDateTime` | ISO 8601 | When sent |
| `lastModifiedDateTime` | ISO 8601 | Last edit time |
| `from` | object | `{user: {displayName, id}}` |
| `body` | object | `{contentType: "html"/"text", content: "..."}` |
| `messageType` | string | `message`, `systemEventMessage` |
| `deletedDateTime` | ISO 8601 | If deleted (null otherwise) |
| `attachments` | array | File/card attachments |

### Chat Message Query Params

| Param | Example | Notes |
|-------|---------|-------|
| `$top` | `$top=50` | Max messages (API max: 50 per page) |
| `$orderby` | Not supported on /messages | Cannot sort chat messages via OData |
| `$skipToken` | For pagination | Use `@odata.nextLink` from response |

**Note:** Chat messages always return in descending order (newest first). Use `reversed()` in Python to display chronologically.

### Pagination for Chat Messages

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"

# First page
RESPONSE=$(m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages?\$top=50")

# Check for next page
NEXT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('@odata.nextLink',''))")

# Fetch next page if exists
if [[ -n "$NEXT" ]]; then
  m365 request --url "$NEXT"
fi
```

---

## Known Chat IDs

| Name | Chat ID | Type |
|------|---------|------|
| 404 Team | `19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2` | Group |

To discover other chat IDs, run:
```bash
m365 teams chat list --output json | python3 -c "
import sys, json
chats = json.load(sys.stdin)
for c in chats:
    print(f\"{c.get('id',''):<65} {c.get('topic') or c.get('chatType','')}\")
"
```

---

## Teams Meeting & Transcript Endpoints

### Meetings

| Endpoint | Description |
|----------|-------------|
| `GET /me/onlineMeetings` | List online meetings (requires `startDateTime`) |
| `GET /me/onlineMeetings/{meeting-id}` | Get specific meeting details |

### Meeting Transcripts

| Endpoint | Description |
|----------|-------------|
| `GET /me/onlineMeetings/{meeting-id}/transcripts` | List all transcripts for a meeting |
| `GET /me/onlineMeetings/{meeting-id}/transcripts/{transcript-id}` | Get transcript metadata |
| `GET /me/onlineMeetings/{meeting-id}/transcripts/{transcript-id}/content` | Download transcript content (VTT) |

### m365 CLI Meeting Commands

```bash
# List meetings in a date range
m365 teams meeting list --startDateTime "2026-03-01T00:00:00Z" --output json

# List transcripts for a meeting
m365 teams meeting transcript list --meetingId "<meeting-id>" --output json

# Download transcript as VTT file
m365 teams meeting transcript get --meetingId "<meeting-id>" --id "<transcript-id>" --outputFile /tmp/transcript.vtt
```

### Meeting Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Meeting ID (base64-encoded) |
| `subject` | string | Meeting title |
| `startDateTime` | ISO 8601 | Scheduled start |
| `endDateTime` | ISO 8601 | Scheduled end |
| `allowTranscription` | bool | Whether transcription is enabled |
| `recordAutomatically` | bool | Auto-record setting |
| `joinWebUrl` | string | Meeting join URL |
| `participants` | object | Organizer and attendees |

### Transcript Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Transcript ID |
| `meetingId` | string | Parent meeting ID |
| `createdDateTime` | ISO 8601 | Transcript start time |
| `endDateTime` | ISO 8601 | Transcript end time |
| `transcriptContentUrl` | string | Direct Graph API URL for content |

---

## m365 CLI Commands Reference

### Outlook Commands

```bash
# List messages (CORRECT path — no 'mail' in command)
m365 outlook message list --folderName Inbox --output json
m365 outlook message list --folderName "Sent Items" --output json
m365 outlook message list --folderName Inbox \
  --startTime "2026-02-01T00:00:00Z" \
  --endTime "2026-02-18T23:59:59Z" \
  --output json

# Get single message
m365 outlook message get --id <messageId> --output json
```

### Teams Chat Commands

```bash
# List all chats
m365 teams chat list --output json

# Get chat details
m365 teams chat get --id <chatId> --output json

# List chat members
m365 teams chat member list --chatId <chatId> --output json

# List messages (NO --top option; use m365 request instead for large chats)
m365 teams chat message list --chatId <chatId> --output json
```

### Generic Graph Request

```bash
# GET
m365 request --url "https://graph.microsoft.com/v1.0/<path>"

# POST
m365 request --url "https://graph.microsoft.com/v1.0/<path>" \
  --method POST \
  --body '{"key": "value"}'
```

---

## Python Helpers

### Strip HTML from message body

```python
import re

def strip_html(html: str) -> str:
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()
```

### Date helpers

```python
from datetime import datetime, timedelta, timezone

# Current time in UTC ISO 8601
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# N days ago
n_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

# Parse Graph API datetime to readable format
def fmt_dt(dt_str):
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d %H:%M')
```

### Full email display

```python
import sys, json, re

data = json.load(sys.stdin)
msgs = data if isinstance(data, list) else data.get('value', [])

for m in msgs:
    sender_addr = m.get('from', {}).get('emailAddress', {}).get('address', '')
    sender_name = m.get('from', {}).get('emailAddress', {}).get('name', '')
    date = m.get('receivedDateTime', '')[:16].replace('T', ' ')
    subject = m.get('subject', '(no subject)')
    msg_id = m.get('id', '')
    is_read = m.get('isRead', True)
    unread_marker = '[UNREAD] ' if not is_read else ''

    print(f"{unread_marker}[{date}] {sender_name} <{sender_addr}>")
    print(f"  Subject: {subject}")
    print(f"  ID: {msg_id}")
    print()
```

---

## Authentication Details

| Field | Value |
|-------|-------|
| App Name | Gnarlysoft-Delegated-CLI |
| App ID | `2dbdde76-d0f3-4aa2-8af6-391a66867742` |
| Tenant ID | `f64ae4c4-b8e2-453a-97bb-8e73450aed49` |
| Auth Type | Device Code |
| Account | `marcos@gnarlysoft.com` |

### Login command (full)

```bash
m365 login \
  --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

### Check current session

```bash
m365 status
```

Output shows: logged in / not logged in, account name, auth type.
