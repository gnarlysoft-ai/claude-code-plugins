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
- API Gateway (REST, API key auth) — manages ALB rules and user onboarding
- EC2 bastion — SSH relay for reverse tunnels
- ALB with wildcard ACM cert — HTTPS termination and routing

The API has four endpoints: setup, create, list, and delete tunnels.
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

If the `.env` file is missing or any required variable is empty, automatically run the setup flow (see Setup section below). Do NOT ask the user to manually create files or run shell commands — the skill handles everything.

**SECURITY**: Never display, echo, or expose the API key in chat output. Read tokens silently and use them only within command variables and headers.

## Setup

The setup flow is fully automated. When the user runs `/tunnel setup`, OR when any other action fails because `.env` is missing:

### Step 1: Ask for credentials

Use AskUserQuestion to ask for the API URL and API key. The user gets these from their GnarlyTunnel deployment (CloudFormation outputs) or from the team wiki.

### Step 2: Generate SSH key (if needed)

```bash
SSH_KEY_PATH="$HOME/.ssh/gnarly-tunnel-key"
if [ ! -f "$SSH_KEY_PATH" ]; then
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "gnarly-tunnel" -q
    echo "Generated SSH key at $SSH_KEY_PATH"
else
    echo "SSH key already exists at $SSH_KEY_PATH"
fi
```

### Step 3: Register SSH key via API

```bash
PUBLIC_KEY=$(cat "${SSH_KEY_PATH}.pub")
curl -s -X POST "${GNARLY_TUNNEL_API_URL}/setup" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"public_key\": \"${PUBLIC_KEY}\"}" | python3 -m json.tool
```

The API registers the public key on the bastion server automatically via SSM. The response contains the `bastion_host` and `base_domain`.

### Step 4: Save .env

Write the `.env` file with all values (use the `bastion_host` from the API response):

```bash
cat > ${CLAUDE_SKILL_DIR}/.env << ENVEOF
GNARLY_TUNNEL_API_URL=<api-url-from-step-1>
GNARLY_TUNNEL_API_KEY=<api-key-from-step-1>
GNARLY_TUNNEL_BASTION_HOST=<bastion-host-from-api-response>
GNARLY_TUNNEL_SSH_KEY=${SSH_KEY_PATH}
ENVEOF
```

### Step 5: Verify

```bash
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "${SSH_KEY_PATH}" tunnel@${GNARLY_TUNNEL_BASTION_HOST} "echo connected" 2>&1
```

Tell the user setup is complete and they can now create tunnels.

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
GNARLY_TUNNEL_SSH_KEY=$(${CLAUDE_SKILL_DIR}/scripts/get-token.sh GNARLY_TUNNEL_SSH_KEY 2>/dev/null || echo "$HOME/.ssh/gnarly-tunnel-key")

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

After creating the tunnel, **tell the user to run the SSH command** to activate it:

```
ssh -N -R <bastion_port>:localhost:<local_port> -i <ssh_key_path> tunnel@<bastion_host>
```

Or suggest running it in the background with `ssh -f -N -R ...`.

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

This removes the ALB listener rule and target group. Remind the user to kill their SSH tunnel too.

## Behavior Guidelines

1. **Subdomain naming**: Suggest descriptive subdomains based on the project or branch name. Default to the current git branch name if available: `git branch --show-current 2>/dev/null | tr '/' '-' | tr '[:upper:]' '[:lower:]'`
2. **Always show the URL**: After creating a tunnel, prominently display the HTTPS URL
3. **SSH command**: Always show the complete SSH command the user needs to run
4. **Cleanup reminder**: When destroying a tunnel, remind the user to kill their SSH tunnel too
5. **Health status**: When listing tunnels, note which ones are healthy (SSH tunnel active) vs unhealthy (SSH tunnel not connected)
6. **Limits**: Maximum 100 concurrent tunnels per deployment. If creation fails with 429, advise cleaning up old tunnels
7. **Auto-setup**: If `.env` is missing when the user tries any action, run the setup flow automatically instead of failing

## Error Handling

- **400**: Invalid subdomain format or duplicate subdomain — suggest a different name
- **404**: Tunnel not found on delete — it may already be deleted
- **429**: Too many tunnels — list and clean up unused ones
- **403/Forbidden**: API key is invalid — re-run `/tunnel setup`

</instructions>

<examples>
<example>
<input>/tunnel setup</input>
<action>
1. Ask user for API URL and API key (use AskUserQuestion)
2. Generate SSH key at ~/.ssh/gnarly-tunnel-key if it doesn't exist
3. POST /setup with the public key to register it on the bastion
4. Save all values to ${CLAUDE_SKILL_DIR}/.env
5. Verify SSH connectivity
6. Tell user setup is complete
</action>
</example>

<example>
<input>/tunnel expose 3000 as my-feature</input>
<action>
1. Load credentials via get-token.sh (if missing, run setup flow first)
2. POST /tunnels with subdomain "my-feature", local_port 3000
3. Display the HTTPS URL: https://my-feature.tunnel.gnarlysoft.com
4. Show the SSH command to run to activate the tunnel
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
