FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# The Python base includes a Yarn apt source whose signing key is unavailable.
# Yarn is not needed here; Node.js is supplied by the devcontainer feature.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg git-lfs poppler-utils libgl1 libglib2.0-0 ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && python -m venv /opt/venv

COPY requirements.txt /tmp/histagent-requirements.txt
# CPU wheels avoid downloading CUDA libraries for a general development container.
RUN pip install --no-cache-dir torch==2.2.0 torchvision==0.17.0 \
        --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /tmp/histagent-requirements.txt \
        'smolagents[litellm]==1.15.0' \
    && python -m playwright install --with-deps chromium \
    && chmod -R a+rX /opt/playwright \
    && chown -R vscode:vscode /opt/venv \
    && mkdir -p /home/vscode/.codex \
    && chown vscode:vscode /home/vscode/.codex \
    && rm -rf /var/lib/apt/lists/*
