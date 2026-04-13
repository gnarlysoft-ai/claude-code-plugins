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

<instructions>

## Authentication

```bash
m365 status
```

If not logged in:

```bash
m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

If m365 CLI not installed: `npm install -g @pnp/cli-microsoft365`

The session persists between terminal sessions. Always check `m365 status` before running queries if there is any doubt.

### Adding new permissions (CRITICAL)

The m365 CLI does **NOT** automatically request new scopes even after they are added to the Azure AD app registration. A normal `m365 logout` + `m365 login` will reuse the previously consented scopes and the new permission will be missing from the token (resulting in 403 errors).

To add a new permission scope:

1. Add the permission to the app registration (Azure Portal or `az ad app permission add`)
2. **Force user consent** via direct OAuth URL (replace `{SCOPE}` with the Graph scope, e.g. `Files.ReadWrite.All`):
   ```bash
   open "https://login.microsoftonline.com/f64ae4c4-b8e2-453a-97bb-8e73450aed49/oauth2/v2.0/authorize?client_id=2dbdde76-d0f3-4aa2-8af6-391a66867742&response_type=code&redirect_uri=http://localhost&scope=https://graph.microsoft.com/{SCOPE}+offline_access&prompt=consent"
   ```
   The browser will show a consent prompt, then redirect to `localhost` which will fail with "connection refused" — **this is expected and means consent succeeded**.
3. **Then** re-login to get a token with the new scope:
   ```bash
   m365 logout
   m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
     --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
     --authType deviceCode
   ```
4. Verify the scope is present by decoding the token:
   ```bash
   ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)
   python3 -c "
   import base64, json
   token = '${ACCESS_TOKEN}'.split('.')[1]
   token += '=' * (4 - len(token) % 4)
   d = json.loads(base64.b64decode(token))
   print(d.get('scp', 'NO SCP'))
   "
   ```

**Without step 2, the new permission will NOT appear in the token regardless of how many times you re-login.**

---

## Domain Reference

Each domain has its own file with full endpoints, examples, and edge cases. Read the relevant file when working with that domain.

### Outlook Email → [email.md](email.md)

List, read, search, delete emails. Rich HTML clipboard copy for Outlook.

```bash
m365 outlook message list --folderName Inbox --output json
```

### Calendar → [calendar.md](calendar.md)

List events, check availability, view calendars.

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=2026-01-01T00:00:00Z&endDateTime=2026-01-07T00:00:00Z&\$orderby=start/dateTime" --accept "application/json" --output json
```

### Teams Chat & Presence → [teams.md](teams.md)

List/send/edit chat messages, @mentions, presence status.

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/chats?\$expand=members&\$top=20"
```

### Meeting Transcripts → [transcripts.md](transcripts.md)

List meetings, download transcripts, parse VTT.

```bash
m365 teams meeting list --startDateTime "2026-01-01T00:00:00Z" --output json
```

### OneDrive & SharePoint Files → [files.md](files.md)

Upload, download, share files. SharePoint site access.

```bash
ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)
curl -s -X PUT "https://graph.microsoft.com/v1.0/me/drive/root:/file.pdf:/content" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"/path/to/file.pdf"
```

---

## Global Caveats

| Caveat | Details |
|--------|---------|
| `$select` on mail endpoints | Causes 400 errors — omit and filter in Python |
| `$search` + `$orderby` | Cannot be combined — omit `$orderby` when searching |
| Method case | Always lowercase: `--method post`, `--method delete`, `--method patch` |
| Binary uploads | `m365 request --filePath` returns empty output — use `curl` with access token |
| `m365 teams team list` | Always fails (Skype backend error) — use Graph API |
| `m365 outlook mail message list` | Wrong path — use `m365 outlook message list` |
| `m365 teams chat message list` | No `--top` — use `m365 request` with Graph API |
| Delete chat messages | NOT supported via API (405/404) — must use Teams app |
| New permissions not in token | m365 CLI reuses old consent — must force consent via OAuth URL first (see Auth section) |

---

## Generic Graph API Request

```bash
# GET
m365 request --url "https://graph.microsoft.com/v1.0/me"

# POST
m365 request --url "https://graph.microsoft.com/v1.0/<path>" \
  --method post \
  --body '{"key": "value"}' \
  --content-type "application/json"
```

### Getting an access token for curl

```bash
ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)
```

### Output parsing pattern

```bash
m365 request --url "..." | python3 -c "
import sys, json
data = json.load(sys.stdin)
items = data if isinstance(data, list) else data.get('value', [])
for item in items:
    print(item.get('fieldName', ''))
"
```

### Strip HTML from message bodies

```python
import re
body_clean = re.sub(r'<[^>]+>', '', html_body).strip()
body_clean = re.sub(r'\n\s*\n\s*\n', '\n\n', body_clean)
```

---

## Failure Notification (MANDATORY)

If any step, command, API call, or tool in this workflow fails or does not work as expected, you MUST immediately notify the user with:
1. What failed
2. The error or unexpected behavior observed
3. What you plan to do instead (if anything)

Do NOT silently fall back to alternative approaches without informing the user first.

---

## Self-Update Protocol

If you discovered something new during this task (failures, bugs, edge cases, better approaches, new IDs or mappings), update the relevant domain file directly without waiting for the user to ask. Skip if the task was routine with no new findings.

</instructions>
