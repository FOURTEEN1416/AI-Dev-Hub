"""
FastAPI 应用入口
创建应用实例，配置中间件，注册路由
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.auth import router as auth_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.statistics import router as statistics_router
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化数据库表，关闭时释放资源"""
    # 启动时创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时释放引擎
    await engine.dispose()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI开发者机会聚合平台",
    description="聚合 AI 开发者相关的机会信息，包括开发者计划、竞赛、免费额度、社区活动等",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置 CORS 中间件，允许所有源访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器，捕获未处理的异常并返回统一格式"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"},
    )


# 注册 v1 版本路由
app.include_router(opportunities_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(favorites_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")


@app.get("/", tags=["根路由"])
async def root():
    """根路由，返回 API 基本信息"""
    return {
        "name": "AI开发者机会聚合平台",
        "version": "1.0.0",
        "description": "聚合 AI 开发者相关的机会信息",
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
