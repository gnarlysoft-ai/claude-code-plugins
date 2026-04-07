---
name: "gnarlysoft:tunnel"
description: Expose local ports to the internet via HTTPS subdomains. Use when the user wants to create a tunnel, expose a local service, get a public URL for a local port, list active tunnels, or tear down a tunnel. Self-hosted ngrok alternative using AWS ALB + SSH relay.
allowed-tools: Bash
user-invocable: true
argument-hint: "<action> [options] (e.g., 'expose 3000 as my-app', 'list', 'destroy my-app', 'setup')"
---

# GnarlyTunnel — Local Port Tunneling

<context>
GnarlyTunnel exposes local ports to the internet via HTTPS subdomains on `*.tunnel.gnarlysoft.com`.

**How it works:**
1. An API call creates an ALB listener rule that routes `{subdomain}.tunnel.gnarlysoft.com` to the bastion EC2 instance on an assigned port
2. The user opens an SSH reverse tunnel from their local machine to the bastion
3. Internet traffic flows: Browser → ALB → Bastion → SSH tunnel → localhost

**Components:**
- API Gateway (REST, API key auth) — manages ALB rules
- EC2 bastion — SSH relay for reverse tunnels
- ALB with wildcard ACM cert — HTTPS termination and routing

The API has three endpoints: create, list, and delete tunnels.
</context>

<instructions>

## Configuration

Credentials are stored in `${CLAUDE_SKILL_DIR}/.env` and loaded via `get-token.sh`:

```bash
GNARLY_TUNNEL_API_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL)
GNARLY_TUNNEL_API_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_KEY)
GNARLY_TUNNEL_BASTION_HOST=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_BASTION_HOST)
GNARLY_TUNNEL_SSH_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_SSH_KEY 2>/dev/null || echo "$HOME/.ssh/gnarly-tunnel-key")
```

If the `.env` file is missing or any required variable is empty, tell the user to run `/tunnel setup` or manually create `${CLAUDE_SKILL_DIR}/.env` with:

```
GNARLY_TUNNEL_API_URL=https://xxxx.execute-api.us-east-1.amazonaws.com/prod
GNARLY_TUNNEL_API_KEY=your-api-key-here
GNARLY_TUNNEL_BASTION_HOST=52.x.x.x
GNARLY_TUNNEL_SSH_KEY=~/.ssh/gnarly-tunnel-key
```

**SECURITY**: Never display, echo, or expose the API key in chat output. Read tokens silently and use them only within command variables and headers. Never print token values to stdout or include them in responses to the user.

## Setup

When the user runs `/tunnel setup` or provides their API URL, API key, and bastion host, write the `.env` file for them:

```bash
cat > ${CLAUDE_SKILL_DIR}/.env <<'EOF'
GNARLY_TUNNEL_API_URL=<provided-url>
GNARLY_TUNNEL_API_KEY=<provided-key>
GNARLY_TUNNEL_BASTION_HOST=<provided-host>
GNARLY_TUNNEL_SSH_KEY=~/.ssh/gnarly-tunnel-key
EOF
```

After writing, verify by loading the values:

```bash
${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL && echo "Config saved successfully"
```

If the user doesn't provide all three values, ask for the missing ones using AskUserQuestion.

## Making Requests

All API calls use this pattern:

```bash
GNARLY_TUNNEL_API_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL)
GNARLY_TUNNEL_API_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_KEY)

curl -s -X <METHOD> "${GNARLY_TUNNEL_API_URL}/<path>" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" \
  -H "Content-Type: application/json" \
  [-d '<json_body>']
```

Always load credentials via `get-token.sh` before each request. Always pipe responses through `python3 -m json.tool` for readable output.

## Available Actions

### Create a tunnel (expose a port)

```bash
GNARLY_TUNNEL_API_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL)
GNARLY_TUNNEL_API_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_KEY)
GNARLY_TUNNEL_BASTION_HOST=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_BASTION_HOST)

curl -s -X POST "${GNARLY_TUNNEL_API_URL}/tunnels" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"subdomain": "<SUBDOMAIN>", "local_port": <PORT>}' | python3 -m json.tool
```

**Parameters:**
- `subdomain` — lowercase alphanumeric with hyphens, 1-63 chars (e.g., `my-app`, `feature-x`, `webhook-test`)
- `local_port` — the local port to expose (e.g., `3000`, `8080`)

**Response** includes:
- `url` — the public HTTPS URL (e.g., `https://my-app.tunnel.gnarlysoft.com`)
- `bastion_port` — the assigned relay port on the bastion
- `ssh_command` — the exact SSH command the user needs to run

After creating the tunnel, **tell the user to run the SSH command** in a separate terminal:

```bash
GNARLY_TUNNEL_SSH_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_SSH_KEY 2>/dev/null || echo "$HOME/.ssh/gnarly-tunnel-key")
ssh -N -R <bastion_port>:localhost:<local_port> -i ${GNARLY_TUNNEL_SSH_KEY} tunnel@${GNARLY_TUNNEL_BASTION_HOST}
```

Or if the user prefers, run it in the background:

```bash
ssh -f -N -R <bastion_port>:localhost:<local_port> -i ${GNARLY_TUNNEL_SSH_KEY} tunnel@${GNARLY_TUNNEL_BASTION_HOST}
```

The tunnel is only active while the SSH connection is open.

### List active tunnels

```bash
GNARLY_TUNNEL_API_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL)
GNARLY_TUNNEL_API_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_KEY)

curl -s "${GNARLY_TUNNEL_API_URL}/tunnels" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" | python3 -m json.tool
```

Returns all active tunnels with subdomain, URL, port, and health status.

### Delete a tunnel (tear down)

```bash
GNARLY_TUNNEL_API_URL=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_URL)
GNARLY_TUNNEL_API_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_API_KEY)

curl -s -X DELETE "${GNARLY_TUNNEL_API_URL}/tunnels/<SUBDOMAIN>" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" | python3 -m json.tool
```

This removes the ALB listener rule and target group. The user should also terminate their SSH tunnel.

## Behavior Guidelines

1. **Subdomain naming**: Suggest descriptive subdomains based on the project or branch name. Default to the current git branch name if available: `git branch --show-current 2>/dev/null | tr '/' '-' | tr '[:upper:]' '[:lower:]'`
2. **Always show the URL**: After creating a tunnel, prominently display the HTTPS URL
3. **SSH command**: Always show the complete SSH command the user needs to run
4. **Cleanup reminder**: When destroying a tunnel, remind the user to kill their SSH tunnel too
5. **Health status**: When listing tunnels, note which ones are healthy (SSH tunnel active) vs unhealthy (SSH tunnel not connected)
6. **Limits**: Maximum 100 concurrent tunnels per deployment. If creation fails with 429, advise cleaning up old tunnels

## Error Handling

- **400**: Invalid subdomain format or duplicate subdomain — suggest a different name
- **404**: Tunnel not found on delete — it may already be deleted
- **429**: Too many tunnels — list and clean up unused ones
- **403/Forbidden**: API key is invalid — check `.env` file

</instructions>

<examples>
<example>
<input>/tunnel setup</input>
<action>
1. Ask user for API URL, API key, and bastion host (use AskUserQuestion)
2. Write values to ${CLAUDE_SKILL_DIR}/.env
3. Verify by loading with get-token.sh
</action>
</example>

<example>
<input>/tunnel expose 3000 as my-feature</input>
<action>
1. Load credentials via get-token.sh
2. POST /tunnels with subdomain "my-feature", local_port 3000
3. Display the HTTPS URL: https://my-feature.tunnel.gnarlysoft.com
4. Show the SSH command to run
</action>
</example>

<example>
<input>/tunnel list</input>
<action>
1. Load credentials via get-token.sh
2. GET /tunnels
3. Display table of active tunnels with URL, port, and health status
</action>
</example>

<example>
<input>/tunnel destroy my-feature</input>
<action>
1. Load credentials via get-token.sh
2. DELETE /tunnels/my-feature
3. Confirm deletion
4. Remind user to kill SSH tunnel
</action>
</example>
</examples>
