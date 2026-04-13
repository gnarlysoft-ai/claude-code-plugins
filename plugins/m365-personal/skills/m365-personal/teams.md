# Teams Chat & Presence Reference

## Table of Contents

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
| `m365 teams team list` | Returns Skype-related error | Use Graph API: `m365 request --url ".../me/joinedTeams"` |
| `m365 teams chat message list` | No `--top` option, fetches all messages | Use Graph API: `m365 request --url ".../chats/{id}/messages?$top=N"` |
