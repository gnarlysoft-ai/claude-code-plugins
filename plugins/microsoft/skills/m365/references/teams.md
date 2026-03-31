# Microsoft Teams

## Contents

- [Teams](#teams) — CRUD operations
- [Channels](#channels) — Create, list, messaging
- [Chat](#chat) — 1:1 and group chat
- [Tabs](#tabs) — Add and manage tabs

## Teams

### List Teams

```bash
curl 'https://graph.microsoft.com/v1.0/teams?\$select=id,displayName,description' \
  -H "Authorization: Bearer $TOKEN"
```

Note: Listing all teams requires the `Team.ReadBasic.All` permission. Alternatively, list groups with `resourceProvisioningOptions` containing `Team`:

```bash
curl 'https://graph.microsoft.com/v1.0/groups?\$filter=resourceProvisioningOptions/Any(x:x%20eq%20'\''Team'\'')&\$select=id,displayName' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Team

```bash
curl 'https://graph.microsoft.com/v1.0/teams/{teamId}?\$select=id,displayName,description,isArchived' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Team

Create a team from scratch (also creates the backing M365 group):

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/teams' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "template@odata.bind": "https://graph.microsoft.com/v1.0/teamsTemplates('\''standard'\'')",
    "displayName": "Engineering Team",
    "description": "Team for engineering collaboration",
    "members": [
      {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "roles": ["owner"],
        "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId}"
      }
    ]
  }'
```

Returns `202 Accepted` with a `Location` header containing the async operation URL. Poll it until status is `succeeded`.

### Create Team from Existing Group

```bash
curl -X PUT 'https://graph.microsoft.com/v1.0/groups/{groupId}/team' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "memberSettings": {"allowCreateUpdateChannels": true},
    "messagingSettings": {"allowUserEditMessages": true},
    "funSettings": {"allowGiphy": true}
  }'
```

### Delete Team

```bash
curl -X DELETE 'https://graph.microsoft.com/v1.0/groups/{groupId}' \
  -H "Authorization: Bearer $TOKEN"
```

Deleting a team is done by deleting its backing group.

## Channels

### List Channels

```bash
curl 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels?\$select=id,displayName,membershipType' \
  -H "Authorization: Bearer $TOKEN"
```

### Create Channel

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Design Reviews",
    "description": "Channel for design review discussions",
    "membershipType": "standard"
  }'
```

Membership types: `standard` (visible to all), `private` (invite only), `shared` (cross-team).

### List Channel Messages

```bash
curl 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages?\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

### Send Channel Message

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "body": {
      "contentType": "html",
      "content": "<p>Deployment to production is complete.</p>"
    }
  }'
```

### Reply to a Channel Message

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages/{messageId}/replies' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "body": {
      "contentType": "text",
      "content": "Confirmed — all health checks are passing."
    }
  }'
```

## Chat

### List User's Chats

```bash
curl 'https://graph.microsoft.com/v1.0/users/{id}/chats?\$select=id,topic,chatType&\$top=25' \
  -H "Authorization: Bearer $TOKEN"
```

### Create One-on-One Chat

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/chats' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "chatType": "oneOnOne",
    "members": [
      {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "roles": ["owner"],
        "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId1}"
      },
      {
        "@odata.type": "#microsoft.graph.aadUserConversationMember",
        "roles": ["owner"],
        "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId2}"
      }
    ]
  }'
```

### Create Group Chat

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/chats' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "chatType": "group",
    "topic": "Project Alpha Discussion",
    "members": [
      {"@odata.type": "#microsoft.graph.aadUserConversationMember", "roles": ["owner"], "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId1}"},
      {"@odata.type": "#microsoft.graph.aadUserConversationMember", "roles": ["guest"], "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId2}"},
      {"@odata.type": "#microsoft.graph.aadUserConversationMember", "roles": ["guest"], "user@odata.bind": "https://graph.microsoft.com/v1.0/users/{userId3}"}
    ]
  }'
```

### Send Chat Message

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/chats/{chatId}/messages' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "body": {
      "contentType": "text",
      "content": "Meeting has been moved to 3 PM."
    }
  }'
```

## Tabs

### List Tabs in a Channel

```bash
curl 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/tabs?\$expand=teamsApp' \
  -H "Authorization: Bearer $TOKEN"
```

### Add a Website Tab

```bash
curl -X POST 'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/tabs' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Project Dashboard",
    "teamsApp@odata.bind": "https://graph.microsoft.com/v1.0/appCatalogs/teamsApps/com.microsoft.teamspace.tab.web",
    "configuration": {
      "entityId": null,
      "contentUrl": "https://dashboard.example.com",
      "websiteUrl": "https://dashboard.example.com",
      "removeUrl": null
    }
  }'
```

Common built-in tab app IDs:
- Website: `com.microsoft.teamspace.tab.web`
- SharePoint page: `2a527703-1f6f-4559-a332-d8a7d288cd88`
- Planner: `com.microsoft.teamspace.tab.planner`
- OneNote: `0d820ecd-def2-4297-adad-78056cde7c78`
