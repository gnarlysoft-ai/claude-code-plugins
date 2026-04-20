# Outline Skill

Interact with one or more Outline knowledge bases via the REST API.

## Usage

`/outline [instance] <action>` — e.g. `/outline list collections`, `/outline technologymatch search CRM Overhaul`.

## Env vars

- Default: `OUTLINE_BASE_URL`, `OUTLINE_API_TOKEN`
- Named: `OUTLINE_<NAME>_BASE_URL`, `OUTLINE_<NAME>_API_TOKEN`

## Files

- `SKILL.md` — instance resolution, behavior rules
- `documents.md`, `collections.md`, `comments-shares.md`, `users-groups.md`, `misc.md` — endpoint reference
