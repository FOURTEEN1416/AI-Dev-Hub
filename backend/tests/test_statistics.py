"""
统计测试
测试统计相关的接口
"""


class TestStatistics:
    """统计测试类"""

    async def test_overview_stats(self, client):
        """测试获取概览统计"""
        response = await client.get("/api/v1/statistics/overview")
        assert response.status_code == 200
        data = response.json()
        # 验证返回的字段
        assert "total_opportunities" in data
        assert "by_type" in data
        assert "by_source" in data
        assert "active_count" in data
        assert "expiring_soon" in data

    async def test_overview_stats_with_data(self, client, test_opportunity_data):
        """测试有数据时的概览统计"""
        # 创建一些机会
        for i in range(3):
            data = test_opportunity_data.copy()
            data["title"] = f"测试机会 {i}"
            await client.post("/api/v1/opportunities", json=data)
        
        response = await client.get("/api/v1/statistics/overview")
        assert response.status_code == 200
        data = response.json()
        assert data["total_opportunities"] >= 3

    async def test_trend_data(self, client):
        """测试获取趋势数据"""
        response = await client.get("/api/v1/statistics/trend?days=7")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data

    async def test_trend_data_with_group_by(self, client):
        """测试不同分组方式的趋势数据"""
        # 按天分组
        response = await client.get("/api/v1/statistics/trend?days=30&group_by=day")
        assert response.status_code == 200
        
        # 按周分组
        response = await client.get("/api/v1/statistics/trend?days=30&group_by=week")
        assert response.status_code == 200
        
        # 按月分组
        response = await client.get("/api/v1/statistics/trend?days=90&group_by=month")
        assert response.status_code == 200

    async def test_trend_data_invalid_group_by(self, client):
        """测试无效的分组方式"""
        response = await client.get("/api/v1/statistics/trend?days=30&group_by=invalid")
        assert response.status_code == 422

    async def test_trend_data_days_range(self, client):
        """测试趋势数据天数范围"""
        # 最小天数
        response = await client.get("/api/v1/statistics/trend?days=1")
        assert response.status_code == 200
        
        # 最大天数
        response = await client.get("/api/v1/statistics/trend?days=365")
        assert response.status_code == 200

    async def test_source_distribution(self, client):
        """测试获取来源分布"""
        response = await client.get("/api/v1/statistics/distribution/source")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_type_distribution(self, client):
        """测试获取类型分布"""
        response = await client.get("/api/v1/statistics/distribution/type")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_distribution_with_data(self, client, test_opportunity_data):
        """测试有数据时的分布统计"""
        # 创建不同类型和来源的机会
        data1 = test_opportunity_data.copy()
        data1["type"] = "competition"
        data1["source"] = "SourceA"
        await client.post("/api/v1/opportunities", json=data1)
        
        data2 = test_opportunity_data.copy()
        data2["type"] = "developer_program"
        data2["source"] = "SourceB"
        data2["title"] = "开发者计划"
        await client.post("/api/v1/opportunities", json=data2)
        
        # 检查类型分布
        response = await client.get("/api/v1/statistics/distribution/type")
        assert response.status_code == 200
        
        # 检查来源分布
        response = await client.get("/api/v1/statistics/distribution/source")
        assert response.status_code == 200

    async def test_tag_cloud(self, client):
        """测试获取标签云"""
        response = await client.get("/api/v1/statistics/tags/cloud")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_tag_cloud_with_limit(self, client):
        """测试带数量限制的标签云"""
        response = await client.get("/api/v1/statistics/tags/cloud?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 10

    async def test_tag_cloud_with_data(self, client, test_opportunity_data):
        """测试有数据时的标签云"""
        # 创建带标签的机会
        await client.post("/api/v1/opportunities", json=test_opportunity_data)
        
        response = await client.get("/api/v1/statistics/tags/cloud")
        assert response.status_code == 200

    async def test_deadline_calendar(self, client):
        """测试获取截止日期日历"""
        from datetime import date, timedelta
        
        today = date.today()
        start_date = today.isoformat()
        end_date = (today + timedelta(days=30)).isoformat()
        
        response = await client.get(
            f"/api/v1/statistics/calendar?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "start_date" in data
        assert "end_date" in data

    async def test_deadline_calendar_with_data(self, client, test_opportunity_data):
        """测试有截止日期数据的日历"""
        from datetime import datetime, timedelta, date
        
        # 创建带截止日期的机会
        data = test_opportunity_data.copy()
        data["deadline"] = (datetime.now() + timedelta(days=7)).isoformat()
        data["title"] = "带截止日期的机会"
        await client.post("/api/v1/opportunities", json=data)
        
        today = date.today()
        start_date = today.isoformat()
        end_date = (today + timedelta(days=30)).isoformat()
        
        response = await client.get(
            f"/api/v1/statistics/calendar?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
