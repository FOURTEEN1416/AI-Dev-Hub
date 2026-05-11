"""
收藏测试
测试用户收藏的增删查接口
"""


class TestFavorites:
    """收藏测试类"""

    async def test_add_favorite(self, auth_client, test_opportunity_data):
        """测试添加收藏"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        assert create_resp.status_code == 201
        opp_id = create_resp.json()["id"]
        
        # 添加收藏
        response = await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "收藏成功"
        assert data["data"]["opportunity_id"] == opp_id

    async def test_add_favorite_duplicate(self, auth_client, test_opportunity_data):
        """测试重复收藏"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        opp_id = create_resp.json()["id"]
        
        # 第一次收藏
        await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        
        # 第二次收藏同一机会
        response = await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        assert response.status_code == 400
        assert "已收藏" in response.json()["detail"]

    async def test_add_favorite_nonexistent_opportunity(self, auth_client):
        """测试收藏不存在的机会"""
        response = await auth_client.post("/api/v1/favorites?opportunity_id=99999")
        assert response.status_code == 404

    async def test_remove_favorite(self, auth_client, test_opportunity_data):
        """测试取消收藏"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        opp_id = create_resp.json()["id"]
        
        # 添加收藏
        await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        
        # 取消收藏
        response = await auth_client.delete(f"/api/v1/favorites/{opp_id}")
        assert response.status_code == 200
        assert "成功" in response.json()["message"]

    async def test_remove_favorite_not_exist(self, auth_client):
        """测试取消不存在的收藏"""
        response = await auth_client.delete("/api/v1/favorites/99999")
        assert response.status_code == 404

    async def test_get_favorites(self, auth_client, test_opportunity_data):
        """测试获取收藏列表"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        opp_id = create_resp.json()["id"]
        
        # 添加收藏
        await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        
        # 获取收藏列表
        response = await auth_client.get("/api/v1/favorites")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_get_favorites_empty(self, auth_client):
        """测试获取空收藏列表"""
        response = await auth_client.get("/api/v1/favorites")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_check_favorite_true(self, auth_client, test_opportunity_data):
        """测试检查已收藏的机会"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        opp_id = create_resp.json()["id"]
        
        # 添加收藏
        await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        
        # 检查收藏状态
        response = await auth_client.get(f"/api/v1/favorites/check/{opp_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorited"] is True

    async def test_check_favorite_false(self, auth_client, test_opportunity_data):
        """测试检查未收藏的机会"""
        # 先创建机会
        create_resp = await auth_client.post("/api/v1/opportunities", json=test_opportunity_data)
        opp_id = create_resp.json()["id"]
        
        # 不添加收藏，直接检查
        response = await auth_client.get(f"/api/v1/favorites/check/{opp_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_favorited"] is False

    async def test_unauthorized_favorite(self, client):
        """测试未认证用户访问收藏接口"""
        # 尝试添加收藏
        response = await client.post("/api/v1/favorites?opportunity_id=1")
        assert response.status_code == 401
        
        # 尝试获取收藏列表
        response = await client.get("/api/v1/favorites")
        assert response.status_code == 401
        
        # 尝试取消收藏
        response = await client.delete("/api/v1/favorites/1")
        assert response.status_code == 401

    async def test_favorites_pagination(self, auth_client, test_opportunity_data):
        """测试收藏列表分页"""
        # 创建多个机会并收藏
        for i in range(5):
            data = test_opportunity_data.copy()
            data["title"] = f"测试机会 {i}"
            create_resp = await auth_client.post("/api/v1/opportunities", json=data)
            opp_id = create_resp.json()["id"]
            await auth_client.post(f"/api/v1/favorites?opportunity_id={opp_id}")
        
        # 测试分页
        response = await auth_client.get("/api/v1/favorites?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["limit"] == 2
