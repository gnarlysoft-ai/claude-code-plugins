# Search, Events, Attachments, File Operations

## Search

### Full-text search
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

### Title search
```
POST /documents.search_titles
Body: { "query": "search terms" }
```

### AI answer
```
POST /documents.answerQuestion
Body: { "query": "your question in natural language" }
```

## Events (Audit Log)

```
POST /events.list
Body: { "name?": "documents.create", "documentId?": "uuid", "collectionId?": "uuid", "limit?": 25 }
```

## Attachments

### Upload
```
POST /attachments.create
```
Multipart form upload. Returns a signed URL.

### Delete
```
POST /attachments.delete
Body: { "id": "uuid" }
```

## File Operations (Bulk Export/Import)

```
POST /fileOperations.list      Body: { "type": "export" }
POST /fileOperations.info      Body: { "id": "uuid" }
POST /fileOperations.redirect  Body: { "id": "uuid" }
POST /fileOperations.delete    Body: { "id": "uuid" }
```
