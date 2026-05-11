.PHONY: help dev build up down logs api spider spider-all migrate test lint

help: ## 显示帮助信息
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===== 开发命令 =====

dev: ## 启动所有服务（开发模式）
	docker compose up -d

build: ## 构建所有镜像
	docker compose build

up: ## 启动所有服务
	docker compose up -d

down: ## 停止所有服务
	docker compose down

logs: ## 查看日志
	docker compose logs -f

restart: ## 重启所有服务
	docker compose restart

# ===== 后端命令 =====

api: ## 启动后端 API 服务
	cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate: ## 运行数据库迁移
	cd backend && alembic upgrade head

makemigrations: ## 创建数据库迁移
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ===== 爬虫命令 =====

spider: ## 运行指定爬虫 (用法: make spider name=github_trending)
	cd spiders && pip install -r requirements.txt && python run.py --spider $(name)

spider-all: ## 运行所有爬虫
	cd spiders && pip install -r requirements.txt && python run.py --all

spider-list: ## 列出所有可用爬虫
	cd spiders && pip install -r requirements.txt && python run.py --list

spider-schedule: ## 启动定时爬虫调度
	cd spiders && pip install -r requirements.txt && python run.py --schedule

spider-docker: ## Docker 中运行爬虫
	docker compose run --rm spider python run.py --all

# ===== 前端命令 =====

frontend: ## 启动前端开发服务器
	cd frontend && npm install && npm run dev

frontend-build: ## 构建前端生产版本
	cd frontend && npm install && npm run build

# ===== 测试命令 =====

test: ## 运行所有测试
	cd backend && python -m pytest tests/ -v

lint: ## 代码检查
	cd frontend && npm run lint

# ===== 清理命令 =====

clean: ## 清理 Docker 资源
	docker compose down -v --rmi all

db-reset: ## 重置数据库
	docker compose down -v
	docker compose up -d db redis
	sleep 5
	cd backend && alembic upgrade head
