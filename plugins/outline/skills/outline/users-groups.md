# Users & Groups

All endpoints are POST with JSON body.

## Users

### Get current user
```
POST /auth.info
Body: {}
```

### List users
```
POST /users.list
Body: { "limit?": 25 }
```

### Get user info
```
POST /users.info
Body: { "id": "uuid" }
```

### Invite users
```
POST /users.invite
Body: { "invites": [{ "email": "user@example.com", "name": "Name", "role": "member" }] }
```

## Groups

### List groups
```
POST /groups.list
Body: { "limit?": 25 }
```

### Create group
```
POST /groups.create
Body: { "name": "string" }
```

### Update / delete group
```
POST /groups.update   Body: { "id": "uuid", "name": "string" }
POST /groups.delete   Body: { "id": "uuid" }
```

### Manage group members
```
POST /groups.memberships    Body: { "id": "uuid" }
POST /groups.add_user       Body: { "id": "uuid", "userId": "uuid" }
POST /groups.remove_user    Body: { "id": "uuid", "userId": "uuid" }
```
