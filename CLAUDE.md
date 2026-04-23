# GnarlySoft Claude Code Plugins

Marketplace of Claude Code plugins by GnarlySoft AI. Directory-based marketplace registered in user settings as `gnarlysoft-plugins`.

## Architecture

```
plugins/
  schedule/         # Repeating prompt schedules (Python, uses uv)
  outline/          # Outline knowledge base API integration
  dev-tools/        # Code review, security, E2E testing, and CLAUDE.md management
  frontend-design/  # Frontend design audit, critique, and polish tools
  excalidraw/       # Gnarlysoft-branded Excalidraw diagram creator
  nano-banana/      # AI image generation with Nano Banana Pro (Gemini 3 Pro Image)
  m365-personal/    # Microsoft 365 personal data (email, calendar, Teams, presence)
  microsoft/        # Microsoft 365 (Graph API) and Azure (Resource Manager API)
  gnarly-tunnel/    # Local port tunneling via HTTPS subdomains (ALB + SSH relay)
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
name: "gnarlysoft:example-skill"
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

Plugin JSON `name` field is prefixed with `gnarlysoft-` (e.g., `gnarlysoft-dev-tools`, `gnarlysoft-schedule`).

### Unified `/gnarlysoft:` prefix

All skills and commands use `name: "gnarlysoft:skill-name"` in their SKILL.md/command frontmatter. This overrides the default plugin namespace so everything appears under a unified `/gnarlysoft:` prefix regardless of which plugin it belongs to.

```yaml
---
name: "gnarlysoft:my-skill"
description: What it does
---
```

When adding new skills or commands, always include this `name` field with the `gnarlysoft:` prefix.

### Version bumps

**MANDATORY:** When modifying any plugin's skills, agents, commands, or configuration, bump the plugin version in `.claude-plugin/plugin.json` and update `README.md` Plugins table to match. Use semver: patch for fixes, minor for new features/content, major for breaking changes. `plugin.json` is the single source of truth for versions.

### Agent model

Agents that don't need Opus use `model: sonnet` in frontmatter to reduce cost.

## Commands

| Command | Plugin | Description |
|---------|--------|-------------|
| `/gnarlysoft:code-review` | dev-tools | Expert code review for quality, security, and maintainability |
| `/gnarlysoft:e2e` | dev-tools | Generate and run E2E tests with Playwright |
| `/gnarlysoft:revise-claude-md` | dev-tools | Capture session learnings into CLAUDE.md |

## Agents

| Agent | Plugin | Description |
|-------|--------|-------------|
| `security-reviewer` | dev-tools | Security vulnerability detection and remediation |
| `e2e-runner` | dev-tools | E2E testing with Playwright |

## Skills

| Skill | Plugin | Source |
|-------|--------|--------|
| `/gnarlysoft:schedule` | schedule | — |
| `/gnarlysoft:outline` | outline | — |
| `/gnarlysoft:adapt` | frontend-design | `impeccable` |
| `/gnarlysoft:audit` | frontend-design | `impeccable` |
| `/gnarlysoft:critique` | frontend-design | `impeccable` |
| `/gnarlysoft:extract` | frontend-design | `impeccable` |
| `/gnarlysoft:optimize` | frontend-design | `impeccable` |
| `/gnarlysoft:polish` | frontend-design | `impeccable` |
| `/gnarlysoft:quieter` | frontend-design | `impeccable` |
| `/gnarlysoft:teach-impeccable` | frontend-design | `impeccable` |
| `/gnarlysoft:security-review` | dev-tools | `everything-claude-code` |
| `/gnarlysoft:claude-md-improver` | dev-tools | `claude-plugins-official/claude-md-management` |
| `/gnarlysoft:excalidraw-diagram` | excalidraw | — |
| `/gnarlysoft:nano-banana` | nano-banana | — |
| `/gnarlysoft:m365-personal` | m365-personal | — |
| `/gnarlysoft:m365` | microsoft | — |
| `/gnarlysoft:azure` | microsoft | — |
| `/gnarlysoft:tunnel` | gnarly-tunnel | — |

## Keeping Docs in Sync

When adding, removing, or modifying plugins, skills, agents, or commands, update **both** files:

1. **`CLAUDE.md`** — Update the relevant table (Plugins architecture, Commands, Agents, Skills)
2. **`README.md`** — Update the Plugins table (name, version, description)

Specifically:
- New plugin → add to `README.md` Plugins table and `CLAUDE.md` Architecture tree + relevant tables
- New skill/agent/command → add to the corresponding `CLAUDE.md` table
- Version bump → update `README.md` Plugins table version
- Removed plugin/skill → remove from both files

## Gotchas

- The `schedule` plugin uses Python with `uv` — it has a `.venv/` directory and `pyproject.toml`
- Plugin names in `marketplace.json` differ from `plugin.json` names (e.g., `dev-tools` vs `gnarlysoft-dev-tools`)
- Skills from `impeccable` (in `frontend-design` plugin) don't have the `from` field on all of them yet
- `plugin.json` is the single source of truth for plugin versions — `marketplace.json` does not include version fields (they're silently ignored if present)
- The `outline` plugin has only a skill (no agents or commands)
- The `microsoft` plugin uses Python with `uv` for token management — shared `scripts/` at plugin root (not per-skill)
- The `microsoft` plugin reuses the same env var pattern as `mcp-365-admin` (`M365_PROFILES`, `M365_{NAME}_TENANT_ID/CLIENT_ID/CLIENT_SECRET`)
- M365 and Azure use the same Entra ID app but different permission planes: Graph API permissions vs Azure RBAC roles
