# AI开发者机会聚合平台

> 自动采集各大厂AI开发者计划、比赛信息、免费Token额度等福利，为AI开发者提供一站式机会发现平台。

## 🌟 项目简介

AI Dev Hub 是一个功能完善的AI开发者机会聚合平台，自动爬取并展示：
- 🏢 各大厂AI开发者计划（OpenAI、Google、AWS、Azure等）
- 🏆 AI相关比赛信息（Kaggle、天池、和鲸等）
- 🎁 免费Token/API额度福利
- 📢 技术社区热门动态（GitHub、Hacker News、V2EX、掘金等）

## ✨ 功能特性

### 核心功能
- 🔍 **机会聚合** - 自动采集多个平台的AI开发者机会
- 🏷️ **智能分类** - 按类型（开发者计划/比赛/免费额度/社区动态）分类展示
- 🔎 **全文搜索** - PostgreSQL 全文搜索，支持中文分词
- 🎯 **高级筛选** - 多维度筛选（类型、来源、标签、日期范围等）

### 用户系统
- 👤 **用户注册/登录** - 邮箱密码注册，JWT 认证
- ❤️ **收藏功能** - 收藏感兴趣的机会，随时查看
- 📊 **个人中心** - 管理个人信息和收藏列表

### 智能推荐
- 🤖 **个性化推荐** - 基于用户行为的协同过滤推荐
- 📈 **热门推荐** - 基于全局热度的机会推荐
- 🔗 **相似机会** - 基于标签和类型的相似度推荐
- 📊 **行为追踪** - 自动追踪用户行为优化推荐

### 消息通知
- 📧 **邮件订阅** - 每日/每周机会推送
- ⚙️ **偏好设置** - 自定义感兴趣的类型、来源、标签
- 🎯 **智能匹配** - 根据用户偏好精准推送

### 数据可视化
- 📈 **数据看板** - 机会统计、趋势分析
- 📊 **分布图表** - 来源分布、类型分布可视化
- ☁️ **标签云** - 热门标签一目了然
- 📅 **日历视图** - 截止日期日历提醒

## 🏗️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui + Recharts |
| 后端 | Python + FastAPI + SQLAlchemy 2.x |
| 数据库 | PostgreSQL 15 + Redis 7 |
| 爬虫 | Scrapy + Playwright + httpx |
| 认证 | JWT + bcrypt |
| 测试 | pytest + pytest-asyncio + pytest-cov |
| CI/CD | GitHub Actions + Docker |
| 部署 | Docker Compose + Nginx |

## 📁 项目结构

```
ai-dev-hub/
├── frontend/          # Next.js 前端
│   ├── src/app/       # 页面（首页、列表、详情、登录、注册、个人中心、数据看板、设置）
│   ├── src/components/# 组件（筛选、图表、仪表盘、认证、推荐、订阅等）
│   ├── src/hooks/     # 自定义 Hooks
│   ├── src/lib/       # API 封装、工具函数
│   └── src/store/     # Zustand 状态管理
├── backend/           # FastAPI 后端
│   ├── app/api/       # API 路由（36个端点）
│   ├── app/models/    # 数据模型
│   ├── app/schemas/   # Pydantic 模型
│   ├── app/services/  # 业务逻辑
│   ├── app/core/      # 核心配置
│   ├── app/templates/ # 邮件模板
│   └── tests/         # 测试套件
├── spiders/           # 爬虫服务
│   ├── spiders/github/       # GitHub Trending
│   ├── spiders/hackernews/   # Hacker News
│   ├── spiders/competitions/ # Kaggle、天池
│   ├── spiders/forums/       # V2EX、掘金
│   └── spiders/developer_programs/ # OpenAI 等
├── .github/           # GitHub Actions CI/CD
├── nginx/             # Nginx 配置
├── docker-compose.yml # 容器编排
├── Makefile           # 常用命令
└── .env.example       # 环境变量模板
```

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### Docker 一键启动

```bash
# 1. 克隆项目
git clone <repo-url>
cd ai-dev-hub

# 2. 配置环境变量
cp .env.example .env

# 3. 启动服务
docker compose up -d

# 4. 运行爬虫（首次需要）
docker compose run --rm spider python run.py --all
```

访问地址：
- 前端: http://localhost:3000
- API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

```bash
# 1. 配置环境变量
cp .env.example .env

# 2. 启动数据库和Redis
docker compose up -d db redis

# 3. 启动后端
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 4. 启动前端（新终端）
cd frontend
npm install
npm run dev

# 5. 运行爬虫（新终端）
cd spiders
pip install -r requirements.txt
python run.py --all
```

### 运行测试

```bash
cd backend
pytest -v --cov=app --cov-report=html
```

## 🕷️ 爬虫列表

| 爬虫 | 来源 | 类型 | 命令 |
|------|------|------|------|
| GitHub Trending | github.com | 社区动态 | `python run.py --spider github_trending` |
| Hacker News | news.ycombinator.com | 社区动态 | `python run.py --spider hackernews_hot` |
| Kaggle | kaggle.com | 比赛 | `python run.py --spider kaggle_competitions` |
| 天池 | tianchi.aliyun.com | 比赛 | `python run.py --spider tianchi` |
| V2EX | v2ex.com | 社区动态 | `python run.py --spider v2ex` |
| 掘金 | juejin.cn | 社区动态 | `python run.py --spider juejin` |
| OpenAI | openai.com | 开发者计划 | `python run.py --spider openai_programs` |

## 📖 API 文档

启动后端后访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

**机会相关**
- `GET /api/v1/opportunities` - 获取机会列表
- `GET /api/v1/opportunities/{id}` - 获取机会详情
- `GET /api/v1/opportunities/search` - 搜索机会
- `GET /api/v1/opportunities/search/advanced` - 高级搜索
- `POST /api/v1/opportunities` - 创建机会（爬虫使用）

**认证相关**
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户

**收藏相关**
- `GET /api/v1/favorites` - 获取收藏列表
- `POST /api/v1/favorites` - 添加收藏
- `DELETE /api/v1/favorites/{id}` - 取消收藏

**推荐相关**
- `GET /api/v1/recommendations` - 获取个性化推荐
- `GET /api/v1/recommendations/trending` - 获取热门推荐
- `GET /api/v1/recommendations/similar/{id}` - 获取相似机会
- `POST /api/v1/recommendations/behavior` - 记录用户行为

**通知相关**
- `POST /api/v1/notifications/subscribe` - 订阅通知
- `POST /api/v1/notifications/unsubscribe` - 取消订阅
- `GET /api/v1/notifications/settings` - 获取通知设置

**统计相关**
- `GET /api/v1/statistics/overview` - 概览统计
- `GET /api/v1/statistics/trend` - 趋势数据
- `GET /api/v1/statistics/distribution/source` - 来源分布
- `GET /api/v1/statistics/distribution/type` - 类型分布
- `GET /api/v1/statistics/tags/cloud` - 标签云

## 📝 常用命令

```bash
make help          # 查看所有命令
make dev           # 启动所有服务
make spider-all    # 运行所有爬虫
make migrate       # 运行数据库迁移
make test          # 运行测试
make logs          # 查看日志
make down          # 停止所有服务
make clean         # 清理所有资源
```

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| 项目文件 | 144+ |
| 后端 Python 文件 | 35+ |
| 前端 TS/TSX 文件 | 55+ |
| 爬虫 Python 文件 | 20+ |
| API 端点 | 36 |
| 爬虫源 | 7 |
| 测试用例 | 50+ |

## 🔧 环境变量配置

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_dev_hub

# Redis
REDIS_URL=redis://localhost:6379/0

# 安全
SECRET_KEY=your-secret-key

# 邮件（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 前端
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🤝 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与开发。

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 License

MIT
