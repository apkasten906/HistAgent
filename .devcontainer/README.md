# Docker development environment

1. Start Docker Desktop with Linux containers. On Windows, use its WSL 2 backend.
2. Install the VS Code **Dev Containers** extension (`ms-vscode-remote.remote-containers`).
3. Open this repository and run **Dev Containers: Reopen in Container**.
4. Wait for the image build and setup to finish. The first build downloads large
   Python packages and Chromium; allow several GB of disk space.
5. Add the application API keys to the ignored root `.env` file as described in
   the main README, and download HistBench using the existing installation steps.

The image supplies Python 3.12, a writable virtual environment at `/opt/venv`,
CPU-only PyTorch, Chromium/Playwright, FFmpeg, Poppler, Git LFS, and ripgrep.
Dev Container features add Node.js and GitHub CLI. Setup installs Codex CLI and
registers the checkout's modified `browser_use` package without copying sources
into site-packages. VS Code installs Python, Pylance, debugger, Ruff, Codex,
GitHub PR/Actions, container, YAML, TOML, and CSV extensions automatically.
Ruff formatting is available on demand; opening the project does not reformat it.

## Git and GitHub

Git author and committer default to `apkasten906 <apkasten@gmail.com>`.
`GITHUB_USER` and `GITHUB_EMAIL` are also available for scripts; these identify
the user but do not authenticate GitHub requests.

VS Code [forwards the host Git credential helper or SSH agent](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials).
For GitHub CLI, host `GH_TOKEN` and `GITHUB_TOKEN` variables are forwarded to
VS Code terminals and processes in the container. Set them before launching
VS Code, then reopen/rebuild the container after changes. Alternatively run
`gh auth login` inside the container. Check with `gh auth status`.
Never put token values in `devcontainer.json`.

## Codex authentication passthrough

The host's `.codex` directory is mounted read-only at `/mnt/host-codex`.
On first startup, setup copies an existing `auth.json` to a private Docker volume
at `/home/vscode/.codex`, shared by the container's Codex CLI and IDE extension.
Subsequent starts retain the container's refreshed credentials. Host configuration
and Windows paths are not copied. The mount grants this container read access to
your host Codex directory; credentials are never included in the image or repo.
This follows OpenAI's [cached-authentication transfer guidance](https://learn.chatgpt.com/docs/auth).

The default host path uses `USERPROFILE` on Windows and `HOME` on Linux/macOS.
If both are set, or you use a custom `CODEX_HOME`, replace the mount's `source`
with the actual host Codex directory. That directory must exist before opening
the container. If it is absent, create it or remove the host bind mount and log
in from the container instead.

Run `codex login status` in the container. If host credentials are stored in an OS
keychain, no auth file can be copied: sign in using the Codex sidebar or run
`codex login --device-auth` (requires device login enabled for your account).
The Docker volume preserves this login across rebuilds. To replace stale copied
credentials, run `codex logout`, then `bash .devcontainer/codex-auth.sh` after
signing in again on the host, or sign in directly inside the container.
This provides Codex access to the mounted repo; it does not transfer the current
desktop conversation or its connected apps into VS Code.

## Maintenance and checks

Rebuild the container after changing `requirements.txt` or the Dockerfile.
For interactive development, `python -m pip install ...` uses `/opt/venv`.
Run commands from the repository root. Browser automation normally runs headless.
This is a CPU development environment; GPU/CUDA support needs separate configuration.

```bash
python --version
python -m pip check
python -c "import browser_use; print(browser_use.__file__)"
codex --version
gh --version
git var GIT_AUTHOR_IDENT
```

API-backed benchmark runs require their service credentials and dataset. Creating
the development environment does not download datasets or run paid API requests.
