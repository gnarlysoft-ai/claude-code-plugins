---
name: m365-personal
description: Query your personal Microsoft 365 data — read your own Outlook inbox, sent items, folders, and messages; view your calendar events, meetings, and availability; list and read your Teams chats, messages, and conversations; check and set your presence status — using the CLI for Microsoft 365 (m365) tool and direct Graph API calls. Use this skill for personal M365 use (reading your own inbox, calendar, Teams chats, presence), not for org-wide or admin management tasks.
allowed-tools: Bash, Read
---

# Microsoft 365 Query Skill

<context>
This skill queries Microsoft 365 data using the `m365` CLI (v11.4.0, `@pnp/cli-microsoft365`) and direct Microsoft Graph API calls via `m365 request`. Authentication is managed by the m365 CLI itself — no API token files needed.

**Authenticated account:** Run `m365 status` to verify
**App:** Gnarlysoft-Delegated-CLI (App ID: `2dbdde76-d0f3-4aa2-8af6-391a66867742`)
**Tenant:** `f64ae4c4-b8e2-453a-97bb-8e73450aed49`
**Permissions:** `User.Read`, `Mail.Read`, `Mail.ReadBasic`, `Mail.ReadWrite`, `Chat.Read`, `ChannelMessage.Read.All`, `Team.ReadBasic.All`, `Presence.ReadWrite`
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

After login, run `m365 status` again to confirm the authenticated account.

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

Update the "Known chat IDs" table in this file with the chat IDs relevant to you.

### 4. (Optional) Presence consent

If you need presence features (read/set status), the m365 CLI does not automatically request the `Presence.ReadWrite` scope. You must consent manually:

1. Open this URL in your browser (replace `{tenant-id}` and `{app-id}` with the values from the context block above):
   ```
   https://login.microsoftonline.com/f64ae4c4-b8e2-453a-97bb-8e73450aed49/oauth2/v2.0/authorize?client_id=2dbdde76-d0f3-4aa2-8af6-391a66867742&response_type=code&redirect_uri=http://localhost&scope=https://graph.microsoft.com/Presence.ReadWrite+offline_access&prompt=consent
   ```
2. After consenting, logout and re-login with `m365 login --authType browser` to get a fresh token with the scope included.

---

<instructions>

## Authentication

### Check login status
```bash
m365 status
```

### Re-authenticate if needed
```bash
m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

The session persists between terminal sessions. Always check `m365 status` before running queries if there is any doubt.

---

## Outlook Email

### List messages from a folder

**Correct command path:** `m365 outlook message list` (NOT `m365 outlook mail message list`)

```bash
# List inbox (default output)
m365 outlook message list --folderName Inbox --output json

# List sent items
m365 outlook message list --folderName "Sent Items" --output json

# Filter by date range (ISO 8601)
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

Use the Graph API escape hatch to fetch full message content:

```bash
MESSAGE_ID="your_message_id_here"
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/${MESSAGE_ID}" | python3 -c "
import sys, json, re
msg = json.load(sys.stdin)
body = msg.get('body', {}).get('content', '')
# Strip HTML tags
body_clean = re.sub(r'<[^>]+>', '', body).strip()
# Collapse whitespace
body_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', body_clean)
print(f\"Subject: {msg.get('subject')}\")
print(f\"From: {msg.get('from', {}).get('emailAddress', {}).get('address')}\")
print(f\"Date: {msg.get('receivedDateTime')}\")
print(f\"---\")
print(body_clean[:3000])
"
```

### List messages via Graph API (more control)

Use `m365 request` for query params like `$top`, `$orderby`, `$filter`. Do NOT use `$select` — it can cause 400 errors.

```bash
# Get latest 20 inbox messages ordered by date
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$top=20&\$orderby=receivedDateTime desc" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"[{m.get('receivedDateTime','')[:10]}] {m.get('from',{}).get('emailAddress',{}).get('address','')} | {m.get('subject','')}\")
"

# Filter messages from a specific sender
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$filter=from/emailAddress/address eq 'someone@example.com'&\$top=10"

# Get messages from a specific folder using folder path
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?\$top=20&\$orderby=receivedDateTime desc"
```

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

Calendar is accessed via direct Graph API requests (no dedicated m365 CLI commands exist).

### List upcoming events (calendarView)

```bash
# Events for a date range (required: startDateTime and endDateTime)
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=2026-02-19T00:00:00Z&endDateTime=2026-02-26T00:00:00Z&\$orderby=start/dateTime&\$select=subject,start,end,location,isAllDay" --accept "application/json" --output json
```

### Useful query parameters

- `$select=subject,start,end,location,isAllDay,organizer,attendees` — pick fields
- `$orderby=start/dateTime` — sort chronologically
- `$filter=isAllDay eq false` — exclude all-day events
- `$top=10` — limit results

### Get a single event

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/events/{event-id}?\$select=subject,start,end,body,attendees,location" --accept "application/json" --output json
```

### List calendars

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendars?\$select=name,id" --accept "application/json" --output json
```

### Key notes
- All datetime values are in UTC — convert to user's timezone for display
- Use `calendarView` (not `events`) for date-range queries as it expands recurring events
- Escape `$` in OData params with `\$` in bash

---

## Microsoft Teams

### List Teams chats

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

### List messages in a chat (via Graph API — preferred over m365 teams chat message list)

The native `m365 teams chat message list` has no `--top` option and is slow. Use Graph API directly:

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

### Send a message to a chat

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages" \
  --method post \
  --body '{"body":{"content":"your message here"}}' \
  --content-type "application/json"
```

**Important:** Use lowercase `post` for `--method` and always include `--content-type "application/json"`.

> **Note:** Deleting chat messages via the Graph API is not supported (softDelete returns 405, DELETE returns 404). Messages must be deleted manually in the Teams app.

### Read a specific chat message

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
MESSAGE_ID="your_message_id"

m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages/${MESSAGE_ID}" | python3 -c "
import sys, json, re
m = json.load(sys.stdin)
sender = (m.get('from') or {}).get('user', {}) or {}
body = re.sub(r'<[^>]+>', '', (m.get('body') or {}).get('content', '')).strip()
print(f\"From: {sender.get('displayName','unknown')}\")
print(f\"Date: {m.get('createdDateTime','')}\")
print(body)
"
```

### Get chat info (members, topic)

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}?expand=members"
```

### List all chats with member info

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/chats?\$expand=members&\$top=20" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('value', []):
    members = [m.get('displayName','') for m in c.get('members', [])]
    topic = c.get('topic') or ', '.join(members)
    print(f\"{c.get('id',''):<60} | {topic}\")
"
```

---

## Teams Presence

### Required Permission
- `Presence.ReadWrite` (delegated, admin consent NOT required)
- If getting 403, the user needs to consent via OAuth URL:
  ```
  https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize?client_id={app-id}&response_type=code&redirect_uri=http://localhost&scope=https://graph.microsoft.com/Presence.ReadWrite+offline_access&prompt=consent
  ```
- After consenting, logout and re-login with `m365 login --authType browser` to get a fresh token with the scope included.
- Note: the m365 CLI does NOT request this scope automatically even if configured on the app registration. The manual OAuth consent URL is needed to trigger user consent.

### Read current presence

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence"
```

Returns: availability, activity, statusMessage, outOfOfficeSettings.

### Set presence (availability/activity) — USE setUserPreferredPresence

**IMPORTANT:** Use `setUserPreferredPresence` (beta API), NOT `setPresence`. The `setPresence` endpoint only sets a per-session presence that gets overridden by the Teams client status. `setUserPreferredPresence` sets the user-level preferred status which overrides all sessions.

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/setUserPreferredPresence" \
  --method post \
  --body '{"availability":"Available","activity":"Available"}' \
  --content-type "application/json"
```

- `availability`: `Available`, `Busy`, `DoNotDisturb`, `Away`, `BeRightBack`, `Offline`
- `activity`: `Available`, `InACall`, `InAMeeting`, `Busy`, `Away`, `BeRightBack`, `DoNotDisturb`, `Offline`, `OffWork`
- `expirationDuration` (optional): ISO 8601 duration (e.g., `PT1H` = 1 hour). Omit to keep indefinitely.
- No `sessionId` needed for this endpoint

#### Legacy per-session endpoint (usually NOT what you want)

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/setPresence" \
  --method post \
  --body '{"sessionId":"2dbdde76-d0f3-4aa2-8af6-391a66867742","availability":"Busy","activity":"InACall","expirationDuration":"PT1H"}' \
  --content-type "application/json"
```

### Clear presence (reset to automatic)

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/clearUserPreferredPresence" \
  --method post \
  --body '{}' \
  --content-type "application/json"
```

#### Legacy per-session clear

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/clearPresence" \
  --method post \
  --body '{"sessionId":"2dbdde76-d0f3-4aa2-8af6-391a66867742"}' \
  --content-type "application/json"
```

### Set status message

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/setStatusMessage" \
  --method post \
  --body '{"statusMessage":{"message":{"content":"Your message here","contentType":"text"},"expiryDateTime":{"dateTime":"2026-02-28T23:59:59.9999999","timeZone":"UTC"}}}' \
  --content-type "application/json"
```

### Clear status message

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence/setStatusMessage" \
  --method post \
  --body '{"statusMessage":{"message":{"content":"","contentType":"text"}}}' \
  --content-type "application/json"
```

---

## Generic Graph API Requests

Use `m365 request` as a general-purpose escape hatch for any Graph endpoint:

```bash
# GET request
m365 request --url "https://graph.microsoft.com/v1.0/me"

# POST request with body
m365 request --url "https://graph.microsoft.com/v1.0/me/messages" \
  --method POST \
  --body '{"subject": "test"}'
```

**Known caveats with `m365 request`:**
- `$select` param can cause 400 errors — omit it and filter fields in Python instead
- `$top`, `$orderby`, `$filter` all work correctly
- Escape `$` in shell with `\$` or use single quotes

---

## Output Formatting

### Strip HTML from message bodies

```python
import re
body_clean = re.sub(r'<[^>]+>', '', html_body).strip()
body_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', body_clean)
```

### Parse JSON output inline

```bash
m365 outlook message list --folderName Inbox --output json | python3 -m json.tool
```

### Extract specific fields with python3

```bash
m365 teams chat list --output json | python3 -c "
import sys, json
data = json.load(sys.stdin)
# data is a list for m365 commands, dict with 'value' for m365 request
items = data if isinstance(data, list) else data.get('value', [])
for item in items:
    print(json.dumps(item, indent=2))
" | head -50
```

---

## Copying Rich HTML to Clipboard (for Outlook)

Use `textutil` to convert HTML to RTF, then `pbcopy` to copy it. This preserves tables, bold, colors, and all formatting when pasted into Outlook.

**IMPORTANT:** Do NOT pipe raw HTML strings through `pbcopy` directly — Outlook will paste the HTML source code as plain text. You must convert to RTF first via `textutil`.

### Full workflow

**Step 1:** Write content as a proper HTML file with Outlook-compatible styling:

```html
<html>
<head>
<style>
body { font-family: Aptos, Arial, sans-serif; font-size: 11pt; color: #000000; }
p { margin: 0 0 10pt 0; }
ul { margin: 4pt 0 10pt 0; }
li { margin-bottom: 4pt; }
</style>
</head>
<body>
<p>Your content here with <b>bold</b>, lists, etc.</p>
</body>
</html>
```

**Key styling notes:**
- Use `Aptos, Arial, sans-serif` at `11pt` — Aptos is Outlook's current default font (replaced Calibri)
- Use `margin: 0 0 10pt 0` on `<p>` tags for proper paragraph spacing
- Use `<b>` for bold (renders correctly in Outlook)
- Use `<ul>/<li>` for bullet lists
- Use `&mdash;` for em dashes, `&quot;` for quotes

**Step 2:** Convert and copy to clipboard:

```bash
textutil -convert rtf -stdout /tmp/email.html | pbcopy
```

**Why not the `hexdump | xargs | osascript` approach?** That method breaks with larger HTML files due to `xargs` argument length limits. The `textutil` pipeline is simpler and handles any file size.

**Why not raw HTML via `pbcopy`?** Piping HTML directly into `pbcopy` (e.g., `echo "<b>text</b>" | pbcopy`) copies it as plain text. Outlook pastes the literal HTML tags instead of rendering them. The `textutil` RTF conversion is required for rich text formatting.

---

## Common Workflows

### Find emails from a sender in the last 7 days

```bash
SENDER="someone@example.com"
START=$(python3 -c "from datetime import datetime, timedelta; print((datetime.utcnow()-timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'))")

m365 outlook message list --folderName Inbox \
  --startTime "${START}" \
  --output json | python3 -c "
import sys, json
msgs = json.load(sys.stdin)
filtered = [m for m in msgs if '${SENDER}' in str(m.get('from', {}))]
for m in filtered:
    print(f\"[{m['receivedDateTime'][:10]}] {m['subject']}\")
    print(f\"  ID: {m['id']}\")
"
```

### Read latest N messages from a Teams chat

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
N=10

m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages?\$top=${N}&\$orderby=createdDateTime desc" | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
msgs = list(reversed(data.get('value', [])))
for m in msgs:
    user = ((m.get('from') or {}).get('user') or {}).get('displayName', 'unknown')
    ts = m.get('createdDateTime', '')[:16].replace('T', ' ')
    body = re.sub(r'<[^>]+>', '', (m.get('body') or {}).get('content', '')).strip()
    if body:
        print(f'[{ts}] {user}: {body[:300]}')
        print()
"
```

### List all unread emails

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$filter=isRead eq false&\$top=25&\$orderby=receivedDateTime desc" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"[{m.get('receivedDateTime','')[:10]}] {m.get('from',{}).get('emailAddress',{}).get('address','')} | {m.get('subject','')}\")
"
```

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `Not logged in` | Session expired | Run `m365 login` with deviceCode |
| `Access denied` | Missing permission | Check app permissions in Azure AD |
| `400 Bad Request` with `$select` | Graph API quirk | Remove `$select`, filter in Python |
| `Skype backend error` on `m365 teams team list` | Known m365 CLI bug | Do not use `m365 teams team list` — use Graph API directly |
| `m365 outlook mail message list` fails | Wrong command path | Use `m365 outlook message list` (no `mail` in path) |
| `m365 teams chat message list` — no `--top` | Missing option | Use `m365 request` with Graph API instead |
| `400 Bad Request` on DELETE with uppercase `DELETE` | m365 request only accepts lowercase methods | Use `--method delete` (lowercase), not `--method DELETE` |
| `400 Bad Request` when using `$search` with `$orderby` | Graph API does not allow `$orderby` alongside `$search` | Remove `$orderby` when using `$search`; results are returned by relevance by default |

---

## Commands to Avoid

- `m365 teams team list` — causes Skype backend error, always fails
- `m365 outlook mail message list` — wrong command path, does not exist
- `m365 teams chat message list` — works but has no `--top`; slow for large chats; prefer Graph API

For extended Graph API reference and additional endpoint patterns, see [reference.md](reference.md).

---

## Failure Notification (MANDATORY)

If any step, command, API call, or tool in this workflow fails or does not work as expected, you MUST immediately notify the user with:
1. What failed
2. The error or unexpected behavior observed
3. What you plan to do instead (if anything)

Do NOT silently fall back to alternative approaches without informing the user first.

---
## Self-Update Protocol

This skill should be updated when:
1. **New real-world usage patterns discovered** — e.g., successful workflows, workarounds, parameter combinations
2. **Known issues found** — e.g., commands that fail unexpectedly, error patterns
3. **New Graph API queries tested** — e.g., new filter combinations, pagination patterns
4. **Authentication edge cases** — e.g., session expiry, re-auth failures, permission issues
5. **Performance improvements** — e.g., faster query methods, better Python parsing

If you discover new information during a task (failures, new patterns, bugs, fixes), automatically update this SKILL.md file without waiting for the user to ask. Add findings to the appropriate section (Outlook Email, Microsoft Teams, Common Workflows, or Error Handling), including exact command syntax and any caveats. Skip if the task was routine with no new findings.

### Recent discoveries (Feb 18, 2026)

- **Search emails by name**: Use `m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$search=\"NAME\"&\$top=25"` to search across all message content (subject, body, from, to)
- **Search returns 25 results by default**: The `$search` parameter respects `$top` parameter for limiting results
- **Graph API search works reliably**: Unlike some m365 CLI native commands, the Graph API search endpoint works as expected
- **Sending chat messages works**: Use `m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages" --method post --body '{"body":{"content":"your message"}}' --content-type "application/json"`. Requires lowercase `post` for method and explicit `--content-type "application/json"`.
- **Deleting chat messages is NOT supported via API**: Both `softDelete` (405) and DELETE (404) fail. Messages can only be deleted from the Teams app UI.
- **Deleting emails works with `--method delete` (lowercase)**: `m365 request --url "https://graph.microsoft.com/v1.0/me/messages/{id}" --method delete` successfully deletes emails. Using uppercase `--method DELETE` returns a 400 error ("DELETE is not a valid value for method"). Always use lowercase method names with `m365 request`.
- **Mail.ReadWrite permission is available**: Email deletion works, confirming the app has `Mail.ReadWrite` permissions despite not being listed originally.
- **Presence.ReadWrite works after manual user consent**: The m365 CLI doesn't automatically request `Presence.ReadWrite` scope. Use the OAuth authorize URL with `prompt=consent` to trigger user consent, then re-login with `--authType browser`.
- **Set/clear presence and status messages**: All presence endpoints confirmed working: `/me/presence`, `/me/presence/setPresence`, `/me/presence/clearPresence`, `/me/presence/setStatusMessage`.
- **`$search` and `$orderby` cannot be combined**: Using both in the same Graph API request causes a 400 error. When using `$search`, omit `$orderby` entirely — search results are ranked by relevance automatically. Fails: `?\$search=\"keyword\"&\$top=10&\$orderby=receivedDateTime desc`. Works: `?\$search=\"keyword\"&\$top=10`.

</instructions>
