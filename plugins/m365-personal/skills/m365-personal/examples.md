# M365 Personal — Common Workflow Examples

## Table of Contents

- [Find emails from a sender in the last 7 days](#find-emails-from-a-sender-in-the-last-7-days)
- [List all unread emails](#list-all-unread-emails)
- [Search emails by keyword](#search-emails-by-keyword)
- [Read latest N messages from a Teams chat](#read-latest-n-messages-from-a-teams-chat)
- [Send a message with @mentions](#send-a-message-with-mentions)
- [List meetings with transcript availability](#list-meetings-with-transcript-availability)
- [Download and parse a meeting transcript](#download-and-parse-a-meeting-transcript)
- [Upload file to SharePoint and get sharing link](#upload-file-to-sharepoint-and-get-sharing-link)
- [Upload large file to OneDrive (> 4MB)](#upload-large-file-to-onedrive--4mb)
- [Check OneDrive storage quota](#check-onedrive-storage-quota)

---

## Find emails from a sender in the last 7 days

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

---

## List all unread emails

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$filter=isRead eq false&\$top=25&\$orderby=receivedDateTime desc" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"[{m.get('receivedDateTime','')[:10]}] {m.get('from',{}).get('emailAddress',{}).get('address','')} | {m.get('subject','')}\")
"
```

---

## Search emails by keyword

Use `$search` to search across all message content (subject, body, from, to). Do NOT combine `$search` with `$orderby`.

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/messages?\$search=\"keyword\"&\$top=25" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"[{m.get('receivedDateTime','')[:10]}] {m.get('from',{}).get('emailAddress',{}).get('address','')} | {m.get('subject','')}\")
"
```

---

## Read latest N messages from a Teams chat

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

---

## Send a message with @mentions

**Step 1:** Get the user's Teams ID from the chat members:

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/members" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data.get('value', []):
    print(f\"{m.get('displayName','')}: userId={m.get('userId','')}, email={m.get('email','')}\")
"
```

**Step 2:** Send the message with the mention:

```bash
CHAT_ID="19:db5939070fcf4dad8dfe2bbd32e1334a@thread.v2"
m365 request --url "https://graph.microsoft.com/v1.0/chats/${CHAT_ID}/messages" \
  --method post \
  --body '{
    "body": {
      "contentType": "html",
      "content": "Hey <at id=\"0\">Javier Jaquez</at>, check this out."
    },
    "mentions": [
      {
        "id": 0,
        "mentionText": "Javier Jaquez",
        "mentioned": {
          "user": {
            "displayName": "Javier Jaquez",
            "id": "15700490-e1cd-4af4-81b5-aa8d639daeb3",
            "userIdentityType": "aadUser"
          }
        }
      }
    ]
  }' \
  --content-type "application/json"
```

**Notes:**
- The `id` in `<at id="0">` must match the `id` in the `mentions` array
- For multiple mentions, increment the id: `<at id="0">`, `<at id="1">`, etc.
- `userIdentityType` is always `aadUser` for regular M365 users

---

## List meetings with transcript availability

```bash
m365 teams meeting list --startDateTime "2026-03-01T00:00:00Z" --output json | python3 -c "
import sys, json
meetings = json.load(sys.stdin)
for m in meetings:
    subject = m.get('subject', '(no subject)')
    start = m.get('startDateTime', '')[:16].replace('T', ' ')
    has_transcription = m.get('allowTranscription', False)
    auto_record = m.get('recordAutomatically', False)
    print(f'[{start}] {subject}')
    print(f'  Transcription: {has_transcription} | Auto-record: {auto_record}')
    print(f'  ID: {m.get(\"id\", \"\")}')
    print()
"
```

---

## Download and parse a meeting transcript

```bash
MEETING_ID="<meeting-id>"
TRANSCRIPT_ID="<transcript-id>"

# Download as VTT
m365 teams meeting transcript get \
  --meetingId "$MEETING_ID" \
  --id "$TRANSCRIPT_ID" \
  --outputFile /tmp/meeting-transcript.vtt

# Parse VTT to plain text
python3 -c "
import re, sys
with open('/tmp/meeting-transcript.vtt') as f:
    content = f.read()
entries = re.findall(r'(\d{2}:\d{2}:\d{2}\.\d+) --> \d{2}:\d{2}:\d{2}\.\d+\n<v ([^>]+)>(.+?)</v>', content)
current_speaker = None
for ts, speaker, text in entries:
    if speaker != current_speaker:
        current_speaker = speaker
        print(f'\n**{speaker}** [{ts[:8]}]')
    print(f'  {text}')
"
```

---

## Upload file to SharePoint and get sharing link

```bash
FILE_PATH="/path/to/attachment.pdf"
FILE_NAME="attachment.pdf"
DRIVE_ID="b!PMw4hWM4GkqxxjNxV6MCPdvAbeoHQN1MjSDuN9tmbW8XWDbGGaPcSa9cXkAmP_-0"
DEST_FOLDER="Shared-Files"
ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)

# Step 1: Upload via curl (binary-safe, returns JSON response)
curl -s -X PUT "https://graph.microsoft.com/v1.0/drives/${DRIVE_ID}/root:/${DEST_FOLDER}/${FILE_NAME}:/content" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @"${FILE_PATH}" > /tmp/upload-result.json

# Step 2: Create org-wide sharing link
m365 request --url "https://graph.microsoft.com/v1.0/drives/${DRIVE_ID}/root:/${DEST_FOLDER}/${FILE_NAME}:/createLink" \
  --method post \
  --body '{"type":"view","scope":"organization"}' \
  --content-type "application/json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
link = data.get('link', {}).get('webUrl', '')
print(f'Sharing link: {link}')
"
```

---

## Upload large file to OneDrive (> 4MB)

For files larger than 4MB, use a resumable upload session:

```bash
FILE_PATH="/path/to/large-file.zip"
DEST_PATH="Shared-Files/large-file.zip"

# Step 1: Create upload session
UPLOAD_URL=$(m365 request --url "https://graph.microsoft.com/v1.0/me/drive/root:/${DEST_PATH}:/createUploadSession" \
  --method post \
  --body '{"item":{"@microsoft.graph.conflictBehavior":"rename"}}' \
  --content-type "application/json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('uploadUrl', ''))
")

# Step 2: Upload file in chunks using curl
FILE_SIZE=$(stat -f%z "${FILE_PATH}")
curl -s -X PUT "${UPLOAD_URL}" \
  -H "Content-Length: ${FILE_SIZE}" \
  -H "Content-Range: bytes 0-$((FILE_SIZE-1))/${FILE_SIZE}" \
  --data-binary @"${FILE_PATH}" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Uploaded: {data.get('name')}\")
print(f\"Size: {data.get('size')} bytes\")
print(f\"Web URL: {data.get('webUrl')}\")
"
```

---

## Check OneDrive storage quota

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/drive" | python3 -c "
import sys, json
data = json.load(sys.stdin)
q = data.get('quota', {})
used = q.get('used', 0) / (1024**3)
total = q.get('total', 0) / (1024**3)
remaining = q.get('remaining', 0) / (1024**3)
print(f\"Drive: {data.get('driveType')}\")
print(f\"Used: {used:.2f} GB / {total:.2f} GB\")
print(f\"Remaining: {remaining:.2f} GB\")
"
```
