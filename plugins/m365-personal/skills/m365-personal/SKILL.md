---
name: "gnarlysoft:m365-personal"
description: Query your personal Microsoft 365 data — read your own Outlook inbox, sent items, folders, and messages; view your calendar events, meetings, and availability; list and read your Teams chats, messages, and conversations; list Teams teams and channels (including channel email addresses); check and set your presence status; fetch and download meeting transcripts; upload, download, and share files on OneDrive and SharePoint — using the CLI for Microsoft 365 (m365) tool and direct Graph API calls. Use this skill for personal M365 use (reading your own inbox, calendar, Teams chats/teams/channels, presence, meeting transcripts, OneDrive/SharePoint files), not for org-wide or admin management tasks.
allowed-tools: Bash, Read
---

# Microsoft 365 Query Skill

<context>
This skill queries Microsoft 365 data using the `m365` CLI (v11.4.0, `@pnp/cli-microsoft365`) and direct Microsoft Graph API calls via `m365 request`. Authentication is managed by the m365 CLI itself — no API token files needed.

**Authenticated account:** Run `m365 status` to verify
**App:** Gnarlysoft-Delegated-CLI (App ID: `2dbdde76-d0f3-4aa2-8af6-391a66867742`)
**Tenant:** `f64ae4c4-b8e2-453a-97bb-8e73450aed49`
**Permissions:** `User.Read`, `User.ReadBasic.All`, `Mail.Read`, `Mail.ReadBasic`, `Mail.ReadWrite`, `Chat.Read`, `Chat.ReadWrite`, `ChannelMessage.Read.All`, `ChannelMessage.Send`, `Team.ReadBasic.All`, `Channel.ReadBasic.All`, `Presence.ReadWrite`, `OnlineMeetings.Read`, `OnlineMeetingTranscript.Read.All`, `Files.ReadWrite.All`, `Calendars.Read`
</context>

<instructions>

## Authentication

```bash
m365 status
```

If not logged in, run the **full bootstrap** (see below) rather than a bare `m365 login` — a bare login produces a token that is missing most scopes and causes mid-task 403s.

If m365 CLI not installed: `npm install -g @pnp/cli-microsoft365`

### Why scopes go missing (root cause)

Three independent layers determine what's in your access token:

| Layer | What it controls | Failure mode |
|---|---|---|
| App registration permissions | Which scopes the app is *allowed* to request | Scope not listed → can't be consented → 403 |
| User/admin consent | Which allowed scopes the user has *agreed* to | Consented only for a subset → remaining scopes 403 |
| CLI login scope request | Which consented scopes the CLI *asks for* at login | CLI asks for a fixed default set → other consented scopes still missing from token |

**`m365 login` has no `--scope` flag.** At login, the CLI requests a fixed default set; built-in `m365 xyz` commands then *incrementally* acquire more scopes via MSAL on first use. But `m365 request` (raw Graph) does **not** trigger incremental acquisition — it reuses whatever is already cached. That's why a raw `m365 request` to a chat endpoint can 403 even after you consented to `Chat.ReadWrite`.

**The fix:** pre-consent every scope you'll need in one shot (so the app's consent state covers all of them), then let the CLI's login + first-use calls populate the token cache. After that, raw `m365 request` works for any of those scopes.

### Full bootstrap (run once, or after adding new permissions)

**Step 1 — Consolidated force-consent** (grants all 16 scopes in one consent screen):

```bash
open "https://login.microsoftonline.com/f64ae4c4-b8e2-453a-97bb-8e73450aed49/oauth2/v2.0/authorize?client_id=2dbdde76-d0f3-4aa2-8af6-391a66867742&response_type=code&redirect_uri=http://localhost&prompt=consent&scope=https%3A%2F%2Fgraph.microsoft.com%2FUser.Read+https%3A%2F%2Fgraph.microsoft.com%2FUser.ReadBasic.All+https%3A%2F%2Fgraph.microsoft.com%2FMail.Read+https%3A%2F%2Fgraph.microsoft.com%2FMail.ReadBasic+https%3A%2F%2Fgraph.microsoft.com%2FMail.ReadWrite+https%3A%2F%2Fgraph.microsoft.com%2FChat.Read+https%3A%2F%2Fgraph.microsoft.com%2FChat.ReadWrite+https%3A%2F%2Fgraph.microsoft.com%2FChannelMessage.Read.All+https%3A%2F%2Fgraph.microsoft.com%2FChannelMessage.Send+https%3A%2F%2Fgraph.microsoft.com%2FTeam.ReadBasic.All+https%3A%2F%2Fgraph.microsoft.com%2FChannel.ReadBasic.All+https%3A%2F%2Fgraph.microsoft.com%2FPresence.ReadWrite+https%3A%2F%2Fgraph.microsoft.com%2FOnlineMeetings.Read+https%3A%2F%2Fgraph.microsoft.com%2FOnlineMeetingTranscript.Read.All+https%3A%2F%2Fgraph.microsoft.com%2FFiles.ReadWrite.All+https%3A%2F%2Fgraph.microsoft.com%2FCalendars.Read+offline_access"
```

Approve the consent screen. The redirect to `localhost` will fail with "connection refused" — **this is expected and means consent succeeded**.

**Step 2 — Fresh login:**

```bash
m365 logout
m365 login --appId "2dbdde76-d0f3-4aa2-8af6-391a66867742" \
  --tenant "f64ae4c4-b8e2-453a-97bb-8e73450aed49" \
  --authType deviceCode
```

**Step 3 — Verify token scopes:**

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

**Step 4 — If a scope is still missing from the token after Steps 1–3**, trigger MSAL to cache it by running a built-in m365 command that declares that scope as required. Examples:

| Missing scope | Command that forces MSAL to acquire it |
|---|---|
| `Chat.ReadWrite` | `m365 teams chat list` |
| `Mail.ReadWrite` | `m365 outlook message list --folderName Inbox --output json` |
| `Files.ReadWrite.All` | `m365 onedrive list` |
| `Presence.ReadWrite` | `m365 teams user presence get` |
| `Team.ReadBasic.All` | `m365 request --url "https://graph.microsoft.com/v1.0/me/joinedTeams"` |
| `Calendars.Read` | `m365 request --url "https://graph.microsoft.com/v1.0/me/calendars"` |

After the warm-up command runs successfully, subsequent raw `m365 request` calls using that scope will work.

### Troubleshooting a 403 mid-task

1. Decode the current token (Step 3 above) — is the scope present?
2. If **not present**: re-run the Step 1 consent URL (all scopes at once), then `m365 logout && m365 login`, then the warm-up command from the Step 4 table.
3. If **present** but still 403: the endpoint may require a different scope than documented — check the Graph API reference and add that scope to the consent URL.

**Do NOT** silently fall back to another approach — per the skill's Failure Notification rule, tell the user which scope is missing and which step failed before retrying.

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

### Teams Chat, Channels & Presence → [teams.md](teams.md)

List/send/edit chat messages, @mentions, presence status. List joined Teams, channels, and get channel email addresses.

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/chats?\$expand=members&\$top=20"
m365 request --url "https://graph.microsoft.com/v1.0/me/joinedTeams"
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
| 403 on `m365 request` with scope that "should" be there | CLI's login only requests a default scope set; raw `m365 request` doesn't trigger incremental consent. Run the full bootstrap + warm-up command in Auth section. |

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
# Teams channel messages often contain literal backslash-escaped newlines (\\n)
# between paragraph tags — replace them before stripping HTML.
body_clean = html_body.replace('\\n', '\n')
body_clean = re.sub(r'<br[^>]*>', '\n', body_clean)
body_clean = re.sub(r'</(p|li|div)>', '\n', body_clean)
body_clean = re.sub(r'<[^>]+>', '', body_clean)
body_clean = body_clean.replace('&nbsp;', ' ').replace('&amp;', '&').strip()
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
