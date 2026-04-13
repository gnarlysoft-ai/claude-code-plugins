# Outlook Email Reference

## Table of Contents

- [Endpoints](#endpoints)
- [CLI Commands](#cli-commands)
- [Message Object Fields](#message-object-fields)
- [Mail Folder Names](#mail-folder-names)
- [List Messages via Graph API](#list-messages-via-graph-api)
- [Parse and Display Email List](#parse-and-display-email-list)
- [Get Specific Message with Body](#get-specific-message-with-body)
- [List Mail Folders](#list-mail-folders)
- [Search Emails](#search-emails)
- [Filter Examples](#filter-examples)
- [Find Emails from Sender in Last 7 Days](#find-emails-from-sender-in-last-7-days)
- [List Unread Emails](#list-unread-emails)
- [Delete Email](#delete-email)
- [Copying Rich HTML to Clipboard](#copying-rich-html-to-clipboard)
- [Common Errors](#common-errors)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/messages | List messages across all folders |
| GET | /me/mailFolders/{folder}/messages | List messages in a specific folder |
| GET | /me/messages/{id} | Get a specific message |
| GET | /me/mailFolders | List all mail folders |
| DELETE | /me/messages/{id} | Delete a specific message |

## CLI Commands

List emails in Inbox:

```bash
m365 outlook message list --folderName Inbox --output json
```

**IMPORTANT:** The correct command is `m365 outlook message list`, NOT `m365 outlook mail message list`.

## Message Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique message identifier |
| subject | string | Email subject line |
| receivedDateTime | string | ISO 8601 datetime when received |
| from | object | Sender info: `from.emailAddress.name`, `from.emailAddress.address` |
| toRecipients | array | Recipients with emailAddress objects |
| body | object | `body.contentType` (html/text), `body.content` |
| bodyPreview | string | Short plaintext preview of body |
| isRead | boolean | Whether the message has been read |
| hasAttachments | boolean | Whether the message has attachments |
| importance | string | low, normal, high |
| flag | object | Flag status |
| webLink | string | URL to open in Outlook web |

## Mail Folder Names

| Folder Name | Description |
|-------------|-------------|
| Inbox | Main inbox |
| Sent Items | Sent messages |
| Drafts | Draft messages |
| Deleted Items | Trash |
| Junk Email | Spam folder |
| Archive | Archived messages |

## List Messages via Graph API

List latest 10 messages in Inbox, ordered by date:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?\$top=10&\$orderby=receivedDateTime desc" --method get
```

List latest 5 messages across all folders:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$top=5&\$orderby=receivedDateTime desc" --method get
```

**IMPORTANT:** Do NOT use `$select` — it causes 400 Bad Request errors with the mail API.

## Parse and Display Email List

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?\$top=10&\$orderby=receivedDateTime desc" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
msgs = data.get('value', data) if isinstance(data, dict) else data
for m in msgs:
    fr = m['from']['emailAddress']
    read = 'Read' if m['isRead'] else 'UNREAD'
    print(f\"[{read}] {m['receivedDateTime'][:16]}  From: {fr['name']} <{fr['address']}>  Subject: {m['subject']}\")
"
```

## Get Specific Message with Body

Fetch a message by ID and strip HTML from the body:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/MESSAGE_ID_HERE" --method get | python3 -c "
import sys, json, re
msg = json.load(sys.stdin)
fr = msg['from']['emailAddress']
print(f\"From: {fr['name']} <{fr['address']}>\")
print(f\"Date: {msg['receivedDateTime']}\")
print(f\"Subject: {msg['subject']}\")
print(f\"To: {', '.join(r['emailAddress']['address'] for r in msg['toRecipients'])}\")
print('---')
body = msg['body']['content']
text = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '', text)
text = re.sub(r'&nbsp;', ' ', text)
text = re.sub(r'&amp;', '&', text)
text = re.sub(r'&lt;', '<', text)
text = re.sub(r'&gt;', '>', text)
text = re.sub(r'\n{3,}', '\n\n', text)
print(text.strip())
"
```

## List Mail Folders

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data['value']:
    print(f\"{f['displayName']:30s} Total: {f['totalItemCount']:5d}  Unread: {f['unreadItemCount']:5d}  ID: {f['id']}\")
"
```

## Search Emails

Use `$search` to find emails by keyword:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$search=\"quarterly report\"&\$top=10" --method get
```

**IMPORTANT:** Do NOT combine `$search` with `$orderby` — it causes 400 Bad Request. Search results are returned by relevance.

## Filter Examples

| Filter | Example |
|--------|---------|
| Unread messages | `$filter=isRead eq false` |
| From specific sender | `$filter=from/emailAddress/address eq 'user@example.com'` |
| Subject contains | `$filter=contains(subject,'keyword')` |
| Has attachments | `$filter=hasAttachments eq true` |
| Date range | `$filter=receivedDateTime ge 2026-04-01T00:00:00Z and receivedDateTime lt 2026-04-14T00:00:00Z` |
| Unread with attachments | `$filter=isRead eq false and hasAttachments eq true` |

## Find Emails from Sender in Last 7 Days

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$filter=from/emailAddress/address eq 'sender@example.com' and receivedDateTime ge $(date -u -v-7d +%Y-%m-%dT00:00:00Z)&\$orderby=receivedDateTime desc&\$top=20" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
msgs = data.get('value', data) if isinstance(data, dict) else data
for m in msgs:
    print(f\"{m['receivedDateTime'][:16]}  Subject: {m['subject']}\")
print(f\"Total: {len(msgs)} messages\")
"
```

## List Unread Emails

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages?\$filter=isRead eq false&\$orderby=receivedDateTime desc&\$top=20" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
msgs = data.get('value', data) if isinstance(data, dict) else data
for m in msgs:
    fr = m['from']['emailAddress']
    print(f\"{m['receivedDateTime'][:16]}  From: {fr['name']} <{fr['address']}>  Subject: {m['subject']}\")
print(f\"Total unread: {len(msgs)}\")
"
```

## Delete Email

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/MESSAGE_ID_HERE" --method delete
```

**IMPORTANT:** Use `--method delete` (lowercase). Uppercase `DELETE` may cause issues.

## Copying Rich HTML to Clipboard

To copy an HTML email body to the clipboard as rich text (for pasting into Outlook, Word, etc.):

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/MESSAGE_ID_HERE" --method get | python3 -c "
import sys, json
msg = json.load(sys.stdin)
print(msg['body']['content'])
" > /tmp/email.html
textutil -convert rtf -stdout /tmp/email.html | pbcopy
```

**IMPORTANT:**
- Do NOT pipe raw HTML via `pbcopy` — it pastes as plain HTML source code
- Do NOT use hexdump approach — it does not produce rich text
- Use `textutil -convert rtf` to convert HTML to RTF, then pipe to `pbcopy`

For better font rendering in Outlook, wrap the HTML body with Aptos font styling:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages/MESSAGE_ID_HERE" --method get | python3 -c "
import sys, json
msg = json.load(sys.stdin)
html = msg['body']['content']
styled = f'<div style=\"font-family: Aptos, Calibri, Arial, sans-serif; font-size: 11pt;\">{html}</div>'
print(styled)
" > /tmp/email.html
textutil -convert rtf -stdout /tmp/email.html | pbcopy
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 400 Bad Request with `$select` | `$select` is not supported on mail messages endpoint | Remove `$select` from the query |
| 400 Bad Request with `$search` + `$orderby` | Cannot combine `$search` with `$orderby` | Use `$search` alone (results ordered by relevance) |
| Command not found: `m365 outlook mail message list` | Wrong command path | Use `m365 outlook message list` (no `mail` segment) |
| Empty response on delete | Normal behavior | DELETE returns empty body on success (HTTP 204) |
