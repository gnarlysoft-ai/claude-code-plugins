# Teams Chat, Channels & Presence Reference

## Table of Contents

- [Teams & Channels](#teams--channels)
- [List Joined Teams](#list-joined-teams)
- [List Channels in a Team](#list-channels-in-a-team)
- [Get Channel Email Address](#get-channel-email-address)
- [Chat Endpoints](#chat-endpoints)
- [Known Chat IDs](#known-chat-ids)
- [Chat Object Fields](#chat-object-fields)
- [Message Object Fields](#message-object-fields)
- [List Chats](#list-chats)
- [List Chat Messages](#list-chat-messages)
- [Read Latest N Messages](#read-latest-n-messages)
- [Send Message](#send-message)
- [Edit Message](#edit-message)
- [Mentions](#mentions)
- [Pagination](#pagination)
- [Presence](#presence)
- [Presence Availability Values](#presence-availability-values)
- [Presence Activity Values](#presence-activity-values)
- [Set Presence](#set-presence)
- [Set Status Message](#set-status-message)
- [Clear Status Message](#clear-status-message)
- [Presence Consent](#presence-consent)
- [Commands to Avoid](#commands-to-avoid)

## Teams & Channels

**Required permissions:** `Team.ReadBasic.All`, `Channel.ReadBasic.All`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/joinedTeams | List all Teams you belong to |
| GET | /teams/{teamId}/channels | List channels in a Team |
| GET | /teams/{teamId}/channels/{channelId} | Get a specific channel (includes email) |

### List Joined Teams

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/joinedTeams" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data.get('value', []):
    print(f\"{t.get('displayName', 'Unknown')}  ID: {t['id']}\")
"
```

**IMPORTANT:** `m365 teams team list` always fails with a Skype backend error — use the Graph API endpoint above instead.

### List Channels in a Team

```bash
m365 request --url "https://graph.microsoft.com/v1.0/teams/TEAM_ID_HERE/channels" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data.get('value', []):
    email = c.get('email', 'N/A')
    print(f\"{c.get('displayName', 'Unknown')}  email: {email}  ID: {c['id']}\")
"
```

### Get Channel Email Address

Each Teams channel can have an email address. Send an email to this address and it appears as a message in the channel.

```bash
# Get a specific channel's details including email
m365 request --url "https://graph.microsoft.com/v1.0/teams/TEAM_ID_HERE/channels/CHANNEL_ID_HERE" --method get | python3 -c "
import sys, json
c = json.load(sys.stdin)
print(f\"Channel: {c.get('displayName')}\")
print(f\"Email: {c.get('email', 'No email configured')}\")
"
```

**Note:** Not all channels have email addresses. The `email` field will be absent or null if not configured.

---

## Channel Messages

**Required permissions:** `ChannelMessage.Read.All` (list/read), `ChannelMessage.Send` (post/reply), `User.ReadBasic.All` (resolve @mention user IDs).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /teams/{teamId}/channels/{channelId}/messages | List messages in a channel |
| POST | /teams/{teamId}/channels/{channelId}/messages | Post a message to a channel |
| POST | /teams/{teamId}/channels/{channelId}/messages/{messageId}/replies | Reply to a channel message |

The channel ID format is `19:HASH@thread.tacv2` (URL-decoded from the Teams deep link).

### List Channel Messages

```bash
m365 request --url "https://graph.microsoft.com/v1.0/teams/TEAM_ID_HERE/channels/CHANNEL_ID_HERE/messages?\$top=20" --method get --output json | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
for m in data.get('value', []):
    if m.get('messageType') != 'message':
        continue
    sender = m.get('from', {}).get('user', {}).get('displayName', 'Unknown')
    text = re.sub(r'<[^>]+>', '', m.get('body', {}).get('content', '')).strip()
    if text:
        print(f\"{m['createdDateTime'][:16]}  {sender}: {text}\")
"
```

### Send Channel Message (plain)

```bash
m365 request --url "https://graph.microsoft.com/v1.0/teams/TEAM_ID_HERE/channels/CHANNEL_ID_HERE/messages" \
  --method post \
  --content-type "application/json" \
  --body '{"body":{"contentType":"html","content":"<p>Hello channel</p>"}}'
```

### Send Channel Message with @mentions

Every `<at id="N">...</at>` tag in the HTML body must have a matching entry in the `mentions` array with the same integer `id`. The mentioned user needs `userIdentityType: "aadUser"`.

1. Resolve each user's `id` by display name (requires `User.ReadBasic.All`):

```bash
m365 request --url "https://graph.microsoft.com/v1.0/users?\$filter=startswith(displayName,'Jacob')&\$select=id,displayName,mail&\$top=5" --output json | python3 -c "
import sys, json
d = json.load(sys.stdin)
for u in d.get('value', []):
    print(f\"{u['displayName']:35s} mail={u.get('mail','')}  id={u['id']}\")
"
```

2. Send with the mention payload. Because the JSON contains quotes inside quotes, prefer a Python helper over an inline `--body`:

```python
import json, subprocess, urllib.request

TEAM_ID = "TEAM_ID_HERE"
CHANNEL_ID = "19:...@thread.tacv2"
USERS = [
    {"id": "USER_ID_1", "name": "Jacob Kapostins"},
    {"id": "USER_ID_2", "name": "Eliezer Pujols"},
]

mentions_html = " ".join(f'<at id="{i}">{u["name"]}</at>' for i, u in enumerate(USERS))
payload = {
    "body": {"contentType": "html", "content": f"<p>Hey {mentions_html}, see this.</p>"},
    "mentions": [
        {"id": i, "mentionText": u["name"],
         "mentioned": {"user": {"id": u["id"], "userIdentityType": "aadUser"}}}
        for i, u in enumerate(USERS)
    ],
}
token = subprocess.check_output(
    ["m365", "util", "accesstoken", "get", "--resource", "https://graph.microsoft.com", "--output", "text"],
    text=True,
).strip()
req = urllib.request.Request(
    f"https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages",
    data=json.dumps(payload).encode(), method="POST",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)
print(json.loads(urllib.request.urlopen(req).read()).get("webUrl"))
```

### Reply to a Channel Message

```bash
m365 request --url "https://graph.microsoft.com/v1.0/teams/TEAM_ID_HERE/channels/CHANNEL_ID_HERE/messages/PARENT_MESSAGE_ID/replies" \
  --method post \
  --content-type "application/json" \
  --body '{"body":{"contentType":"html","content":"<p>Thanks</p>"}}'
```

### Parsing a Teams Channel Deep Link

A Teams channel URL has the form:

```
https://teams.microsoft.com/l/channel/<url-encoded-channelId>/<ChannelName>?groupId=<teamId>&tenantId=<tenantId>
```

- `groupId` = `teamId` used in the Graph URL
- The first path segment is the URL-encoded channel ID — decode `%3A` → `:` and `%40` → `@` to get `19:...@thread.tacv2`

---

## Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/chats | List all chats |
| GET | /chats/{chatId} | Get a specific chat |
| GET | /chats/{chatId}/messages | List messages in a chat |
| GET | /chats/{chatId}/members | List members of a chat |
| POST | /chats/{chatId}/messages | Send a message |
| PATCH | /chats/{chatId}/messages/{messageId} | Edit a message |

## Known Chat IDs

| Chat | Chat ID |
|------|---------|
| 404 Team | `19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2` |

## Chat Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Chat thread ID |
| topic | string | Chat topic/name (null for 1:1) |
| chatType | string | oneOnOne, group, meeting |
| createdDateTime | string | ISO 8601 creation time |
| lastUpdatedDateTime | string | ISO 8601 last activity time |
| members | array | Chat members (when expanded) |
| webUrl | string | URL to open in Teams |

## Message Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Message ID |
| body | object | `body.contentType` (html/text), `body.content` |
| from | object | `from.user.displayName`, `from.user.id` |
| createdDateTime | string | ISO 8601 when sent |
| lastModifiedDateTime | string | ISO 8601 when last edited |
| messageType | string | message, systemEventMessage |
| importance | string | normal, high, urgent |
| mentions | array | @mentions in the message |
| attachments | array | File attachments |

## List Chats

Using m365 CLI:

```bash
m365 teams chat list --output json
```

Using Graph API with member expansion:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/chats?\$expand=members&\$top=50" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data['value']:
    topic = c.get('topic')
    if not topic:
        members = c.get('members', [])
        names = [m.get('displayName', 'Unknown') for m in members]
        topic = ', '.join(names)
    print(f\"[{c['chatType']}] {topic}  ID: {c['id']}\")
"
```

## List Chat Messages

Use Graph API directly (preferred — native CLI `m365 teams chat message list` has no `--top` option):

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages?\$top=20" --method get | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
msgs = data.get('value', data) if isinstance(data, dict) else data
for m in msgs:
    if m.get('messageType') != 'message':
        continue
    sender = m.get('from', {}).get('user', {}).get('displayName', 'Unknown')
    body = m.get('body', {}).get('content', '')
    text = re.sub(r'<[^>]+>', '', body).strip()
    if not text:
        continue
    print(f\"{m['createdDateTime'][:16]}  {sender}: {text}\")
"
```

## Read Latest N Messages

Read the latest 10 messages from a specific chat:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages?\$top=10" --method get | python3 -c "
import sys, json, re
data = json.load(sys.stdin)
msgs = data.get('value', data) if isinstance(data, dict) else data
msgs = [m for m in msgs if m.get('messageType') == 'message']
for m in reversed(msgs):
    sender = m.get('from', {}).get('user', {}).get('displayName', 'Unknown')
    body = m.get('body', {}).get('content', '')
    text = re.sub(r'<[^>]+>', '', body).strip()
    if text:
        print(f\"{m['createdDateTime'][:16]}  {sender}: {text}\")
"
```

## Send Message

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages" --method post --body '{"body":{"contentType":"html","content":"Hello from CLI"}}' --content-type "application/json"
```

**IMPORTANT:** Use `--method post` (lowercase) and include `--content-type "application/json"`.

## Edit Message

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages/MESSAGE_ID_HERE" --method patch --body '{"body":{"contentType":"html","content":"Updated message text"}}' --content-type "application/json"
```

**IMPORTANT:** PATCH returns empty string `""` on success — this is NOT an error.

## Mentions

To @mention a user, use `<at id="N">Name</at>` in the message body and include a `mentions` array:

First, get the member's user ID:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/members" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data['value']:
    uid = m.get('userId', 'N/A')
    print(f\"{m.get('displayName', 'Unknown')}  userId: {uid}\")
"
```

Then send with mention:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages" --method post --body '{"body":{"contentType":"html","content":"Hey <at id=\"0\">John Doe</at>, check this out"},"mentions":[{"id":0,"mentionText":"John Doe","mentioned":{"user":{"displayName":"John Doe","id":"USER_ID_HERE"}}}]}' --content-type "application/json"
```

## Delete Messages

**NOT supported via the Graph API.** Attempting to delete chat messages returns 405 Method Not Allowed or 404 Not Found.

## Pagination

- Chat messages support `$top` with a maximum of 50 per page
- Use `@odata.nextLink` from the response to fetch the next page
- Continue following `@odata.nextLink` until it is absent from the response

```bash
m365 request --url "https://graph.microsoft.com/v1.0/chats/CHAT_ID_HERE/messages?\$top=50" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
msgs = data.get('value', [])
print(f\"Messages in this page: {len(msgs)}\")
next_link = data.get('@odata.nextLink')
if next_link:
    print(f\"Next page: {next_link}\")
else:
    print('No more pages')
"
```

## Presence

Get current presence status:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/presence" --method get | python3 -c "
import sys, json
p = json.load(sys.stdin)
print(f\"Availability: {p['availability']}\")
print(f\"Activity: {p['activity']}\")
msg = p.get('statusMessage', {})
if msg and msg.get('message', {}).get('content'):
    print(f\"Status: {msg['message']['content']}\")
"
```

## Presence Availability Values

| Value | Description |
|-------|-------------|
| Available | Online and available |
| Busy | Busy |
| DoNotDisturb | Do not disturb |
| Away | Away |
| BeRightBack | Be right back |
| Offline | Appear offline |

## Presence Activity Values

| Value | Description |
|-------|-------------|
| Available | Available |
| InACall | In a call |
| InAMeeting | In a meeting |
| Busy | Busy |
| Away | Away |
| BeRightBack | Be right back |
| DoNotDisturb | Do not disturb |
| Offline | Offline |
| OffWork | Off work |

## Set Presence

**IMPORTANT:** Use `setUserPreferredPresence` (beta endpoint), NOT `setPresence`. The per-session `setPresence` gets overridden by Teams client activity within minutes.

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/setUserPreferredPresence" --method post --body '{"availability":"DoNotDisturb","activity":"DoNotDisturb","expirationDuration":"PT4H"}' --content-type "application/json"
```

The `expirationDuration` is ISO 8601 duration format (e.g., PT1H = 1 hour, PT4H = 4 hours, PT8H = 8 hours).

To clear the preferred presence (revert to automatic):

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/clearUserPreferredPresence" --method post --body '{}' --content-type "application/json"
```

## Set Status Message

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/setStatusMessage" --method post --body '{"statusMessage":{"message":{"content":"Working remotely today","contentType":"text"},"expiryDateTime":{"dateTime":"'$(date -u -v+8H +%Y-%m-%dT%H:%M:%S.0000000)'","timeZone":"UTC"}}}' --content-type "application/json"
```

## Clear Status Message

```bash
m365 request --url "https://graph.microsoft.com/beta/me/presence/clearStatusMessage" --method post --body '{}' --content-type "application/json"
```

## Presence Consent

If presence API returns 403 Forbidden, the Presence.ReadWrite permission may need manual OAuth consent:

1. Open the OAuth consent URL in a browser:
   ```
   https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=2dbdde76-d0f3-4aa2-8af6-391a66867742&response_type=code&scope=Presence.ReadWrite
   ```
2. Grant consent in the browser
3. Re-login with: `m365 logout && m365 login --authType browser`

## Commands to Avoid

| Command | Problem | Alternative |
|---------|---------|-------------|
| `m365 teams team list` | Returns Skype-related error | Use Graph API: `m365 request --url ".../me/joinedTeams"` (requires `Team.ReadBasic.All` consent) |
| `m365 teams chat message list` | No `--top` option, fetches all messages | Use Graph API: `m365 request --url ".../chats/{id}/messages?$top=N"` |
