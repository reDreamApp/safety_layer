#!/usr/bin/env python3
"""Deploy a small self-hosted Langfuse stack on a Scaleway Instance.

The script reads Scaleway credentials from .env/environment and never prints
secret values.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / ".codex" / "langfuse-scaleway"
STATE_FILE = STATE_DIR / "state.json"


def load_config() -> dict[str, str]:
    load_dotenv(ROOT / ".env")
    aliases = {
        "project_id": ("SCW_DEFAULT_PROJECT_ID", "SCW_PROJECT_ID"),
        "organization_id": ("SCW_DEFAULT_ORGANIZATION_ID", "SCW_ORGANIZATION_ID"),
        "zone": ("SCW_DEFAULT_ZONE",),
        "region": ("SCW_DEFAULT_REGION",),
        "access_key": ("SCW_ACCESS_KEY",),
        "secret_key": ("SCW_SECRET_KEY",),
    }
    cfg: dict[str, str] = {}
    missing: list[str] = []
    for name, keys in aliases.items():
        value = next((os.getenv(key) for key in keys if os.getenv(key)), None)
        if value:
            cfg[name] = value
        else:
            missing.append("/".join(keys))
    if missing:
        raise SystemExit("Missing required env vars: " + ", ".join(missing))
    return cfg


def api(cfg: dict[str, str], method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = "https://api.scaleway.com" + path
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "X-Auth-Token": cfg["secret_key"],
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            body = res.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {detail}") from exc
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def api_text(cfg: dict[str, str], method: str, path: str, payload: str) -> dict[str, Any]:
    url = "https://api.scaleway.com" + path
    req = urllib.request.Request(
        url,
        data=payload.encode("utf-8"),
        method=method,
        headers={
            "X-Auth-Token": cfg["secret_key"],
            "Content-Type": "text/plain",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            body = res.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed with HTTP {exc.code}: {detail}") from exc
    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def state_load() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def state_save(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def products(cfg: dict[str, str]) -> dict[str, Any]:
    return api(cfg, "GET", f"/instance/v1/zones/{cfg['zone']}/products/servers")


def pick_type(product_data: dict[str, Any]) -> str:
    servers = product_data.get("servers", {})
    preferred = ["GP1-XS", "PLAY2-MICRO", "DEV1-L"]
    available = set(servers.keys())
    for name in preferred:
        item = servers.get(name, {})
        if name in available and item.get("arch", "x86_64") == "x86_64":
            return name
    candidates: list[tuple[int, int, str]] = []
    for name, item in servers.items():
        ncpus = int(item.get("ncpus") or item.get("cpus") or 0)
        ram = int(item.get("ram") or 0)
        # RAM is usually bytes in this API.
        if ncpus >= 4 and ram >= 16 * 1024**3 and item.get("arch", "x86_64") == "x86_64":
            candidates.append((ncpus, ram, name))
    if not candidates:
        raise SystemExit("Could not find a 4 vCPU / 16 GiB x86_64 instance type in this zone.")
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    return candidates[0][2]


def cmd(args: list[str], *, input_text: str | None = None, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        input=input_text,
        text=True,
        check=True,
        capture_output=True,
        timeout=timeout,
    )


def local_public_key() -> str:
    for name in ("id_ed25519.pub", "id_rsa.pub"):
        path = Path.home() / ".ssh" / name
        if path.exists():
            return path.read_text().strip()
    raise SystemExit("No local SSH public key found at ~/.ssh/id_ed25519.pub or ~/.ssh/id_rsa.pub")


def ensure_server(cfg: dict[str, str], commercial_type: str) -> dict[str, Any]:
    state = state_load()
    server_id = state.get("server_id")
    if server_id:
        return api(cfg, "GET", f"/instance/v1/zones/{cfg['zone']}/servers/{server_id}")["server"]

    payload = {
        "name": "langfuse-redreamai",
        "project": cfg["project_id"],
        "commercial_type": commercial_type,
        "image": "ubuntu_noble",
        "enable_ipv6": True,
        "dynamic_ip_required": True,
        "tags": ["langfuse", "codex-managed"],
    }
    res = api(cfg, "POST", f"/instance/v1/zones/{cfg['zone']}/servers", payload)
    server = res["server"]
    state.update({"server_id": server["id"], "commercial_type": commercial_type})
    state_save(state)
    return server


def server_action(cfg: dict[str, str], server_id: str, action: str) -> None:
    api(cfg, "POST", f"/instance/v1/zones/{cfg['zone']}/servers/{server_id}/action", {"action": action})


def put_user_data(cfg: dict[str, str], server_id: str) -> None:
    ssh_key = local_public_key()
    cloud_config = f"""#cloud-config
users:
  - default
  - name: root
    ssh_authorized_keys:
      - {ssh_key}
    lock_passwd: true
    shell: /bin/bash
ssh_pwauth: false
package_update: true
packages:
  - ca-certificates
  - curl
  - gnupg
  - git
"""
    # Scaleway userdata values are plain text sent as JSON strings.
    api_text(
        cfg,
        "PATCH",
        f"/instance/v1/zones/{cfg['zone']}/servers/{server_id}/user_data/cloud-init",
        cloud_config,
    )


def public_ip(server: dict[str, Any]) -> str | None:
    ip = server.get("public_ip")
    if isinstance(ip, dict):
        return ip.get("address")
    if isinstance(ip, str):
        return ip
    routed = server.get("routed_ip")
    if isinstance(routed, dict):
        return routed.get("address")
    return None


def wait_for_server(cfg: dict[str, str], server_id: str) -> dict[str, Any]:
    for _ in range(90):
        server = api(cfg, "GET", f"/instance/v1/zones/{cfg['zone']}/servers/{server_id}")["server"]
        ip = public_ip(server)
        if ip and server.get("state") in {"running", "started"}:
            return server
        time.sleep(5)
    raise SystemExit("Timed out waiting for server to start and receive a public IP.")


def wait_ssh(ip: str) -> None:
    for _ in range(90):
        try:
            with socket.create_connection((ip, 22), timeout=5):
                break
        except OSError:
            time.sleep(5)
    else:
        raise SystemExit("Timed out waiting for SSH port 22.")

    ssh_base = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=10",
        f"root@{ip}",
    ]
    for _ in range(60):
        try:
            cmd(ssh_base + ["true"], timeout=20)
            return
        except subprocess.CalledProcessError:
            time.sleep(5)
    raise SystemExit("SSH is reachable, but key authentication did not succeed.")


def remote_script(host: str) -> str:
    secrets = {
        "NEXTAUTH_SECRET": os.urandom(32).hex(),
        "SALT": os.urandom(32).hex(),
        "ENCRYPTION_KEY": os.urandom(32).hex(),
        "POSTGRES_PASSWORD": os.urandom(24).hex(),
        "CLICKHOUSE_PASSWORD": os.urandom(24).hex(),
        "REDIS_AUTH": os.urandom(24).hex(),
        "MINIO_ROOT_PASSWORD": os.urandom(24).hex(),
        "LANGFUSE_INIT_PROJECT_PUBLIC_KEY": "pk-lf-" + os.urandom(16).hex(),
        "LANGFUSE_INIT_PROJECT_SECRET_KEY": "sk-lf-" + os.urandom(24).hex(),
        "LANGFUSE_INIT_USER_PASSWORD": base64.urlsafe_b64encode(os.urandom(18)).decode().rstrip("="),
    }
    nextauth_url = f"http://{host}:3000"
    env_lines = {
        "NEXTAUTH_URL": nextauth_url,
        "TELEMETRY_ENABLED": "false",
        "LANGFUSE_INIT_ORG_ID": "redreamai",
        "LANGFUSE_INIT_ORG_NAME": "ReDreamAI",
        "LANGFUSE_INIT_PROJECT_ID": "redreamai-thesis",
        "LANGFUSE_INIT_PROJECT_NAME": "ReDreamAI Thesis",
        "LANGFUSE_INIT_USER_EMAIL": "admin@redreamai.local",
        "LANGFUSE_INIT_USER_NAME": "ReDreamAI Admin",
        **secrets,
    }
    env_text = "\n".join(f"{key}={value}" for key, value in env_lines.items())
    return f"""set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl git openssl
install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
fi
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
mkdir -p /opt/langfuse
cd /opt/langfuse
if [ ! -d langfuse/.git ]; then
  git clone --depth 1 https://github.com/langfuse/langfuse.git
fi
cd langfuse
cat > .env <<'EOF'
{env_text}
DATABASE_URL=postgresql://postgres:{secrets['POSTGRES_PASSWORD']}@postgres:5432/postgres
CLICKHOUSE_PASSWORD={secrets['CLICKHOUSE_PASSWORD']}
REDIS_AUTH={secrets['REDIS_AUTH']}
LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY={secrets['MINIO_ROOT_PASSWORD']}
LANGFUSE_S3_MEDIA_UPLOAD_SECRET_ACCESS_KEY={secrets['MINIO_ROOT_PASSWORD']}
LANGFUSE_S3_BATCH_EXPORT_SECRET_ACCESS_KEY={secrets['MINIO_ROOT_PASSWORD']}
MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD={secrets['MINIO_ROOT_PASSWORD']}
EOF
docker compose up -d
cat > /root/langfuse-credentials.txt <<'EOF'
URL={nextauth_url}
ADMIN_EMAIL=admin@redreamai.local
ADMIN_PASSWORD={secrets['LANGFUSE_INIT_USER_PASSWORD']}
LANGFUSE_PUBLIC_KEY={secrets['LANGFUSE_INIT_PROJECT_PUBLIC_KEY']}
LANGFUSE_SECRET_KEY={secrets['LANGFUSE_INIT_PROJECT_SECRET_KEY']}
EOF
chmod 600 /root/langfuse-credentials.txt
"""


def deploy_stack(ip: str) -> None:
    script = remote_script(ip)
    cmd(
        [
            "ssh",
            "-o",
            "StrictHostKeyChecking=accept-new",
            f"root@{ip}",
            "bash -s",
        ],
        input_text=script,
        timeout=1800,
    )


def fetch_credentials(ip: str) -> str:
    return cmd(
        [
            "ssh",
            "-o",
            "StrictHostKeyChecking=accept-new",
            f"root@{ip}",
            "cat /root/langfuse-credentials.txt",
        ],
        timeout=30,
    ).stdout


def probe() -> None:
    cfg = load_config()
    data = products(cfg)
    servers = data.get("servers", {})
    print(f"Scaleway zone: {cfg['zone']}")
    print(f"Project ID: set")
    print(f"Recommended type selected: {pick_type(data)}")
    print("Nearby 4 vCPU / 16 GiB candidates:")
    shown = 0
    for name, item in sorted(servers.items()):
        ncpus = int(item.get("ncpus") or item.get("cpus") or 0)
        ram = int(item.get("ram") or 0)
        if ncpus >= 4 and ram >= 16 * 1024**3:
            print(f"- {name}: {ncpus} vCPU, {ram / 1024**3:.0f} GiB RAM")
            shown += 1
            if shown >= 10:
                break


def create_and_deploy() -> None:
    cfg = load_config()
    product_data = products(cfg)
    commercial_type = pick_type(product_data)
    print(f"Creating/reusing Scaleway Instance type {commercial_type} in {cfg['zone']}...")
    server = ensure_server(cfg, commercial_type)
    put_user_data(cfg, server["id"])
    if server.get("state") not in {"running", "started"}:
        print("Powering on server...")
        server_action(cfg, server["id"], "poweron")
    server = wait_for_server(cfg, server["id"])
    ip = public_ip(server)
    if not ip:
        raise SystemExit("Server has no public IP in API response.")
    state = state_load()
    state.update({"server_id": server["id"], "public_ip": ip, "commercial_type": commercial_type})
    state_save(state)
    print(f"Server is running at {ip}. Waiting for SSH...")
    wait_ssh(ip)
    print("Installing Docker and deploying Langfuse...")
    deploy_stack(ip)
    print("Langfuse deployment command completed.")
    print(fetch_credentials(ip))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["probe", "deploy"])
    args = parser.parse_args()
    if args.command == "probe":
        probe()
    elif args.command == "deploy":
        create_and_deploy()


if __name__ == "__main__":
    main()
