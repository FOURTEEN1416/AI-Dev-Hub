"""
爬虫数据模型模块
定义所有爬虫采集数据的 Pydantic 模型，用于数据标准化和验证
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class OpportunityType(str, Enum):
    """机会类型枚举"""
    COMMUNITY = "community"           # 社区项目
    COMPETITION = "competition"       # 竞赛
    FREE_CREDITS = "free_credits"     # 免费额度
    DEVELOPER_PROGRAM = "developer_program"  # 开发者计划
    GRANT = "grant"                   # 资助
    TOOL = "tool"                     # 工具


class OpportunityItem(BaseModel):
    """
    机会数据模型
    与后端 Opportunity 模型对应，用于爬虫数据标准化
    """

    # ==================== 必填字段 ====================
    # 标题
    title: str = Field(..., min_length=1, max_length=500, description="标题")

    # 描述
    description: str = Field(default="", max_length=5000, description="描述")

    # 来源 URL
    source_url: str = Field(..., min_length=1, max_length=2000, description="来源链接")

    # 来源平台
    source: str = Field(..., min_length=1, max_length=100, description="来源平台")

    # 机会类型
    type: str = Field(..., description="机会类型")

    # 标签列表
    tags: list[str] = Field(default_factory=list, description="标签列表")

    # ==================== 可选字段 ====================
    # 外部编号（如 GitHub 仓库全名、Kaggle 比赛编号等）
    external_id: Optional[str] = Field(default=None, max_length=500, description="外部编号")

    # 编程语言
    language: Optional[str] = Field(default=None, max_length=100, description="编程语言")

    # Star 数量
    stars: Optional[int] = Field(default=None, ge=0, description="Star 数量")

    # 今日 Star 增量
    stars_today: Optional[int] = Field(default=None, ge=0, description="今日 Star 增量")

    # 奖励金额
    reward: Optional[str] = Field(default=None, max_length=500, description="奖励")

    # 截止日期
    deadline: Optional[date] = Field(default=None, description="截止日期")

    # 额外元数据（JSON 格式存储）
    metadata: Optional[dict] = Field(default=None, description="额外元数据")

    # 采集时间
    collected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="采集时间"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "langchain - Build context-aware reasoning applications",
                "description": "Build context-aware reasoning applications",
                "source_url": "https://github.com/langchain-ai/langchain",
                "source": "GitHub",
                "type": "community",
                "tags": ["Python", "LLM", "AI"],
                "language": "Python",
                "stars": 50000,
                "stars_today": 200,
            }
        }


class SpiderResult(BaseModel):
    """
    爬虫运行结果模型
    记录单次爬虫运行的统计信息
    """

    # 爬虫名称
    spider_name: str = Field(..., description="爬虫名称")

    # 采集到的数据条数
    items_count: int = Field(default=0, ge=0, description="采集条数")

    # 过滤掉的数据条数
    filtered_count: int = Field(default=0, ge=0, description="过滤条数")

    # 去重后跳过的条数
    duplicate_count: int = Field(default=0, ge=0, description="去重跳过条数")

    # 成功入库的条数
    saved_count: int = Field(default=0, ge=0, description="入库条数")

    # 错误数量
    error_count: int = Field(default=0, ge=0, description="错误数量")

    # 运行耗时（秒）
    duration: float = Field(default=0.0, ge=0, description="运行耗时")

    # 是否成功完成
    success: bool = Field(default=True, description="是否成功")

    # 错误信息
    error_message: Optional[str] = Field(default=None, description="错误信息")

    # 运行时间戳
    ran_at: datetime = Field(default_factory=datetime.utcnow, description="运行时间")
