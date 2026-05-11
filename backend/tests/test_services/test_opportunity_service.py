"""
机会服务层测试
测试 OpportunityService 的业务逻辑
"""

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.opportunity import OpportunityCreate, OpportunityAdvancedFilter
from app.services.opportunity import OpportunityService


class TestOpportunityService:
    """机会服务层测试类"""

    async def test_create_opportunity(self, db_session: AsyncSession):
        """测试创建机会"""
        service = OpportunityService(db_session)
        
        data = OpportunityCreate(
            title="测试机会",
            type="competition",
            source="TestSource",
            description="这是一个测试机会",
            tags=["AI", "测试"],
            status="active"
        )
        
        result = await service.create_opportunity(data)
        
        assert result.id is not None
        assert result.title == "测试机会"
        assert result.type == "competition"
        assert result.source == "TestSource"

    async def test_get_opportunity(self, db_session: AsyncSession):
        """测试获取单个机会"""
        service = OpportunityService(db_session)
        
        # 先创建机会
        data = OpportunityCreate(
            title="测试机会",
            type="competition",
            source="TestSource",
            description="这是一个测试机会"
        )
        created = await service.create_opportunity(data)
        
        # 再获取
        result = await service.get_opportunity(created.id)
        
        assert result is not None
        assert result.id == created.id
        assert result.title == "测试机会"

    async def test_get_opportunity_not_found(self, db_session: AsyncSession):
        """测试获取不存在的机会"""
        service = OpportunityService(db_session)
        
        result = await service.get_opportunity(99999)
        
        assert result is None

    async def test_get_opportunities_with_pagination(self, db_session: AsyncSession):
        """测试分页获取机会列表"""
        service = OpportunityService(db_session)
        
        # 创建多个机会
        for i in range(5):
            data = OpportunityCreate(
                title=f"测试机会 {i}",
                type="competition",
                source="TestSource",
                description=f"描述 {i}"
            )
            await service.create_opportunity(data)
        
        # 获取第一页
        result = await service.get_opportunities(
            filters={},
            page=1,
            limit=2
        )
        
        assert result.total >= 5
        assert len(result.items) <= 2
        assert result.page == 1
        assert result.limit == 2

    async def test_get_opportunities_filter_by_type(self, db_session: AsyncSession):
        """测试按类型筛选机会"""
        service = OpportunityService(db_session)
        
        # 创建不同类型的机会
        data1 = OpportunityCreate(
            title="竞赛机会",
            type="competition",
            source="TestSource"
        )
        await service.create_opportunity(data1)
        
        data2 = OpportunityCreate(
            title="开发者计划",
            type="developer_program",
            source="TestSource"
        )
        await service.create_opportunity(data2)
        
        # 筛选竞赛类型
        result = await service.get_opportunities(
            filters={"type": "competition"},
            page=1,
            limit=10
        )
        
        for item in result.items:
            assert item.type == "competition"

    async def test_get_opportunities_filter_by_source(self, db_session: AsyncSession):
        """测试按来源筛选机会"""
        service = OpportunityService(db_session)
        
        # 创建不同来源的机会
        data1 = OpportunityCreate(
            title="机会1",
            type="competition",
            source="SourceA"
        )
        await service.create_opportunity(data1)
        
        data2 = OpportunityCreate(
            title="机会2",
            type="competition",
            source="SourceB"
        )
        await service.create_opportunity(data2)
        
        # 筛选指定来源
        result = await service.get_opportunities(
            filters={"source": "SourceA"},
            page=1,
            limit=10
        )
        
        for item in result.items:
            assert item.source == "SourceA"

    async def test_search_opportunities(self, db_session: AsyncSession):
        """测试搜索机会"""
        service = OpportunityService(db_session)
        
        # 创建机会
        data = OpportunityCreate(
            title="AI开发者大赛",
            type="competition",
            source="TestSource",
            description="这是一个关于人工智能的比赛"
        )
        await service.create_opportunity(data)
        
        # 搜索
        result = await service.search_opportunities(
            keyword="AI",
            page=1,
            limit=10
        )
        
        assert result.total >= 1
        # 验证搜索结果包含关键词
        for item in result.items:
            assert "AI" in item.title or "AI" in (item.description or "")

    async def test_get_distinct_types(self, db_session: AsyncSession):
        """测试获取所有类型"""
        service = OpportunityService(db_session)
        
        # 创建不同类型的机会
        types = ["competition", "developer_program", "free_credits"]
        for t in types:
            data = OpportunityCreate(
                title=f"机会_{t}",
                type=t,
                source="TestSource"
            )
            await service.create_opportunity(data)
        
        result = await service.get_distinct_types()
        
        assert isinstance(result, list)
        for t in types:
            assert t in result

    async def test_get_distinct_sources(self, db_session: AsyncSession):
        """测试获取所有来源"""
        service = OpportunityService(db_session)
        
        # 创建不同来源的机会
        sources = ["SourceA", "SourceB", "SourceC"]
        for s in sources:
            data = OpportunityCreate(
                title=f"机会_{s}",
                type="competition",
                source=s
            )
            await service.create_opportunity(data)
        
        result = await service.get_distinct_sources()
        
        assert isinstance(result, list)
        for s in sources:
            assert s in result

    async def test_get_opportunities_advanced(self, db_session: AsyncSession):
        """测试高级筛选"""
        service = OpportunityService(db_session)
        
        # 创建机会
        data = OpportunityCreate(
            title="AI大赛",
            type="competition",
            source="TestSource",
            description="人工智能比赛",
            tags=["AI", "机器学习"]
        )
        await service.create_opportunity(data)
        
        # 高级筛选
        filters = OpportunityAdvancedFilter(
            keyword="AI",
            types=["competition"],
            sort_by="created_at",
            sort_order="desc"
        )
        
        result = await service.get_opportunities_advanced(
            filters=filters,
            page=1,
            limit=10
        )
        
        assert result.total >= 1

    async def test_get_opportunities_advanced_with_date_filter(self, db_session: AsyncSession):
        """测试带日期范围的高级筛选"""
        service = OpportunityService(db_session)
        
        # 创建带截止日期的机会
        data = OpportunityCreate(
            title="即将截止的机会",
            type="competition",
            source="TestSource",
            deadline=datetime.now() + timedelta(days=7)
        )
        await service.create_opportunity(data)
        
        # 筛选有截止日期的机会
        filters = OpportunityAdvancedFilter(
            has_deadline=True
        )
        
        result = await service.get_opportunities_advanced(
            filters=filters,
            page=1,
            limit=10
        )
        
        for item in result.items:
            assert item.deadline is not None

    async def test_get_opportunities_sorting(self, db_session: AsyncSession):
        """测试排序功能"""
        service = OpportunityService(db_session)
        
        # 创建多个机会
        for i in range(3):
            data = OpportunityCreate(
                title=f"机会_{chr(65+i)}",  # A, B, C
                type="competition",
                source="TestSource"
            )
            await service.create_opportunity(data)
        
        # 按标题升序排序
        filters = OpportunityAdvancedFilter(
            sort_by="title",
            sort_order="asc"
        )
        
        result = await service.get_opportunities_advanced(
            filters=filters,
            page=1,
            limit=10
        )
        
        if len(result.items) >= 2:
            titles = [item.title for item in result.items]
            assert titles == sorted(titles)
