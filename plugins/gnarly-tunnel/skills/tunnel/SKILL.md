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

The skill requires these environment variables to be set in your shell profile or Claude settings:

```bash
GNARLY_TUNNEL_API_URL=https://your-api-id.execute-api.region.amazonaws.com/prod
GNARLY_TUNNEL_API_KEY=your-api-key
GNARLY_TUNNEL_BASTION_HOST=bastion.tunnel.gnarlysoft.com
GNARLY_TUNNEL_SSH_KEY=~/.ssh/gnarly-tunnel-key
```

Before any action, validate all required vars are set:

```bash
[[ -z "${GNARLY_TUNNEL_API_URL}" ]] && echo "ERROR: GNARLY_TUNNEL_API_URL is not set. Run /tunnel setup." && exit 1
[[ -z "${GNARLY_TUNNEL_API_KEY}" ]] && echo "ERROR: GNARLY_TUNNEL_API_KEY is not set. Run /tunnel setup." && exit 1
[[ -z "${GNARLY_TUNNEL_BASTION_HOST}" ]] && echo "ERROR: GNARLY_TUNNEL_BASTION_HOST is not set. Run /tunnel setup." && exit 1
[[ -z "${GNARLY_TUNNEL_SSH_KEY}" ]] && echo "ERROR: GNARLY_TUNNEL_SSH_KEY is not set. Run /tunnel setup." && exit 1
```

**SECURITY**: Never display, echo, or expose the API key in chat output. Read tokens silently and use them only within command variables and headers.

## Setup

The setup flow is fully automated. When the user runs `/tunnel setup`, OR when any other action fails because env vars are missing:

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
  -d "$(jq -n --arg pk "$PUBLIC_KEY" '{"public_key": $pk}')" | python3 -m json.tool
```

The API registers the public key on the bastion server automatically via SSM. The response contains the `bastion_host` and `base_domain`.

### Step 4: Print export commands

Tell the user to add these exports to their shell profile (`~/.zshrc`, `~/.bashrc`, etc.) or to Claude settings as environment variables:

```bash
export GNARLY_TUNNEL_API_URL=<api-url-from-step-1>
export GNARLY_TUNNEL_API_KEY=<api-key-from-step-1>
export GNARLY_TUNNEL_BASTION_HOST=<bastion-host-from-api-response>
export GNARLY_TUNNEL_SSH_KEY=$HOME/.ssh/gnarly-tunnel-key
```

### Step 5: Verify

```bash
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -i "${GNARLY_TUNNEL_SSH_KEY}" tunnel@${GNARLY_TUNNEL_BASTION_HOST} "echo connected" 2>&1
```

Tell the user setup is complete and they can now create tunnels.

## Making Requests

All API calls use this pattern:

```bash
curl -s -X <METHOD> "${GNARLY_TUNNEL_API_URL}/<path>" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" \
  -H "Content-Type: application/json" \
  [-d '<json_body>']
```

Always pipe responses through `python3 -m json.tool` for readable output.

## Available Actions

### Create a tunnel (expose a port)

```bash
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
curl -s "${GNARLY_TUNNEL_API_URL}/tunnels" \
  -H "x-api-key: ${GNARLY_TUNNEL_API_KEY}" | python3 -m json.tool
```

Returns all active tunnels with subdomain, URL, port, and health status.

### Delete a tunnel (tear down)

```bash
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
7. **Auto-setup**: If env vars are missing when the user tries any action, run the setup flow automatically instead of failing

## Error Handling

- **400**: Invalid subdomain format or duplicate subdomain — suggest a different name
- **404**: Tunnel not found on delete — it may already be deleted
- **429**: Too many tunnels — list and clean up unused ones
- **403/Forbidden**: API key is invalid — re-run `/tunnel setup`

## Failure Notification (MANDATORY)

If any step, command, API call, or tool in this workflow fails or does not work as expected, you MUST immediately notify the user with:
1. What failed
2. The error or unexpected behavior observed
3. What you plan to do instead (if anything)

Do NOT silently fall back to alternative approaches without informing the user first.

## Self-Update Protocol

If you discovered something new during this task (failures, bugs, edge cases, better approaches, new IDs or mappings), update this SKILL.md file directly without waiting for the user to ask. Skip if the task was routine with no new findings.

</instructions>

<examples>
<example>
<input>/tunnel setup</input>
<action>
1. Ask user for API URL and API key (use AskUserQuestion)
2. Generate SSH key at ~/.ssh/gnarly-tunnel-key if it doesn't exist
3. POST /setup with the public key to register it on the bastion
4. Print export commands for the user to add to their shell profile
5. Verify SSH connectivity
6. Tell user setup is complete
</action>
</example>

<example>
<input>/tunnel expose 3000 as my-feature</input>
<action>
1. Validate env vars exist (if missing, run setup flow first)
2. POST /tunnels with subdomain "my-feature", local_port 3000
3. Display the HTTPS URL: https://my-feature.tunnel.gnarlysoft.com
4. Show the SSH command to run to activate the tunnel
</action>
</example>

<example>
<input>/tunnel list</input>
<action>
1. Validate env vars exist
2. GET /tunnels
3. Display table of active tunnels with URL, port, and health status
</action>
</example>

<example>
<input>/tunnel destroy my-feature</input>
<action>
1. Validate env vars exist
2. DELETE /tunnels/my-feature
3. Confirm deletion
4. Remind user to kill SSH tunnel
</action>
</example>
</examples>
