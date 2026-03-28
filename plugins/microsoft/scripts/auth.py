#!/usr/bin/env python3
"""Token helper for Microsoft API authentication.

Usage:
    uv run python auth.py list-profiles
    uv run python auth.py get-token <profile> [--scope graph|azure|keyvault]
    uv run python auth.py test <profile> [--scope graph|azure]
    uv run python auth.py add-profile <name> <tenant_id> <client_id> <client_secret>
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import httpx

TOKEN_CACHE_DIR = Path("/tmp")
TOKEN_SAFETY_MARGIN = 5 * 60  # Expire tokens 5 minutes early

SCOPES = {
    "graph": "https://graph.microsoft.com/.default",
    "azure": "https://management.azure.com/.default",
    "keyvault": "https://vault.azure.net/.default",
}

TEST_ENDPOINTS = {
    "graph": "https://graph.microsoft.com/v1.0/organization",
    "azure": "https://management.azure.com/subscriptions?api-version=2022-12-01",
}


def get_profiles() -> dict[str, dict[str, str]]:
    """Discover configured M365 profiles from environment variables."""
    profiles_str = os.environ.get("M365_PROFILES", "")
    if not profiles_str:
        return {}

    profiles = {}
    for name in profiles_str.split(","):
        name = name.strip()
        if not name:
            continue
        upper = name.upper()
        tenant_id = os.environ.get(f"M365_{upper}_TENANT_ID")
        client_id = os.environ.get(f"M365_{upper}_CLIENT_ID")
        client_secret = os.environ.get(f"M365_{upper}_CLIENT_SECRET")

        if tenant_id and client_id and client_secret:
            profiles[name] = {
                "tenant_id": tenant_id,
                "client_id": client_id,
                "client_secret": client_secret,
            }
        else:
            missing = []
            if not tenant_id:
                missing.append(f"M365_{upper}_TENANT_ID")
            if not client_id:
                missing.append(f"M365_{upper}_CLIENT_ID")
            if not client_secret:
                missing.append(f"M365_{upper}_CLIENT_SECRET")
            print(
                f"Warning: Profile '{name}' incomplete, missing: {', '.join(missing)}",
                file=sys.stderr,
            )
    return profiles


def _cache_path(profile: str, scope: str) -> Path:
    return TOKEN_CACHE_DIR / f".m365-token-{profile}-{scope}.json"


def get_cached_token(profile: str, scope: str) -> str | None:
    """Return cached token if still valid."""
    cache_file = _cache_path(profile, scope)
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text())
        if isinstance(data.get("access_token"), str) and time.time() < data.get("expires_at", 0):
            return data["access_token"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def cache_token(profile: str, scope: str, access_token: str, expires_in: int) -> None:
    """Atomically cache token with secure permissions."""
    cache_file = _cache_path(profile, scope)
    content = json.dumps({
        "access_token": access_token,
        "expires_at": time.time() + expires_in - TOKEN_SAFETY_MARGIN,
    })
    # Write to temp file with 0o600 permissions, then atomically rename
    fd, tmp_path = tempfile.mkstemp(dir=TOKEN_CACHE_DIR, prefix=".m365-token-")
    try:
        os.fchmod(fd, 0o600)
        os.write(fd, content.encode())
        os.close(fd)
        os.rename(tmp_path, cache_file)
    except Exception:
        os.close(fd) if not os.get_inheritable(fd) else None
        os.unlink(tmp_path)
        raise


def acquire_token(creds: dict[str, str], scope: str = "graph") -> tuple[str, int]:
    """Acquire a new token via OAuth 2.0 client credentials flow.

    Returns (access_token, expires_in_seconds).
    """
    if scope not in SCOPES:
        raise ValueError(f"Unknown scope '{scope}'. Available: {', '.join(SCOPES)}")

    token_url = f"https://login.microsoftonline.com/{creds['tenant_id']}/oauth2/v2.0/token"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "scope": SCOPES[scope],
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"], int(data.get("expires_in", 3600))


def resolve_profile(profile: str) -> dict[str, str]:
    """Look up a profile by name, exit with error if not found."""
    profiles = get_profiles()
    if profile not in profiles:
        available = ", ".join(profiles.keys()) if profiles else "(none)"
        print(f"Error: Profile '{profile}' not found. Available: {available}", file=sys.stderr)
        sys.exit(1)
    return profiles[profile]


def get_or_acquire_token(profile: str, scope: str) -> str:
    """Get cached token or acquire a new one."""
    cached = get_cached_token(profile, scope)
    if cached:
        return cached

    creds = resolve_profile(profile)
    try:
        token, expires_in = acquire_token(creds, scope)
        cache_token(profile, scope, token, expires_in)
        return token
    except httpx.HTTPStatusError as e:
        print(f"Error: Authentication failed: {e.response.text}", file=sys.stderr)
        sys.exit(1)


def parse_scope(args: list[str]) -> str:
    """Extract --scope value from args, default to 'graph'."""
    for i, arg in enumerate(args):
        if arg == "--scope" and i + 1 < len(args):
            scope = args[i + 1]
            if scope not in SCOPES:
                print(f"Error: Unknown scope '{scope}'. Available: {', '.join(SCOPES)}", file=sys.stderr)
                sys.exit(1)
            return scope
    return "graph"


def cmd_list_profiles() -> None:
    """List all configured profiles."""
    profiles = get_profiles()
    if not profiles:
        print("No profiles configured.")
        print("Set M365_PROFILES and M365_{NAME}_TENANT_ID/CLIENT_ID/CLIENT_SECRET env vars.")
        sys.exit(1)

    print(f"Configured profiles ({len(profiles)}):")
    for name, creds in profiles.items():
        tenant = creds["tenant_id"][:8] + "..."
        print(f"  {name}: tenant={tenant}")


def cmd_get_token(profile: str, scope: str) -> None:
    """Get a bearer token for the given profile. Outputs token to stdout."""
    print(get_or_acquire_token(profile, scope))


def cmd_test(profile: str, scope: str) -> None:
    """Test connectivity by calling a scope-appropriate endpoint."""
    token = get_or_acquire_token(profile, scope)
    test_url = TEST_ENDPOINTS.get(scope, TEST_ENDPOINTS["graph"])

    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            test_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            data = response.json()
            if scope == "graph":
                orgs = data.get("value", [])
                if orgs:
                    org = orgs[0]
                    print(f"Connected to: {org.get('displayName', 'Unknown')}")
                    print(f"Tenant ID: {org.get('id', 'Unknown')}")
                    domains = [d["name"] for d in org.get("verifiedDomains", [])]
                    print(f"Domains: {', '.join(domains)}")
                else:
                    print("Connected (no organization data returned)")
            elif scope == "azure":
                subs = data.get("value", [])
                print(f"Azure subscriptions ({len(subs)}):")
                for sub in subs:
                    print(f"  {sub.get('displayName', 'Unknown')}: {sub.get('subscriptionId', 'Unknown')} ({sub.get('state', 'Unknown')})")
        else:
            print(f"Token acquired but test endpoint returned {response.status_code}")
            print(response.text)


def cmd_add_profile(name: str, tenant_id: str, client_id: str, client_secret: str) -> None:
    """Validate credentials and output env var config."""
    creds = {"tenant_id": tenant_id, "client_id": client_id, "client_secret": client_secret}
    print(f"Testing credentials for profile '{name}'...", file=sys.stderr)
    try:
        token, _ = acquire_token(creds)
    except httpx.HTTPStatusError as e:
        print(f"Error: Authentication failed: {e.response.text}", file=sys.stderr)
        sys.exit(1)

    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            TEST_ENDPOINTS["graph"],
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            orgs = response.json().get("value", [])
            if orgs:
                print(f"Verified: {orgs[0].get('displayName', 'Unknown')}", file=sys.stderr)

    upper = name.upper()
    existing = os.environ.get("M365_PROFILES", "")
    new_profiles = f"{existing},{name}" if existing else name

    print(f"\n# Add these to your .env or shell profile:")
    print(f"M365_PROFILES={new_profiles}")
    print(f"M365_{upper}_TENANT_ID={tenant_id}")
    print(f"M365_{upper}_CLIENT_ID={client_id}")
    print(f"M365_{upper}_CLIENT_SECRET={client_secret}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list-profiles":
        cmd_list_profiles()
    elif command == "get-token":
        if len(sys.argv) < 3:
            print("Usage: auth.py get-token <profile> [--scope graph|azure|keyvault]", file=sys.stderr)
            sys.exit(1)
        scope = parse_scope(sys.argv[3:])
        cmd_get_token(sys.argv[2], scope)
    elif command == "test":
        if len(sys.argv) < 3:
            print("Usage: auth.py test <profile> [--scope graph|azure]", file=sys.stderr)
            sys.exit(1)
        scope = parse_scope(sys.argv[3:])
        cmd_test(sys.argv[2], scope)
    elif command == "add-profile":
        if len(sys.argv) < 6:
            print("Usage: auth.py add-profile <name> <tenant_id> <client_id> <client_secret>", file=sys.stderr)
            sys.exit(1)
        cmd_add_profile(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
