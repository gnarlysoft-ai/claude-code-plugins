# GnarlySoft AI - Claude Code Plugins

Collection of Claude Code plugins by GnarlySoft AI.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| [schedule](plugins/schedule/) | 1.1.0 | Repeating prompt schedules for Claude Code — execute any prompt at intervals with configurable stop conditions (times, duration, or forever mode) |
| [outline](plugins/outline/) | 1.3.0 | Interact with Outline knowledge base API — create, read, update, delete documents, collections, comments, and more |
| [utils](plugins/utils/) | 1.3.0 | Code review and security analysis agents — includes code-reviewer, security-reviewer, e2e-runner agents and security-review skill |
| [excalidraw](plugins/excalidraw/) | 1.0.0 | Gnarlysoft-branded Excalidraw diagram creator with dark mode purple theme |
| [m365-personal](plugins/m365-personal/) | 1.0.0 | Query your personal Microsoft 365 data — Outlook email, calendar, Teams chats, and presence status |
| [microsoft](plugins/microsoft/) | 1.0.0 | Microsoft 365 and Azure administration — M365 via Graph API, Azure via Resource Manager API |

## Installation

In Claude Code, add the marketplace and install plugins:

```
/plugin marketplace add gnarlysoft-ai/claude-code-plugins
/plugin install schedule@gnarlysoft-plugins
/plugin install outline@gnarlysoft-plugins
/plugin install utils@gnarlysoft-plugins
/plugin install excalidraw@gnarlysoft-plugins
/plugin install m365-personal@gnarlysoft-plugins
```

All skills and commands are accessible under the unified `/gnarlysoft:` prefix (e.g., `/gnarlysoft:loop`, `/gnarlysoft:e2e`, `/gnarlysoft:adapt`).

## Requirements

- **Claude Code**
- **uv** - Python package manager (for Python-based plugins)

## License

MIT
