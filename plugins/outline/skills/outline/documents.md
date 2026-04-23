# Documents

All endpoints are POST with JSON body.

## List documents
```
POST /documents.list
Body: { "collectionId?": "uuid", "limit?": 25, "offset?": 0 }
```

## Get document info
```
POST /documents.info
Body: { "id": "uuid" }
```
Returns full document with markdown content in the `text` field.

## Create document
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
Content is in **Markdown**. Set `publish: true` to make it visible (otherwise draft).

### Embedding Excalidraw Diagrams

Outline supports inline Excalidraw diagrams using a `:::excalidraw` fenced block:

```markdown
:::excalidraw
{"type": "excalidraw", "version": 2, "source": "...", "elements": [...], "appState": {...}, "files": {}}
:::
```

The JSON must be on a single line inside the block. To embed an existing `.excalidraw` file, read it, minify the JSON, and wrap it. The JSON can be very large — for multiple diagrams, use `documents.update` with `append: true`.

## Update document
```
POST /documents.update
Body: { "id": "uuid", "title?": "string", "text?": "markdown content", "append?": true }
```
Use `append: true` to add content to the end instead of replacing.

## Delete document
```
POST /documents.delete
Body: { "id": "uuid", "permanent?": false }
```
Moves to trash by default. Set `permanent: true` to permanently delete.

## Search documents
```
POST /documents.search
Body: { "query": "search terms", "collectionId?": "uuid", "userId?": "uuid", "dateFilter?": "day|week|month|year", "limit?": 25 }
```
Returns results with `ranking` score and `context` snippet with highlights.

## Search titles only
```
POST /documents.search_titles
Body: { "query": "search terms" }
```

## Recently viewed
```
POST /documents.viewed
Body: { "limit?": 25 }
```

## List drafts / archived / deleted
```
POST /documents.drafts     Body: { "limit?": 25 }
POST /documents.archived   Body: { "collectionId?": "uuid", "limit?": 25 }
POST /documents.deleted    Body: { "limit?": 25 }
```

## Archive / restore
```
POST /documents.archive    Body: { "id": "uuid" }
POST /documents.restore    Body: { "id": "uuid" }
```

## Move / duplicate
```
POST /documents.move       Body: { "id": "uuid", "collectionId": "uuid", "parentDocumentId?": "uuid" }
POST /documents.duplicate  Body: { "id": "uuid", "collectionId?": "uuid", "recursive?": false }
```

## Unpublish (back to draft)
```
POST /documents.unpublish
Body: { "id": "uuid" }
```

## Export
```
POST /documents.export
Body: { "id": "uuid" }
```
Returns markdown content.

## Import from file
```
POST /documents.import
```
Multipart form upload.

## Convert to template
```
POST /documents.templatize
Body: { "id": "uuid" }
```

## AI-powered Q&A
```
POST /documents.answerQuestion
Body: { "query": "your question" }
```

## Manage document access
```
POST /documents.add_user       Body: { "id": "uuid", "userId": "uuid" }
POST /documents.remove_user    Body: { "id": "uuid", "userId": "uuid" }
POST /documents.add_group      Body: { "id": "uuid", "groupId": "uuid" }
POST /documents.remove_group   Body: { "id": "uuid", "groupId": "uuid" }
POST /documents.users          Body: { "id": "uuid" }
POST /documents.memberships    Body: { "id": "uuid" }
```

## Empty trash
```
POST /documents.empty_trash
Body: {}
```
