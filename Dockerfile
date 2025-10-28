FROM python:3.12-slim

# 安装 curl 并安装 uv
RUN apt-get update && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 把 uv 的路径加到全局 PATH
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY . .

# 默认执行 uv sync
CMD ["uv", "sync"]
