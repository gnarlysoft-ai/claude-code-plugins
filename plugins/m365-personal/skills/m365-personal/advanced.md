# M365 Personal — Advanced Topics

## Table of Contents

- [Error Handling](#error-handling)
- [Commands to Avoid](#commands-to-avoid)
- [Copying Rich HTML to Clipboard (for Outlook)](#copying-rich-html-to-clipboard-for-outlook)
- [Output Formatting](#output-formatting)
- [Graph API Tips](#graph-api-tips)

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
| Empty transcript list | Transcription was not enabled during meeting | Enable transcription in meeting options or set `recordAutomatically: true` |
| `403 Forbidden` on transcripts | Missing `OnlineMeetings.Read` permission | Add permission to app registration and re-consent |
| No meetings returned | Wrong date range or user not an attendee | Adjust `--startDateTime` or check with organizer's userId |
| Graph API sites `$search` returns 400 | Missing `Sites.Read.All` permission | Use `m365 spo site list` instead |
| `m365 request --filePath` PUT returns empty output | Binary file uploaded but no JSON response body | Use `curl` with `m365 util accesstoken get` for binary uploads when you need the response |

---

## Commands to Avoid

- `m365 teams team list` — causes Skype backend error, always fails
- `m365 outlook mail message list` — wrong command path, does not exist
- `m365 teams chat message list` — works but has no `--top`; slow for large chats; prefer Graph API

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

**Why not raw HTML via `pbcopy`?** Piping HTML directly into `pbcopy` copies it as plain text. Outlook pastes the literal HTML tags instead of rendering them.

**Why not the `hexdump | xargs | osascript` approach?** That method breaks with larger HTML files due to `xargs` argument length limits.

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

## Graph API Tips

### Generic Graph API Requests

Use `m365 request` as a general-purpose escape hatch for any Graph endpoint:

```bash
# GET request
m365 request --url "https://graph.microsoft.com/v1.0/me"

# POST request with body
m365 request --url "https://graph.microsoft.com/v1.0/me/messages" \
  --method POST \
  --body '{"subject": "test"}'
```

### Known caveats with `m365 request`

- `$select` param can cause 400 errors on mail endpoints — omit it and filter fields in Python instead
- `$top`, `$orderby`, `$filter` all work correctly
- `$search` and `$orderby` cannot be combined — omit `$orderby` when using `$search`
- Escape `$` in shell with `\$` or use single quotes
- Use lowercase method names: `--method post`, `--method delete`, `--method patch`
- `--filePath` with PUT uploads binary files but returns empty output — use `curl` with access token instead

### Getting an access token for curl

```bash
ACCESS_TOKEN=$(m365 util accesstoken get --resource "https://graph.microsoft.com" --output text)
curl -s -X GET "https://graph.microsoft.com/v1.0/me" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```
