---
name: outline
description: Interact with Outline knowledge base API. Use when the user asks to create, read, update, delete, search, or manage documents, collections, comments, shares, users, or groups in Outline. Also use for exporting, archiving, or organizing knowledge base content.
allowed-tools: Bash
user-invocable: true
argument-hint: "<action> [options] (e.g., 'list documents', 'create doc in Engineering', 'search for API')"
---

# Outline Knowledge Base API

<context>
This skill provides full access to the Outline knowledge base via its REST API.
All endpoints use POST with JSON body. Authentication is via Bearer token.
</context>

<instructions>

## Configuration

Credentials are stored in `${CLAUDE_SKILL_DIR}/.env` and loaded via `get-token.sh`:

```bash
OUTLINE_BASE_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_BASE_URL)
OUTLINE_API_TOKEN=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_API_TOKEN)
```

If either variable is missing or empty, the script will error. Tell the user to populate the `.env` file at `${CLAUDE_SKILL_DIR}/.env`:

```
OUTLINE_BASE_URL=https://<workspace>.getoutline.com/api
OUTLINE_API_TOKEN=ol_api_...
```

**SECURITY**: Never display, echo, or expose API tokens/secrets in chat output. Read tokens silently and use them only within command variables and headers. Never print token values to stdout or include them in responses to the user.

## Making Requests

All API calls follow this pattern:

```bash
OUTLINE_BASE_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_BASE_URL)
OUTLINE_API_TOKEN=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_API_TOKEN)

curl -s -X POST "${OUTLINE_BASE_URL}/<endpoint>" \
  -H "Authorization: Bearer ${OUTLINE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '<json_body>'
```

Always pipe responses through `python3 -m json.tool` for readable output.

## Available Endpoints

### Documents

#### List documents
```
POST /documents.list
Body: { "collectionId?": "uuid", "limit?": 25, "offset?": 0 }
```

#### Get document info
```
POST /documents.info
Body: { "id": "uuid" }
```
Returns full document with markdown content in the `text` field.

#### Create document
```
POST /documents.create
Body: {
  "title": "string",
  "text": "markdown content",
  "collectionId": "uuid",
  "parentDocumentId?": "uuid",
  "publish?": true
}
```
Content is in **Markdown** format. Set `publish: true` to make it visible (otherwise it's a draft).

#### Update document
```
POST /documents.update
Body: {
  "id": "uuid",
  "title?": "string",
  "text?": "markdown content",
  "append?": true
}
```
Use `append: true` to add content to the end instead of replacing.

#### Delete document
```
POST /documents.delete
Body: { "id": "uuid", "permanent?": false }
```
Moves to trash by default. Set `permanent: true` to permanently delete.

#### Search documents
```
POST /documents.search
Body: { "query": "search terms", "collectionId?": "uuid", "limit?": 25 }
```
Returns results with `ranking` score and `context` snippet with highlights.

#### Search titles only
```
POST /documents.search_titles
Body: { "query": "search terms" }
```

#### Get recently viewed
```
POST /documents.viewed
Body: { "limit?": 25 }
```

#### List drafts
```
POST /documents.drafts
Body: { "limit?": 25 }
```

#### List archived
```
POST /documents.archived
Body: { "collectionId?": "uuid", "limit?": 25 }
```

#### List deleted
```
POST /documents.deleted
Body: { "limit?": 25 }
```

#### Archive document
```
POST /documents.archive
Body: { "id": "uuid" }
```

#### Restore document
```
POST /documents.restore
Body: { "id": "uuid" }
```

#### Move document
```
POST /documents.move
Body: { "id": "uuid", "collectionId": "uuid", "parentDocumentId?": "uuid" }
```

#### Duplicate document
```
POST /documents.duplicate
Body: { "id": "uuid", "collectionId?": "uuid", "recursive?": false }
```

#### Unpublish document (back to draft)
```
POST /documents.unpublish
Body: { "id": "uuid" }
```

#### Export document
```
POST /documents.export
Body: { "id": "uuid" }
```
Returns markdown content.

#### Import document from file
```
POST /documents.import
```
Multipart form upload.

#### Convert to template
```
POST /documents.templatize
Body: { "id": "uuid" }
```

#### AI-powered Q&A
```
POST /documents.answerQuestion
Body: { "query": "your question" }
```

#### Manage document access
```
POST /documents.add_user       Body: { "id": "uuid", "userId": "uuid" }
POST /documents.remove_user    Body: { "id": "uuid", "userId": "uuid" }
POST /documents.add_group      Body: { "id": "uuid", "groupId": "uuid" }
POST /documents.remove_group   Body: { "id": "uuid", "groupId": "uuid" }
POST /documents.users          Body: { "id": "uuid" }
POST /documents.memberships    Body: { "id": "uuid" }
```

#### Empty trash
```
POST /documents.empty_trash
Body: {}
```

### Collections

#### List collections
```
POST /collections.list
Body: { "limit?": 25, "offset?": 0 }
```

#### Get collection info
```
POST /collections.info
Body: { "id": "uuid" }
```

#### Get document tree in collection
```
POST /collections.documents
Body: { "id": "uuid" }
```
Returns the hierarchical document structure.

#### Create collection
```
POST /collections.create
Body: {
  "name": "string",
  "description?": "string",
  "icon?": "string (emoji or icon name e.g. 'collection', 'beaker')",
  "color?": "#hex",
  "permission?": "read_write"
}
```
`permission` values: `read_write`, `read`, or `null` (private).

#### Update collection
```
POST /collections.update
Body: { "id": "uuid", "name?": "string", "description?": "string", "icon?": "string", "color?": "#hex" }
```

#### Delete collection
```
POST /collections.delete
Body: { "id": "uuid" }
```
Deletes the collection and all documents within it.

#### Export collection
```
POST /collections.export
Body: { "id": "uuid", "format?": "outline-markdown" }
```

#### Export all collections
```
POST /collections.export_all
Body: { "format?": "outline-markdown" }
```

#### Manage collection access
```
POST /collections.add_user        Body: { "id": "uuid", "userId": "uuid" }
POST /collections.remove_user     Body: { "id": "uuid", "userId": "uuid" }
POST /collections.memberships     Body: { "id": "uuid" }
POST /collections.add_group       Body: { "id": "uuid", "groupId": "uuid" }
POST /collections.remove_group    Body: { "id": "uuid", "groupId": "uuid" }
POST /collections.group_memberships Body: { "id": "uuid" }
```

### Comments

#### List comments
```
POST /comments.list
Body: { "documentId": "uuid", "limit?": 25 }
```

#### Get comment info
```
POST /comments.info
Body: { "id": "uuid" }
```

#### Create comment
```
POST /comments.create
Body: {
  "documentId": "uuid",
  "data": {
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": "Comment text here" }]
      }
    ]
  },
  "parentCommentId?": "uuid"
}
```
Comment body uses ProseMirror JSON format. `parentCommentId` for replies.

#### Update comment
```
POST /comments.update
Body: { "id": "uuid", "data": { ...prosemirror json... } }
```

#### Delete comment
```
POST /comments.delete
Body: { "id": "uuid" }
```

### Shares

#### List shares
```
POST /shares.list
Body: { "limit?": 25 }
```

#### Get share info
```
POST /shares.info
Body: { "id": "uuid" }
```

#### Create public share link
```
POST /shares.create
Body: { "documentId": "uuid" }
```
Returns a share object with a public `url`.

#### Update share
```
POST /shares.update
Body: { "id": "uuid", "includeChildDocuments?": true, "published?": true }
```

#### Revoke share
```
POST /shares.revoke
Body: { "id": "uuid" }
```

### Search

#### Full-text search
```
POST /documents.search
Body: {
  "query": "search terms",
  "collectionId?": "uuid",
  "userId?": "uuid",
  "dateFilter?": "day|week|month|year",
  "limit?": 25
}
```

#### Title search
```
POST /documents.search_titles
Body: { "query": "search terms" }
```

#### AI answer
```
POST /documents.answerQuestion
Body: { "query": "your question in natural language" }
```

### Users

#### Get current user
```
POST /auth.info
Body: {}
```

#### List users
```
POST /users.list
Body: { "limit?": 25 }
```

#### Get user info
```
POST /users.info
Body: { "id": "uuid" }
```

#### Invite users
```
POST /users.invite
Body: { "invites": [{ "email": "user@example.com", "name": "Name", "role": "member" }] }
```

### Groups

#### List groups
```
POST /groups.list
Body: { "limit?": 25 }
```

#### Create group
```
POST /groups.create
Body: { "name": "string" }
```

#### Update/delete group
```
POST /groups.update   Body: { "id": "uuid", "name": "string" }
POST /groups.delete   Body: { "id": "uuid" }
```

#### Manage group members
```
POST /groups.memberships    Body: { "id": "uuid" }
POST /groups.add_user       Body: { "id": "uuid", "userId": "uuid" }
POST /groups.remove_user    Body: { "id": "uuid", "userId": "uuid" }
```

### Events (Audit Log)

```
POST /events.list
Body: { "name?": "documents.create", "documentId?": "uuid", "collectionId?": "uuid", "limit?": 25 }
```

### Attachments

#### Upload file
```
POST /attachments.create
```
Multipart form upload. Returns a signed URL.

#### Delete attachment
```
POST /attachments.delete
Body: { "id": "uuid" }
```

### File Operations (Bulk Export/Import)

```
POST /fileOperations.list     Body: { "type": "export" }
POST /fileOperations.info     Body: { "id": "uuid" }
POST /fileOperations.redirect Body: { "id": "uuid" }
POST /fileOperations.delete   Body: { "id": "uuid" }
```

## Response Format

All responses follow this structure:
```json
{
  "data": { ... },
  "policies": [{ "id": "uuid", "abilities": { ... } }],
  "status": 200,
  "ok": true
}
```

List endpoints include pagination:
```json
{
  "pagination": { "limit": 25, "offset": 0, "total": 10 },
  "data": [ ... ]
}
```

## Behavior Guidelines

1. **Always load credentials via get-token.sh first**. Run `${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_BASE_URL > /dev/null && ${CLAUDE_SKILL_DIR}/scripts/get-token.sh OUTLINE_API_TOKEN > /dev/null && echo "OK"` to verify they're set without printing secrets.
2. **Never print the API token** in output. Use `${OUTLINE_API_TOKEN}` variable reference only.
3. When creating documents, always set `"publish": true` unless the user explicitly wants a draft.
4. When listing, default to `limit: 25`. Use pagination for large result sets.
5. Present results in **table format** when listing multiple items.
6. When the user says "collection", map it to the Outline collection concept. When they say "doc" or "document" or "page", map it to documents.
7. For search, prefer `documents.search` for content search and `documents.search_titles` for quick title lookups.
8. When creating nested documents, first resolve the parent document ID, then use `parentDocumentId`.
9. When the user asks to move content, confirm the target collection exists first.

## Failure Notification (MANDATORY)

If any step, command, API call, or tool in this workflow fails or does not work as expected, you MUST immediately notify the user with:
1. What failed
2. The error or unexpected behavior observed
3. What you plan to do instead (if anything)

Do NOT silently fall back to alternative approaches without informing the user first.

## Self-Update Protocol

If you discovered something new during this task (failures, bugs, edge cases, better approaches, new IDs or mappings), update this SKILL.md file directly without waiting for the user to ask. Skip if the task was routine with no new findings.

</instructions>
