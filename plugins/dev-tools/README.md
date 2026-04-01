# Dev Tools

Code review, security analysis, E2E testing, and CLAUDE.md management tools for Claude Code.

## Installation

In Claude Code, run:

```
/plugin marketplace add gnarlysoft-ai/claude-code-plugins
/plugin install dev-tools@gnarlysoft-plugins
```

## Commands

### code-review

Expert code review for quality, security, and maintainability.

### e2e

Generate and run E2E tests with Playwright.

### revise-claude-md

Capture session learnings into CLAUDE.md.

## Agents

### security-reviewer

Security vulnerability detection and remediation specialist. Flags OWASP Top 10 vulnerabilities, secrets, injection, and unsafe patterns.

### e2e-runner

E2E testing with Playwright.

## Skills

### security-review

Comprehensive security checklist and patterns. Referenced by the `security-reviewer` agent for detailed vulnerability examples, code patterns, and pre-deployment checklists.

### claude-md-improver

Audit and improve CLAUDE.md files in repositories.

## License

MIT
