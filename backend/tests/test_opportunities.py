"""
机会API测试
测试机会的增删改查和搜索接口
"""


class TestOpportunities:
    """机会API测试类"""

    async def test_list_opportunities(self, client):
        """测试获取机会列表"""
        response = await client.get("/api/v1/opportunities")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    async def test_create_opportunity(self, client, test_opportunity_data):
        """测试创建机会"""
        response = await client.post("/api/v1/opportunities", json=test_opportunity_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_opportunity_data["title"]
        assert data["type"] == test_opportunity_data["type"]
        assert data["source"] == test_opportunity_data["source"]
        assert "id" in data

    async def test_get_opportunity(self, client, test_opportunity_data):
        """测试获取单个机会详情"""
        # 先创建机会
        create_resp = await client.post("/api/v1/opportunities", json=test_opportunity_data)
        assert create_resp.status_code == 201
        opp_id = create_resp.json()["id"]
        
        # 再获取该机会
        response = await client.get(f"/api/v1/opportunities/{opp_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == opp_id
        assert data["title"] == test_opportunity_data["title"]

    async def test_get_nonexistent_opportunity(self, client):
        """测试获取不存在的机会"""
        response = await client.get("/api/v1/opportunities/99999")
        assert response.status_code == 404

    async def test_search_opportunities(self, client, test_opportunity_data):
        """测试搜索机会"""
        # 先创建一个机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        # 搜索
        response = await client.get("/api/v1/opportunities/search?keyword=测试")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_search_opportunities_empty_keyword(self, client):
        """测试空关键词搜索"""
        response = await client.get("/api/v1/opportunities/search?keyword=")
        # 空关键词应该返回422验证错误
        assert response.status_code == 422

    async def test_filter_by_type(self, client, test_opportunity_data):
        """测试按类型筛选机会"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        # 按类型筛选
        response = await client.get("/api/v1/opportunities?type=competition")
        assert response.status_code == 200
        data = response.json()
        # 验证返回的数据都是指定类型
        for item in data["items"]:
            assert item["type"] == "competition"

    async def test_filter_by_source(self, client, test_opportunity_data):
        """测试按来源筛选机会"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        # 按来源筛选
        response = await client.get("/api/v1/opportunities?source=TestSource")
        assert response.status_code == 200

    async def test_filter_by_status(self, client, test_opportunity_data):
        """测试按状态筛选机会"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        # 按状态筛选
        response = await client.get("/api/v1/opportunities?status=active")
        assert response.status_code == 200

    async def test_pagination(self, client, test_opportunity_data):
        """测试分页功能"""
        # 创建多个机会
        for i in range(5):
            data = test_opportunity_data.copy()
            data["title"] = f"测试机会 {i}"
            await client.post("/api/v1/opportunities", json=data)
        
        # 测试第一页
        response = await client.get("/api/v1/opportunities?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["limit"] == 2

    async def test_get_opportunity_types(self, client, test_opportunity_data):
        """测试获取所有机会类型"""
        # 创建不同类型的机会
        data1 = test_opportunity_data.copy()
        data1["type"] = "competition"
        await client.post("/api/v1/opportunities", json=data1)
        
        data2 = test_opportunity_data.copy()
        data2["type"] = "developer_program"
        data2["title"] = "开发者计划"
        await client.post("/api/v1/opportunities", json=data2)
        
        response = await client.get("/api/v1/opportunities/types")
        assert response.status_code == 200
        types = response.json()
        assert isinstance(types, list)

    async def test_get_opportunity_sources(self, client, test_opportunity_data):
        """测试获取所有来源"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        response = await client.get("/api/v1/opportunities/sources")
        assert response.status_code == 200
        sources = response.json()
        assert isinstance(sources, list)

    async def test_get_popular_tags(self, client, test_opportunity_data):
        """测试获取热门标签"""
        # 创建带标签的机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        response = await client.get("/api/v1/opportunities/tags/popular")
        assert response.status_code == 200
        tags = response.json()
        assert isinstance(tags, list)

    async def test_get_filter_options(self, client, test_opportunity_data):
        """测试获取筛选选项"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        response = await client.get("/api/v1/opportunities/filters/options")
        assert response.status_code == 200
        options = response.json()
        assert "types" in options
        assert "sources" in options
        assert "tags" in options

    async def test_advanced_search(self, client, test_opportunity_data):
        """测试高级搜索"""
        # 创建机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        # 高级搜索
        response = await client.get(
            "/api/v1/opportunities/search/advanced?keyword=测试&types=competition"
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
