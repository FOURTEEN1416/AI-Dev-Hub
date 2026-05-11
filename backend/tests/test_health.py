"""
健康检查测试
测试应用的根路由和健康检查接口
"""


class TestHealth:
    """健康检查测试类"""

    async def test_health_check(self, client):
        """测试健康检查接口返回正常状态"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_root_endpoint(self, client):
        """测试根路由返回API基本信息"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "AI开发者机会聚合平台"
