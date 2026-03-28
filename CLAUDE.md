# GnarlySoft Claude Code Plugins

Marketplace of Claude Code plugins by GnarlySoft AI. Directory-based marketplace registered in user settings as `gnarlysoft-plugins`.

## Architecture

```
plugins/
  schedule/       # Repeating prompt schedules (Python, uses uv)
  outline/        # Outline knowledge base API integration
  utils/          # Code review, security, design, and CLAUDE.md management
  microsoft/      # Microsoft 365 (Graph API) and Azure (Resource Manager API)
```

Each plugin follows the Claude Code plugin structure:
- `.claude-plugin/plugin.json` — plugin metadata (name, version, description, author)
- `agents/` — agent definitions (`.md` files with frontmatter)
- `commands/` — slash commands (`.md` files)
- `skills/` — skills with `SKILL.md` and optional `references/` subdirectory
- `hooks/` — hook definitions (`hooks.json`)

Marketplace root: `.claude-plugin/marketplace.json` — lists all plugins with name, source path, and description.

## Conventions

### `from` field

Skills and commands copied from other plugins/marketplaces **must** include a `from` field in the frontmatter as the **last field**. This tracks provenance.

```yaml
---
name: example-skill
description: What it does
tools: Read, Grep
from: marketplace-name/plugin-name
---
```

Current sources used:
- `everything-claude-code` — ECC skills/commands
- `impeccable` — design/UI skills
- `claude-plugins-official/claude-md-management` — CLAUDE.md management

### Plugin naming

Plugin JSON `name` field is prefixed with `gnarlysoft-` (e.g., `gnarlysoft-utils`, `gnarlysoft-schedule`).

### Agent model

Agents that don't need Opus use `model: sonnet` in frontmatter to reduce cost.

## Commands

| Command | Plugin | Description |
|---------|--------|-------------|
| `/code-review` | utils | Run code review on changes |
| `/e2e` | utils | Generate and run E2E tests with Playwright |
| `/revise-claude-md` | utils | Capture session learnings into CLAUDE.md |

## Agents

| Agent | Plugin | Description |
|-------|--------|-------------|
| `code-reviewer` | utils | Code quality, security, and maintainability review |
| `security-reviewer` | utils | Security vulnerability detection and remediation |
| `e2e-runner` | utils | E2E testing with Playwright |

## Skills

| Skill | Plugin | Source |
|-------|--------|--------|
| `loop` | schedule | — |
| `outline` | outline | — |
| `audit` | utils | `impeccable` |
| `critique` | utils | `impeccable` |
| `optimize` | utils | `impeccable` |
| `polish` | utils | `impeccable` |
| `quieter` | utils | `impeccable` |
| `teach-impeccable` | utils | `impeccable` |
| `security-review` | utils | `everything-claude-code` |
| `claude-md-improver` | utils | `claude-plugins-official/claude-md-management` |
| `m365` | microsoft | — |
| `azure` | microsoft | — |

## Gotchas

- The `schedule` plugin uses Python with `uv` — it has a `.venv/` directory and `pyproject.toml`
- Plugin names in `marketplace.json` differ from `plugin.json` names (e.g., `utils` vs `gnarlysoft-utils`)
- Skills from `impeccable` (audit, critique, polish, etc.) don't have the `from` field on all of them yet
- `plugin.json` is the single source of truth for plugin versions — `marketplace.json` does not include version fields (they're silently ignored if present)
- The `outline` plugin has only a skill (no agents or commands)
- The `microsoft` plugin uses Python with `uv` for token management — shared `scripts/` at plugin root (not per-skill)
- The `microsoft` plugin reuses the same env var pattern as `mcp-365-admin` (`M365_PROFILES`, `M365_{NAME}_TENANT_ID/CLIENT_ID/CLIENT_SECRET`)
- M365 and Azure use the same Entra ID app but different permission planes: Graph API permissions vs Azure RBAC roles
