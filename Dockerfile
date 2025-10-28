FROM python:3.12-slim

WORKDIR /app

# 安装 curl 并安装 uv
RUN apt-get update && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 验证 uv 是否安装成功
RUN uv --version

COPY . .

CMD ["uv", "sync"]
