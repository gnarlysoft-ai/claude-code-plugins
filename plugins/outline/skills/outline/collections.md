# Collections

All endpoints are POST with JSON body.

## List collections
```
POST /collections.list
Body: { "limit?": 25, "offset?": 0 }
```

## Get collection info
```
POST /collections.info
Body: { "id": "uuid" }
```

## Get document tree in collection
```
POST /collections.documents
Body: { "id": "uuid" }
```
Returns the hierarchical document structure.

## Create collection
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

## Update collection
```
POST /collections.update
Body: { "id": "uuid", "name?": "string", "description?": "string", "icon?": "string", "color?": "#hex" }
```

## Delete collection
```
POST /collections.delete
Body: { "id": "uuid" }
```
Deletes the collection and all documents within it.

## Export
```
POST /collections.export       Body: { "id": "uuid", "format?": "outline-markdown" }
POST /collections.export_all   Body: { "format?": "outline-markdown" }
```

## Manage collection access
```
POST /collections.add_user           Body: { "id": "uuid", "userId": "uuid" }
POST /collections.remove_user        Body: { "id": "uuid", "userId": "uuid" }
POST /collections.memberships        Body: { "id": "uuid" }
POST /collections.add_group          Body: { "id": "uuid", "groupId": "uuid" }
POST /collections.remove_group       Body: { "id": "uuid", "groupId": "uuid" }
POST /collections.group_memberships  Body: { "id": "uuid" }
```
