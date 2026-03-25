# GnarlySoft Claude Code Plugins

Marketplace of Claude Code plugins by GnarlySoft AI. Directory-based marketplace registered in user settings as `gnarlysoft-plugins`.

## Architecture

```
plugins/
  schedule/       # Repeating prompt schedules (Python, uses uv)
  outline/        # Outline knowledge base API integration
  utils/          # Code review, security, design, and CLAUDE.md management
```

Each plugin follows the Claude Code plugin structure:
- `.claude-plugin/plugin.json` — plugin metadata (name, version, description, author)
- `agents/` — agent definitions (`.md` files with frontmatter)
- `commands/` — slash commands (`.md` files)
- `skills/` — skills with `SKILL.md` and optional `references/` subdirectory
- `hooks/` — hook definitions (`hooks.json`)

Marketplace root: `.claude-plugin/marketplace.json` — lists all plugins with name, source path, description, version.

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

## Gotchas

- The `schedule` plugin uses Python with `uv` — it has a `.venv/` directory and `pyproject.toml`
- Plugin names in `marketplace.json` differ from `plugin.json` names (e.g., `utils` vs `gnarlysoft-utils`)
- Skills from `impeccable` (audit, critique, polish, etc.) don't have the `from` field on all of them yet
