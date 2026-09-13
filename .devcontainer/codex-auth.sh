#!/usr/bin/env bash
set -euo pipefail

# Seed once; allow the container to refresh its own credentials independently.
mkdir -p "$CODEX_HOME"
chmod 700 "$CODEX_HOME"
if [[ ! -f "$CODEX_HOME/auth.json" && -f /mnt/host-codex/auth.json ]]; then
    install -m 600 /mnt/host-codex/auth.json "$CODEX_HOME/auth.json"
fi
if [[ ! -f "$CODEX_HOME/config.toml" ]]; then
    printf 'cli_auth_credentials_store = "file"\n' > "$CODEX_HOME/config.toml"
    chmod 600 "$CODEX_HOME/config.toml"
fi
