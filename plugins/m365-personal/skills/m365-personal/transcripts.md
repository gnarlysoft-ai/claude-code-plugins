# Meeting Transcripts Reference

## Required Permissions

| Permission | Type | Description |
|------------|------|-------------|
| OnlineMeetings.Read | Delegated | Required to list meetings and transcripts |
| OnlineMeetingTranscript.Read.All | Application | Optional, for app-level transcript access |

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me/onlineMeetings | List online meetings |
| GET | /me/onlineMeetings/{meetingId}/transcripts | List transcripts for a meeting |
| GET | /me/onlineMeetings/{meetingId}/transcripts/{transcriptId}/content | Download transcript content |

## Meeting Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Meeting ID |
| subject | string | Meeting subject |
| startDateTime | string | ISO 8601 start time |
| endDateTime | string | ISO 8601 end time |
| allowTranscription | boolean | Whether transcription was enabled |
| recordAutomatically | boolean | Whether recording starts automatically |
| joinWebUrl | string | Teams join URL |
| participants | object | Organizer and attendees |

## Transcript Object Fields

| Field | Type | Description |
|-------|------|-------------|
| id | string | Transcript ID |
| meetingId | string | Parent meeting ID |
| createdDateTime | string | ISO 8601 creation time |
| transcriptContentUrl | string | URL to download the transcript |

## Step-by-Step Workflow

### 1. List Recent Meetings

```bash
m365 teams meeting list --output json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data:
    subj = m.get('subject', 'No subject')
    start = m.get('startDateTime', 'N/A')[:16]
    mid = m.get('id', 'N/A')
    print(f\"{start}  {subj}  ID: {mid}\")
"
```

### 2. List Transcripts for a Meeting

```bash
m365 teams meeting transcript list --meetingId MEETING_ID_HERE --output json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data:
    print(f\"Transcript ID: {t['id']}  Created: {t.get('createdDateTime', 'N/A')[:16]}\")
"
```

### 3. Download Transcript

Download the VTT transcript file:

```bash
m365 teams meeting transcript get --meetingId MEETING_ID_HERE --id TRANSCRIPT_ID_HERE --outputFile /tmp/transcript.vtt
```

### 4. Parse VTT to Plain Text

VTT files contain timestamps and speaker labels in `<v Speaker>text</v>` format:

```
WEBVTT

00:00:05.000 --> 00:00:10.000
<v John Doe>Good morning everyone, let's get started.</v>

00:00:10.500 --> 00:00:15.000
<v Jane Smith>Thanks John, I have the quarterly update ready.</v>
```

Parse to readable plain text:

```bash
python3 -c "
import re, sys
with open('/tmp/transcript.vtt', 'r') as f:
    content = f.read()
current_speaker = None
for line in content.split('\n'):
    match = re.match(r'<v ([^>]+)>(.*)</v>', line)
    if match:
        speaker = match.group(1)
        text = match.group(2)
        if speaker != current_speaker:
            current_speaker = speaker
            print(f'\n{speaker}:')
        print(f'  {text}')
"
```

## List Meetings with Transcript Availability

Check which recent meetings have transcripts:

```bash
m365 teams meeting list --output json | python3 -c "
import sys, json, subprocess
data = json.load(sys.stdin)
for m in data[:10]:
    mid = m.get('id')
    subj = m.get('subject', 'No subject')
    start = m.get('startDateTime', 'N/A')[:16]
    result = subprocess.run(
        ['m365', 'teams', 'meeting', 'transcript', 'list', '--meetingId', mid, '--output', 'json'],
        capture_output=True, text=True
    )
    try:
        transcripts = json.loads(result.stdout)
        count = len(transcripts)
    except (json.JSONDecodeError, TypeError):
        count = 0
    status = f'{count} transcript(s)' if count > 0 else 'No transcripts'
    print(f\"{start}  {subj}  [{status}]\")
"
```

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Empty transcript list | Transcription was not enabled for the meeting | Meeting must have `allowTranscription: true` and transcription must have been started during the call |
| 403 Forbidden | Missing OnlineMeetings.Read permission | Ensure the delegated permission is consented; re-login with `m365 login --authType browser` |
| No meetings returned | Wrong date range or no online meetings | `m365 teams meeting list` returns recent meetings; check that the meetings were Teams online meetings (not in-person or other platforms) |
| Transcript download fails | Invalid meeting/transcript ID | Verify IDs by listing meetings then transcripts for the target meeting |
