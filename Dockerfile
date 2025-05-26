# Dockerfile
FROM python:3.12-slim

# 1. Prevent .pyc files & buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 2. Install system deps and granian (uv)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL https://astral.sh/uv/install.sh | sh \
 && rm -f /uv-installer.sh

# 3. Make sure the binary is on PATH
ENV PATH="/root/.local/bin/:$PATH"

# 4. Install Python deps
WORKDIR /app
COPY . .
RUN uv sync --locked 

RUN python3 -m venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# 8. Copy and register entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
