# Outlook Calendar Reference

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/calendarView | List events in a date range (expands recurring) |
| GET | /me/events | List events (does NOT expand recurring) |
| GET | /me/events/{id} | Get a specific event |
| GET | /me/calendars | List all calendars |

## Event Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique event identifier |
| subject | string | Event title |
| start | object | `start.dateTime` (ISO 8601), `start.timeZone` |
| end | object | `end.dateTime` (ISO 8601), `end.timeZone` |
| isAllDay | boolean | Whether the event is all-day |
| location | object | `location.displayName` |
| organizer | object | `organizer.emailAddress.name`, `organizer.emailAddress.address` |
| attendees | array | Each with `emailAddress`, `status.response`, `type` |
| body | object | `body.contentType`, `body.content` |
| webLink | string | URL to open in Outlook web |
| isOnlineMeeting | boolean | Whether it has an online meeting link |
| onlineMeetingUrl | string | Teams/online meeting join URL |
| onlineMeeting | object | `joinUrl`, `conferenceId`, `tollNumber` |
| isCancelled | boolean | Whether the event was cancelled |
| showAs | string | free, tentative, busy, oof, workingElsewhere, unknown |
| importance | string | low, normal, high |
| sensitivity | string | normal, personal, private, confidential |
| recurrence | object | Recurrence pattern if recurring |

## Query Parameters

| Parameter | Description |
|-----------|-------------|
| `$select` | Choose specific fields (works on calendar, unlike mail) |
| `$orderby` | Sort results (e.g., `start/dateTime asc`) |
| `$filter` | Filter events |
| `$top` | Limit number of results |

## Key Notes

- **Always use calendarView for date ranges** — `/me/events` does NOT expand recurring events
- **calendarView requires both `startDateTime` and `endDateTime`** query parameters
- **Datetimes are in UTC** — convert to local timezone for display
- **`$select` works on calendar** — unlike the mail API, you can use `$select` here

## List Upcoming Events (calendarView)

List events for the next 7 days:

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=$(date -u +%Y-%m-%dT%H:%M:%SZ)&endDateTime=$(date -u -v+7d +%Y-%m-%dT%H:%M:%SZ)&\$orderby=start/dateTime asc&\$top=20" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
events = data.get('value', data) if isinstance(data, dict) else data
for e in events:
    start = e['start']['dateTime'][:16]
    end = e['end']['dateTime'][:16]
    loc = e.get('location', {}).get('displayName', '')
    loc_str = f'  Location: {loc}' if loc else ''
    print(f\"{start} - {end}  {e['subject']}{loc_str}\")
print(f\"Total: {len(events)} events\")
"
```

## List Today's Events

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=$(date -u +%Y-%m-%dT00:00:00Z)&endDateTime=$(date -u +%Y-%m-%dT23:59:59Z)&\$orderby=start/dateTime asc" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
events = data.get('value', data) if isinstance(data, dict) else data
for e in events:
    start = e['start']['dateTime'][11:16]
    end = e['end']['dateTime'][11:16]
    all_day = ' (all day)' if e.get('isAllDay') else ''
    print(f\"{start}-{end}{all_day}  {e['subject']}\")
"
```

## Get a Single Event

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/events/EVENT_ID_HERE" --method get | python3 -c "
import sys, json, re
e = json.load(sys.stdin)
print(f\"Subject: {e['subject']}\")
print(f\"Start: {e['start']['dateTime']} ({e['start']['timeZone']})\")
print(f\"End: {e['end']['dateTime']} ({e['end']['timeZone']})\")
loc = e.get('location', {}).get('displayName', '')
if loc:
    print(f\"Location: {loc}\")
if e.get('organizer'):
    org = e['organizer']['emailAddress']
    print(f\"Organizer: {org['name']} <{org['address']}>\")
if e.get('attendees'):
    print('Attendees:')
    for a in e['attendees']:
        addr = a['emailAddress']
        status = a.get('status', {}).get('response', 'unknown')
        print(f\"  - {addr['name']} <{addr['address']}> ({status})\")
if e.get('body', {}).get('content'):
    body = e['body']['content']
    text = re.sub(r'<[^>]+>', '', body)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    if text.strip():
        print(f\"Body:\n{text.strip()}\")
"
```

## List Events with Select

Fetch only specific fields (works on calendar):

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=$(date -u +%Y-%m-%dT00:00:00Z)&endDateTime=$(date -u -v+7d +%Y-%m-%dT23:59:59Z)&\$select=subject,start,end,location,isAllDay&\$orderby=start/dateTime asc&\$top=50" --method get
```

## List All Calendars

```bash
m365 request --url "https://graph.microsoft.com/v1.0/me/calendars" --method get | python3 -c "
import sys, json
data = json.load(sys.stdin)
for c in data['value']:
    default = ' (default)' if c.get('isDefaultCalendar') else ''
    print(f\"{c['name']}{default}  ID: {c['id']}\")
"
```
