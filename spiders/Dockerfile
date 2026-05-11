FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 安装 Playwright 浏览器及其依赖
RUN playwright install chromium && \
    playwright install-deps chromium

# 复制项目代码
COPY . .

# 创建非 root 用户
RUN groupadd -r spider && useradd -r -g spider -d /app -s /sbin/nologin spider && \
    chown -R spider:spider /app

# 切换到非 root 用户
USER spider

# 默认运行所有爬虫
ENTRYPOINT ["python", "run.py"]
CMD ["--all"]
