---
name: "gnarlysoft:outline"
description: Interact with Outline knowledge base API. Use when the user asks to create, read, update, delete, search, or manage documents, collections, comments, shares, users, or groups in Outline. Supports multiple Outline instances (e.g. gnarlysoft, technologymatch) via a leading instance argument. Also use for exporting, archiving, or organizing knowledge base content.
allowed-tools: Bash
model: sonnet
effort: medium
user-invocable: true
argument-hint: "[instance] <action> [options] (e.g., 'list documents', 'technologymatch search CRM Overhaul')"
---

# Outline Knowledge Base API

<context>
This skill provides full access to the Outline knowledge base via its REST API.
All endpoints use POST with JSON body. Authentication is via Bearer token.
Multiple Outline instances are supported (e.g. `gnarlysoft`, `technologymatch`).
</context>

<instructions>

## Instance Resolution (Multi-Instance Support)

This skill supports multiple Outline instances. The user may prefix any command with an instance name (e.g. `technologymatch search ...`). If no instance is given, the skill defaults to the legacy `OUTLINE_BASE_URL` / `OUTLINE_API_TOKEN` pair (which historically points at Gnarlysoft's Outline — backward compatible).

### Resolution rules

Before making any request, resolve `OUTLINE_BASE_URL` and `OUTLINE_API_TOKEN` for the current invocation:

1. If the first argument matches a known instance name (e.g. `gnarlysoft`, `technologymatch`, or any word that maps to a valid env var pair):
   - Uppercase the name → look up `OUTLINE_<NAME>_BASE_URL` and `OUTLINE_<NAME>_API_TOKEN`
   - If BOTH are set → use them; shift the argument off and proceed with the remaining command
   - If EITHER is missing → fall through to step 2 (the word may be part of the action, not an instance)
2. If no instance argument is present (or resolution in step 1 failed):
   - Use the legacy `OUTLINE_BASE_URL` / `OUTLINE_API_TOKEN` pair
3. If neither pair resolves to both values → STOP and warn the user which env vars are missing. Do not continue.

### Resolution helper (run at the start of every invocation)

```bash
resolve_outline_instance() {
  local first="${1:-}"
  if [[ -n "$first" ]]; then
    local upper
    upper=$(echo "$first" | tr '[:lower:]-' '[:upper:]_')
    local url_var="OUTLINE_${upper}_BASE_URL"
    local tok_var="OUTLINE_${upper}_API_TOKEN"
    if [[ -n "${!url_var:-}" && -n "${!tok_var:-}" ]]; then
      export OUTLINE_BASE_URL="${!url_var}"
      export OUTLINE_API_TOKEN="${!tok_var}"
      echo "__SHIFT__"
      return 0
    fi
  fi
  if [[ -z "${OUTLINE_BASE_URL:-}" || -z "${OUTLINE_API_TOKEN:-}" ]]; then
    echo "ERROR: No Outline instance resolved. Set either:" >&2
    echo "  - OUTLINE_BASE_URL and OUTLINE_API_TOKEN (default/legacy)" >&2
    echo "  - OUTLINE_<NAME>_BASE_URL and OUTLINE_<NAME>_API_TOKEN (named instance)" >&2
    return 1
  fi
  return 0
}
```

After calling `resolve_outline_instance "$first_arg"`:
- If stdout contains `__SHIFT__`, the first argument was consumed as an instance name — use remaining args as the command.
- Otherwise, treat all args as the command.

**SECURITY**: Never display, echo, or expose API tokens/secrets in chat output. Use `${OUTLINE_API_TOKEN}` variable reference only.

## Making Requests

All API calls follow this pattern:

```bash
curl -s -X POST "${OUTLINE_BASE_URL}/<endpoint>" \
  -H "Authorization: Bearer ${OUTLINE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '<json_body>'
```

Always pipe responses through `python3 -m json.tool` for readable output.

## Endpoint Reference (by Domain)

For full endpoint specs, parameters, and examples, see the domain files:

- **Documents** — list, create, read, update, delete, search, archive, move, export, access management → see [documents.md](documents.md)
- **Collections** — list, create, update, delete, export, access management → see [collections.md](collections.md)
- **Comments & Shares** — comment threads, public share links → see [comments-shares.md](comments-shares.md)
- **Users & Groups** — list, invite, manage memberships → see [users-groups.md](users-groups.md)
- **Search, Events, Attachments, File Operations** → see [misc.md](misc.md)

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

1. **Resolve the instance first** — call `resolve_outline_instance` at the start of every invocation.
2. **Credentials are env vars** — never print or echo tokens.
3. When creating documents, always set `"publish": true` unless the user explicitly wants a draft.
4. When listing, default to `limit: 25`. Use pagination for large result sets.
5. Present results in **table format** when listing multiple items.
6. When the user says "collection", map it to the Outline collection concept. When they say "doc" / "document" / "page", map it to documents.
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
