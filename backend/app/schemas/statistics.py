"""
统计（Statistics）Pydantic 数据模式
定义统计相关的请求和响应数据验证模式
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    """概览统计数据响应模式"""

    total_opportunities: int = Field(..., description="总机会数")
    by_type: dict[str, int] = Field(..., description="按类型统计")
    by_source: dict[str, int] = Field(..., description="按来源统计")
    active_count: int = Field(..., description="活跃机会数")
    expiring_soon: int = Field(..., description="即将截止的数量（7天内）")


class TrendDataPoint(BaseModel):
    """趋势数据点"""

    date: str = Field(..., description="日期")
    count: int = Field(..., description="新增数量")
    by_type: dict[str, int] = Field(default_factory=dict, description="按类型分组")


class TrendDataResponse(BaseModel):
    """趋势数据响应模式"""

    data: list[TrendDataPoint] = Field(..., description="趋势数据列表")
    total: int = Field(..., description="总计数量")


class DistributionItem(BaseModel):
    """分布数据项"""

    name: str = Field(..., description="名称")
    count: int = Field(..., description="数量")
    percentage: float = Field(..., description="百分比")


class DistributionResponse(BaseModel):
    """分布数据响应模式"""

    items: list[DistributionItem] = Field(..., description="分布数据列表")
    total: int = Field(..., description="总计数量")


class TagCloudItem(BaseModel):
    """标签云数据项"""

    tag: str = Field(..., description="标签名")
    count: int = Field(..., description="出现次数")
    size: int = Field(..., ge=1, le=5, description="相对大小（1-5）")


class TagCloudResponse(BaseModel):
    """标签云响应模式"""

    items: list[TagCloudItem] = Field(..., description="标签云数据列表")


class CalendarOpportunity(BaseModel):
    """日历中的机会简要信息"""

    id: int = Field(..., description="机会ID")
    title: str = Field(..., description="机会标题")
    type: str = Field(..., description="机会类型")
    source: str = Field(..., description="来源平台")
    deadline: Optional[str] = Field(None, description="截止日期")


class CalendarEvent(BaseModel):
    """日历事件"""

    date: str = Field(..., description="日期")
    opportunities: list[CalendarOpportunity] = Field(..., description="当日截止的机会列表")


class CalendarResponse(BaseModel):
    """日历响应模式"""

    events: list[CalendarEvent] = Field(..., description="日历事件列表")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
