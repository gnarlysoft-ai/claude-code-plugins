# Mail and Calendar

## Contents

- [Email](#email) — Send, read, draft, reply, forward, move
- [Mail Folders](#mail-folders) — List, create, well-known folders
- [Calendar](#calendar) — Events, availability, scheduling

## Email

### List Messages

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/messages?\$top=25&\$orderby=receivedDateTime%20desc&\$select=subject,from,receivedDateTime,isRead' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Full Message

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}?\$select=subject,body,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments' \
  -H "Authorization: Bearer $TOKEN"
```

### Send Email

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/sendMail' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "message": {
      "subject": "Project Update",
      "body": {
        "contentType": "HTML",
        "content": "<p>Here is the latest update.</p>"
      },
      "toRecipients": [
        {"emailAddress": {"address": "recipient@example.com", "name": "Jane Smith"}}
      ],
      "ccRecipients": [
        {"emailAddress": {"address": "manager@example.com"}}
      ]
    },
    "saveToSentItems": true
  }'
```

### Create Draft

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/messages' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Draft Subject",
    "body": {"contentType": "Text", "content": "Draft body text."},
    "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}]
  }'
```

### Send Draft

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}/send' \
  -H "Authorization: Bearer $TOKEN"
```

### Reply to Message

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}/reply' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "message": {
      "toRecipients": [{"emailAddress": {"address": "sender@example.com"}}]
    },
    "comment": "Thanks for the update. I will review and respond shortly."
  }'
```

### Forward Message

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}/forward' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "toRecipients": [{"emailAddress": {"address": "colleague@example.com"}}],
    "comment": "FYI — see the message below."
  }'
```

### Update Message Properties

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "isRead": true,
    "categories": ["Important"],
    "flag": {"flagStatus": "flagged"}
  }'
```

### Move Message to Folder

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/messages/{msgId}/move' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"destinationId": "archive"}'
```

Use a folder ID or well-known folder name as `destinationId`.

## Mail Folders

### List Folders

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/mailFolders?\$select=displayName,id,totalItemCount,unreadItemCount' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Folder

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/mailFolders' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"displayName": "Project Alpha"}'
```

### Well-Known Folder Names

Use these as IDs directly in URLs (e.g., `/users/{id}/mailFolders/inbox`):
- `inbox`
- `drafts`
- `sentitems`
- `deleteditems`
- `archive`
- `junkemail`

## Calendar

### List Events in a Date Range

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/calendarview?\$select=subject,start,end,organizer,attendees&startDateTime=2025-03-01T00:00:00Z&endDateTime=2025-03-31T23:59:59Z&\$top=50' \
  -H "Authorization: Bearer $TOKEN" \
  -H "Prefer: outlook.timezone=\"America/Chicago\""
```

The `startDateTime` and `endDateTime` parameters are required for `calendarview`.

### Create Event

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/events' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Sprint Planning",
    "body": {"contentType": "HTML", "content": "<p>Weekly sprint planning meeting.</p>"},
    "start": {"dateTime": "2025-03-20T09:00:00", "timeZone": "America/Chicago"},
    "end": {"dateTime": "2025-03-20T10:00:00", "timeZone": "America/Chicago"},
    "location": {"displayName": "Conference Room A"},
    "attendees": [
      {
        "emailAddress": {"address": "colleague@example.com", "name": "Colleague"},
        "type": "required"
      },
      {
        "emailAddress": {"address": "manager@example.com", "name": "Manager"},
        "type": "optional"
      }
    ],
    "isOnlineMeeting": true,
    "onlineMeetingProvider": "teamsForBusiness"
  }'
```

### Update Event

```bash
curl -X PATCH 'https://graph.microsoft.com/v1.0/users/{id}/events/{eventId}' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"subject": "Updated Sprint Planning", "location": {"displayName": "Room B"}}'
```

### Delete Event

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/users/{id}/events/{eventId}' \
  -H "Authorization: Bearer $TOKEN"
```

### Check Availability (Get Schedule)

Check free/busy status for multiple users:

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/calendar/getSchedule' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "schedules": ["user1@example.com", "user2@example.com"],
    "startTime": {"dateTime": "2025-03-20T08:00:00", "timeZone": "America/Chicago"},
    "endTime": {"dateTime": "2025-03-20T18:00:00", "timeZone": "America/Chicago"},
    "availabilityViewInterval": 30
  }'
```

### Find Meeting Times

Let Graph suggest available time slots:

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/users/{id}/findMeetingTimes' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "attendees": [
      {"emailAddress": {"address": "colleague@example.com"}, "type": "required"}
    ],
    "timeConstraint": {
      "timeslots": [
        {
          "start": {"dateTime": "2025-03-20T08:00:00", "timeZone": "America/Chicago"},
          "end": {"dateTime": "2025-03-20T18:00:00", "timeZone": "America/Chicago"}
        }
      ]
    },
    "meetingDuration": "PT1H",
    "maxCandidates": 5
  }'
```
