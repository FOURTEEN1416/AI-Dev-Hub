"""
机会（Opportunity）Pydantic 数据模式
定义请求和响应的数据验证模式
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OpportunityAdvancedFilter(BaseModel):
    """高级筛选模式，支持多条件组合筛选"""

    keyword: Optional[str] = Field(None, description="搜索关键词")
    types: Optional[list[str]] = Field(None, description="多选类型列表")
    sources: Optional[list[str]] = Field(None, description="多选来源列表")
    tags: Optional[list[str]] = Field(None, description="多选标签列表")
    status: Optional[str] = Field(None, description="状态筛选")
    has_deadline: Optional[bool] = Field(None, description="是否有截止日期")
    deadline_start: Optional[datetime] = Field(None, description="截止日期范围-开始")
    deadline_end: Optional[datetime] = Field(None, description="截止日期范围-结束")
    created_start: Optional[datetime] = Field(None, description="创建时间范围-开始")
    created_end: Optional[datetime] = Field(None, description="创建时间范围-结束")
    sort_by: str = Field("created_at", description="排序字段：created_at/deadline/title")
    sort_order: str = Field("desc", description="排序方向：asc/desc")


class OpportunityBase(BaseModel):
    """机会基础模式，包含所有可编辑字段"""

    title: str = Field(..., max_length=500, description="机会标题")
    type: str = Field(..., max_length=50, description="机会类型：developer_program/competition/free_credits/community")
    source: str = Field(..., max_length=100, description="来源平台")
    source_url: Optional[str] = Field(None, description="来源页面链接")
    description: Optional[str] = Field(None, description="详细描述")
    tags: Optional[list[str]] = Field(None, description="标签列表")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    reward: Optional[str] = Field(None, description="奖励说明")
    requirements: Optional[str] = Field(None, description="参与要求")
    official_link: Optional[str] = Field(None, description="官方链接")
    status: str = Field("active", max_length=20, description="状态：active/closed/expired")


class OpportunityCreate(OpportunityBase):
    """创建机会的请求模式"""

    pass


class OpportunityUpdate(BaseModel):
    """更新机会的请求模式，所有字段均可选"""

    title: Optional[str] = Field(None, max_length=500, description="机会标题")
    type: Optional[str] = Field(None, max_length=50, description="机会类型")
    source: Optional[str] = Field(None, max_length=100, description="来源平台")
    source_url: Optional[str] = Field(None, description="来源页面链接")
    description: Optional[str] = Field(None, description="详细描述")
    tags: Optional[list[str]] = Field(None, description="标签列表")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    reward: Optional[str] = Field(None, description="奖励说明")
    requirements: Optional[str] = Field(None, description="参与要求")
    official_link: Optional[str] = Field(None, description="官方链接")
    status: Optional[str] = Field(None, max_length=20, description="状态")


class OpportunityResponse(OpportunityBase):
    """机会响应模式，包含数据库生成的字段"""

    id: int = Field(..., description="主键ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = {"from_attributes": True}


class OpportunityListResponse(BaseModel):
    """机会列表分页响应模式"""

    items: list[OpportunityResponse] = Field(..., description="机会列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
