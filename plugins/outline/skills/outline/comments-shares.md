# Comments & Shares

All endpoints are POST with JSON body.

## Comments

### List
```
POST /comments.list
Body: { "documentId": "uuid", "limit?": 25 }
```

### Info
```
POST /comments.info
Body: { "id": "uuid" }
```

### Create
```
POST /comments.create
Body: {
  "documentId": "uuid",
  "data": {
    "type": "doc",
    "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Comment text here" }] }
    ]
  },
  "parentCommentId?": "uuid"
}
```
Comment body uses ProseMirror JSON format. `parentCommentId` for replies.

### Update
```
POST /comments.update
Body: { "id": "uuid", "data": { ...prosemirror json... } }
```

### Delete
```
POST /comments.delete
Body: { "id": "uuid" }
```

## Shares

### List
```
POST /shares.list
Body: { "limit?": 25 }
```

### Info
```
POST /shares.info
Body: { "id": "uuid" }
```

### Create public share link
```
POST /shares.create
Body: { "documentId": "uuid" }
```
Returns a share object with a public `url`.

### Update share
```
POST /shares.update
Body: { "id": "uuid", "includeChildDocuments?": true, "published?": true }
```

### Revoke share
```
POST /shares.revoke
Body: { "id": "uuid" }
```
