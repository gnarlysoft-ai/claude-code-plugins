# Outline Skill

Claude Code skill for interacting with the [GnarlySoft Outline wiki](https://wiki.gnarlysoft.com/) via the REST API.

## Setup

### 1. Create the `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then fill in your API token:

```
OUTLINE_BASE_URL=https://wiki.gnarlysoft.com/api   # pre-configured
OUTLINE_API_TOKEN=ol_api_...                        # fill this in
```

### 2. Get your API token

1. Log into [wiki.gnarlysoft.com](https://wiki.gnarlysoft.com/)
2. Go to **Settings > API** (or navigate to `https://wiki.gnarlysoft.com/settings/api`)
3. Click **New API Key**
4. Copy the token into your `.env` file

### 3. Verify the connection

Invoke the skill in Claude Code:

```
/outline list collections
```

If configured correctly, you'll see a table of your collections.

## Usage

The skill is invoked via `/outline` followed by natural language:

| Example | What it does |
|---------|-------------|
| `/outline list collections` | List all collections |
| `/outline search "onboarding"` | Full-text search across all documents |
| `/outline create doc "Meeting Notes" in Sales` | Create a new document in the Sales collection |
| `/outline list docs in SIP` | List documents in the SIP collection |
| `/outline get doc <title>` | Fetch a specific document's content |
| `/outline move doc <title> to <collection>` | Move a document to another collection |
| `/outline delete doc <title>` | Move a document to trash |

### Supported operations

- **Documents**: list, create, read, update, delete, search, archive, restore, move, duplicate, export
- **Collections**: list, create, update, delete, export, manage access
- **Comments**: list, create, update, delete
- **Shares**: create public links, revoke access
- **Users & Groups**: list, invite, manage memberships
- **Search**: full-text search, title search, AI-powered Q&A

## File Structure

```
skills/outline/
  SKILL.md          # Skill definition with full API reference
  README.md         # This file
  .env.example      # Template — copy to .env and add your token
  .env              # Credentials (not committed)
  scripts/
    get-token.sh    # Loads env vars from .env securely
```

## API Token Permissions

Your API token's permissions determine what operations are available. Common limitations:

| Permission | Required for |
|-----------|-------------|
| `read` | Listing and reading documents/collections |
| `createDocument` | Creating new documents |
| `updateDocument` | Editing documents |
| `deleteDocument` | Deleting documents |
| `delete` (collection) | Deleting collections (requires admin on that collection) |
| `export` | Exporting collections |

If an operation returns a 403 error, your token likely lacks the required permission. Use an admin-level token or perform the action in the Outline web UI.

## Security

- The `.env` file is gitignored and never committed
- API tokens are loaded via `get-token.sh` and never printed to chat output
- Claude reads tokens into shell variables only — they are not displayed
