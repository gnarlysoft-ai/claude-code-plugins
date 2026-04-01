# Utils

Code review and security analysis agents for Claude Code.

## Installation

In Claude Code, run:

```
/plugin marketplace add gnarlysoft-ai/claude-code-plugins
/plugin install utils@gnarlysoft-plugins
```

## Agents

### code-reviewer

Expert code review specialist. Reviews code for quality, security, and maintainability.

**Use after writing or modifying code.**

Covers:
- Security (hardcoded secrets, SQL injection, XSS, CSRF, auth bypasses)
- Code quality (large functions, deep nesting, missing error handling)
- React/Next.js patterns (missing deps, stale closures, server/client boundaries)
- Node.js/backend patterns (N+1 queries, missing rate limiting, unvalidated input)
- Performance and best practices

### security-reviewer

Security vulnerability detection and remediation specialist. Flags OWASP Top 10 vulnerabilities, secrets, injection, and unsafe patterns.

**Use proactively after writing code that handles user input, authentication, API endpoints, or sensitive data.**

## Skills

### security-review

Comprehensive security checklist and patterns. Referenced by the `security-reviewer` agent for detailed vulnerability examples, code patterns, and pre-deployment checklists.

## License

MIT
