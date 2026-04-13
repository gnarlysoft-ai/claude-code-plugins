---
name: "gnarlysoft:m365-personal"
description: Query your personal Microsoft 365 data — read your own Outlook inbox, sent items, folders, and messages; view your calendar events, meetings, and availability; list and read your Teams chats, messages, and conversations; check and set your presence status; fetch and download meeting transcripts; upload, download, and share files on OneDrive and SharePoint — using the CLI for Microsoft 365 (m365) tool and direct Graph API calls. Use this skill for personal M365 use (reading your own inbox, calendar, Teams chats, presence, meeting transcripts, OneDrive/SharePoint files), not for org-wide or admin management tasks.
allowed-tools: Bash, Read
---

# Microsoft 365 Query Skill

<context>
This skill queries Microsoft 365 data using the `m365` CLI (v11.4.0, `@pnp/cli-microsoft365`) and direct Microsoft Graph API calls via `m365 request`. Authentication is managed by the m365 CLI itself — no API token files needed.

**Authenticated account:** Run `m365 status` to verify
**App:** Gnarlysoft-Delegated-CLI (App ID: `2dbdde76-d0f3-4aa2-8af6-391a66867742`)
**Tenant:** `f64ae4c4-b8e2-453a-97bb-8e73450aed49`
**Permissions:** `User.Read`, `Mail.Read`, `Mail.ReadBasic`, `Mail.ReadWrite`, `Chat.Read`, `ChannelMessage.Read.All`, `Team.ReadBasic.All`, `Presence.ReadWrite`, `OnlineMeetings.Read`, `OnlineMeetingTranscript.Read.All`, `Files.ReadWrite.All`
</context>

## First-Time Setup

Before running any query, ALWAYS check `m365 status` first. If not logged in, guide the user through the setup steps below.

### 1. Check m365 CLI installation

```bash
which m365
```

If the command is not found, instruct the user to install it:

```bash
npm install -g @pnp/cli-microsoft365
```

### 2. Check login status and authenticate

```bash
m365 status
```

If not logged in, authenticate using the shared Azure AD app (Gnarlysoft-Delegated-CLI):

```bash
m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

The CLI will display a device code and a URL. Instruct the user to open the URL in their browser and enter the code to complete authentication.

### 3. Discover your Teams chat IDs

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/chats?\$expand=members&\$top=50" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('value', []):
    members = [m.get('displayName','') for m in c.get('members', [])]
    topic = c.get('topic') or ', '.join(members)
    print(f\"{c.get('id',''):<60} | {topic}\")
"
```

### 4. (Optional) Presence consent

If you need presence features, consent manually via this URL then re-login with `m365 login --authType browser`:
```
https://login.microsoftonline.com/f64ae4c4-b8e2-453a-97bb-8e73450aed49/oauth2/v2.0/authorize?client_id=2dbdde76-d0f3-4aa2-8af6-391a66867742&response_type=code&redirect_uri=http://localhost&scope=https://graph.microsoft.com/Presence.ReadWrite+offline_access&prompt=consent
```

---

<instructions>

## Authentication

```bash
m365 status
```

Re-authenticate if needed:

```bash
m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

---

## Outlook Email

**Correct command path:** `m365 outlook message list` (NOT `m365 outlook mail message list`)

### List messages

```bash
m365 outlook message list --folderName Inbox --output json
m365 outlook message list --folderName "Sent Items" --output json
m365 outlook message list --folderName Inbox \
  --startTime "2026-02-01T00:00:00Z" \
  --endTime "2026-02-18T23:59:59Z" \
  --output json
```

### Parse and display email list

```bash
m365 outlook message list --folderName Inbox --output json | python3 -c "
import sys, json
msgs = json.load(sys.stdin)
for m in msgs:
    print(f\"[{m.get('receivedDateTime','')[:10]}] From: {m.get('from',{}).get('emailAddress',{}).get('address','')} | Subject: {m.get('subject','')} | ID: {m.get('id','')}\")
"
```

### Get a specific message (with body)

```bash
MESSAGE_ID="your_message_id_here"
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/${MESSAGE_ID}" | python3 -c "
import sys, json, re
msg = json.load(sys.stdin)
body = msg.get('body', {}).get('content', '')
body_clean = re.sub(r'<[^>]+>', '', body).strip()
body_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', body_clean)
print(f\"Subject: {msg.get('subject')}\")
print(f\"From: {msg.get('from', {}).get('emailAddress', {}).get('address')}\")
print(f\"Date: {msg.get('receivedDateTime')}\")
print(f\"---\")
print(body_clean[:3000])
"
```

### List messages via Graph API (more control)

Use `m365 request` for `$top`, `$orderby`, `$filter`. Do NOT use `$select` — it causes 400 errors.

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$top=20&\$orderby=receivedDateTime desc" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"[{m.get('receivedDateTime','')[:10]}] {m.get('from',{}).get('emailAddress',{}).get('address','')} | {m.get('subject','')}\")
"
```

### Delete an email

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/{id}" --method delete
```

**IMPORTANT:** Use lowercase `--method delete`, not `--method DELETE`.

### List mail folders

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('value', []):
    print(f\"{f.get('displayName',''):<30} id={f.get('id','')} unread={f.get('unreadItemCount',0)}\")
"
```

---

## Outlook Calendar

Calendar is accessed via direct Graph API requests (no dedicated m365 CLI commands).

### List upcoming events (calendarView)

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=2026-02-19T00:00:00Z&endDateTime=2026-02-26T00:00:00Z&\$orderby=start/dateTime&\$select=subject,start,end,location,isAllDay" --accept "application/json" --output json
```

### Get a single event

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/events/{event-id}?\$select=subject,start,end,body,attendees,location" --accept "application/json" --output json
```

### Key notes
- All datetime values are in UTC — convert to user's timezone for display
- Use `calendarView` (not `events`) for date-range queries as it expands recurring events
- Escape `$` in OData params with `\$` in bash

---

## Microsoft Teams

### List chats

```bash
m365 teams chat list --output json | python3 -c "
import sys, json
chats = json.load(sys.stdin)
for c in chats:
    topic = c.get('topic') or c.get('chatType','')
    print(f\"{c.get('id',''):<60} | {topic}\")
"
```

### Known chat IDs

| Chat | ID |
|------|----|
| 404 Team | `19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2` |

### List messages in a chat (via Graph API — preferred)

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages?\$top=20" | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
msgs = data.get('value', [])
for m in reversed(msgs):
    sender = m.get('from', {}) or {}
    user = (sender.get('user') or {}).get('displayName', 'unknown')
    created = m.get('createdDateTime', '')[:16].replace('T', ' ')
    body = (m.get('body') or {}).get('content', '')
    body_clean = re.sub(r'<[^>]+>', '', body).strip()
    if body_clean:
        print(f\"[{created}] {user}: {body_clean[:200]}\")
"
```

### Send a message

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages" \
  --method post \
  --body '{"body":{"content":"your message here"}}' \
  --content-type "application/json"
```

Use lowercase `post` for `--method` and always include `--content-type "application/json"`.

> **Note:** Deleting chat messages via the Graph API is not supported (softDelete returns 405, DELETE returns 404).

### Edit a chat message

Use PATCH. Returns empty string `""` on success (204 No Content — not an error).

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
MESSAGE_ID="1775064322404"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages/${MESSAGE_ID}" \
  --method patch \
  --body '{"body":{"contentType":"html","content":"Updated message content"}}' \
  --content-type "application/json"
```

For @mentions workflow, see [examples.md](examples.md).

---

## Teams Meeting Transcripts

### List recent meetings

```bash
m365 teams meeting list --startDateTime "2026-03-24T00:00:00Z" --output json
```

### List transcripts for a meeting

```bash
MEETING_ID="<meeting-id>"
m365 teams meeting transcript list --meetingId "$MEETING_ID" --output json
```

### Download a transcript

```bash
MEETING_ID="<meeting-id>"
TRANSCRIPT_ID="<transcript-id>"
m365 teams meeting transcript get \
  --meetingId "$MEETING_ID" \
  --id "$TRANSCRIPT_ID" \
  --outputFile /tmp/meeting-transcript.vtt
```

The VTT file contains timestamped, speaker-labeled entries (`<v Speaker Name>text</v>`). Any meeting attendee with permissions can fetch transcripts, not just the organizer.

For parsing VTT and full transcript workflows, see [examples.md](examples.md).

---

## Teams Presence

### Read current presence

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence"
```

### Set presence — USE setUserPreferredPresence

**IMPORTANT:** Use `setUserPreferredPresence` (beta API), NOT `setPresence`. The per-session endpoint gets overridden by the Teams client.

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/setUserPreferredPresence" \
  --method post \
  --body '{"availability":"Available","activity":"Available"}' \
  --content-type "application/json"
```

- `availability`: `Available`, `Busy`, `DoNotDisturb`, `Away`, `BeRightBack`, `Offline`
- `activity`: `Available`, `InACall`, `InAMeeting`, `Busy`, `Away`, `BeRightBack`, `DoNotDisturb`, `Offline`, `OffWork`
- `expirationDuration` (optional): ISO 8601 duration (e.g., `PT1H`). Omit to keep indefinitely.

### Clear presence (reset to automatic)

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/clearUserPreferredPresence" \
  --method post \
  --body '{}' \
  --content-type "application/json"
```

### Set / clear status message

```bash
# Set
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/setStatusMessage" \
  --method post \
  --body '{"statusMessage":{"message":{"content":"Your message here","contentType":"text"},"expiryDateTime":{"dateTime":"2026-02-28T23:59:59.9999999","timeZone":"UTC"}}}' \
  --content-type "application/json"

# Clear
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/setStatusMessage" \
  --method post \
  --body '{"statusMessage":{"message":{"content":"","contentType":"text"}}}' \
  --content-type "application/json"
```

---

## OneDrive & SharePoint Files

### List files

```bash
# OneDrive root
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root/children" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('value', []):
    ftype = 'folder' if 'folder' in f else 'file'
    size = f.get('size', 0)
    print(f\"[{ftype}] {f.get('name',''):<40} {size:>10} bytes | {f.get('id','')}\")
"

# Subfolder
FOLDER_PATH="Documents/MyFolder"
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${FOLDER_PATH}:/children"
```

### Upload a file (< 4MB)

For binary files, use curl with an access token:

```bash
FILE_PATH="/path/to/local/file.pdf"
DEST_PATH="Shared-Files/file.pdf"
ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)

curl -s -X PUT "https://graph.microsoft.com/v1.0/me/drive/root:/${DEST_PATH}:/content" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"${FILE_PATH}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Uploaded: {data.get('name')}\")
print(f\"Size: {data.get('size')} bytes\")
print(f\"Web URL: {data.get('webUrl')}\")
"
```

For plain text, `m365 request --body` works:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${DEST_PATH}:/content" \
  --method put \
  --body "text content here" \
  --content-type "text/plain"
```

For large files (> 4MB) and SharePoint uploads, see [examples.md](examples.md).

### Upload to SharePoint

Get the drive ID first, then use the same curl pattern with `/drives/{driveId}/root:/{path}:/content`.

```bash
SITE_PATH="gnarlysoft.sharepoint.com:/sites/allcompany"
m365 request --url "https://graph.microsoft.com/v1.0/sites/${SITE_PATH}:/drives" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data.get('value', []):
    print(f\"Name: {d.get('name'):<20} | ID: {d.get('id')} | Type: {d.get('driveType')}\")
"
```

### Known SharePoint site drive IDs

| Site | Drive ID |
|------|----------|
| All Company (Documents) | `b!PMw4hWM4GkqxxjNxV6MCPdvAbeoHQN1MjSDuN9tmbW8XWDbGGaPcSa9cXkAmP_-0` |

### Create a sharing link

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${FILE_PATH}:/createLink" \
  --method post \
  --body '{"type":"view","scope":"organization"}' \
  --content-type "application/json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
link = data.get('link', {})
print(f\"Link: {link.get('webUrl')}\")
"
```

Link types: `view` (read-only), `edit` (read-write). Scope: `organization` (tenant), `anonymous` (public).

### Download / Delete files

```bash
# Download
DOWNLOAD_URL=$(m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${FILE_PATH}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('@microsoft.graph.downloadUrl', ''))
")
curl -sL "${DOWNLOAD_URL}" -o /tmp/downloaded-file

# Delete
m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${FILE_PATH}" --method delete
```

### List SharePoint sites

```bash
m365 spo site list --output json | python3 -c "
import sys, json
sites = json.load(sys.stdin)
for s in sites:
    print(f\"{s.get('Title',''):<40} | {s.get('Url','')}\")
"
```

---

## Supporting Files

For API endpoint reference and field schemas, see [reference.md](reference.md).
For common workflow examples (search, @mentions, transcripts, SharePoint uploads), see [examples.md](examples.md).
For error handling, commands to avoid, clipboard workflows, and Graph API tips, see [advanced.md](advanced.md).

---

## Failure Notification (MANDATORY)

If any step, command, API call, or tool in this workflow fails or does not work as expected, you MUST immediately notify the user with:
1. What failed
2. The error or unexpected behavior observed
3. What you plan to do instead (if anything)

Do NOT silently fall back to alternative approaches without informing the user first.

---

## Self-Update Protocol

If you discovered something new during this task (failures, bugs, edge cases, better approaches, new IDs or mappings), update this SKILL.md file directly without waiting for the user to ask. Skip if the task was routine with no new findings.

</instructions>
