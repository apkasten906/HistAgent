#!/usr/bin/env bash
set -euo pipefail

git config --global user.name "$GIT_AUTHOR_NAME"
git config --global user.email "$GIT_AUTHOR_EMAIL"
git config --global github.user "$GITHUB_USER"
git lfs install --skip-repo

# Register the checkout so Python uses this repo's modified browser_use package.
python - <<'PY'
from pathlib import Path
import site

(Path(site.getsitepackages()[0]) / "histagent-workspace.pth").write_text(
    str(Path.cwd()) + "\n"
)
PY

npm install --global @openai/codex
bash .devcontainer/codex-auth.sh
