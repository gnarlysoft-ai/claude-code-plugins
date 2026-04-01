# GnarlySoft AI - Claude Code Plugins

Collection of Claude Code plugins by GnarlySoft AI.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [schedule](plugins/schedule/) | 1.1.0 | Repeating prompt schedules for Claude Code — execute any prompt at intervals with configurable stop conditions (times, duration, or forever mode) |
| [outline](plugins/outline/) | 1.3.0 | Interact with Outline knowledge base API — create, read, update, delete documents, collections, comments, and more |
| [dev-tools](plugins/dev-tools/) | 1.4.0 | Code review, security analysis, E2E testing, and CLAUDE.md management — includes code-review command, security-reviewer and e2e-runner agents |
| [frontend-design](plugins/frontend-design/) | 1.0.0 | Frontend design audit, critique, and polish tools — adapt, audit, critique, extract, optimize, polish, quieter, teach-impeccable |
| [excalidraw](plugins/excalidraw/) | 1.0.0 | Gnarlysoft-branded Excalidraw diagram creator with dark mode purple theme |
| [m365-personal](plugins/m365-personal/) | 1.0.0 | Query your personal Microsoft 365 data — Outlook email, calendar, Teams chats, and presence status |
| [microsoft](plugins/microsoft/) | 1.0.0 | Microsoft 365 and Azure administration — M365 via Graph API, Azure via Resource Manager API |

## Installation

In Claude Code, add the marketplace and install plugins:

```
/plugin marketplace add gnarlysoft-ai/claude-code-plugins
/plugin install schedule@gnarlysoft-plugins
/plugin install outline@gnarlysoft-plugins
/plugin install dev-tools@gnarlysoft-plugins
/plugin install frontend-design@gnarlysoft-plugins
/plugin install excalidraw@gnarlysoft-plugins
/plugin install m365-personal@gnarlysoft-plugins
/plugin install microsoft@gnarlysoft-plugins
```

All skills and commands are accessible under the unified `/gnarlysoft:` prefix (e.g., `/gnarlysoft:loop`, `/gnarlysoft:e2e`, `/gnarlysoft:adapt`).

## Requirements

- **Claude Code**
- **uv** - Python package manager (for Python-based plugins)

## License

MIT
