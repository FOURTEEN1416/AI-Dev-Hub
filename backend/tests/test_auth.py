"""
认证测试
测试用户注册、登录、获取用户信息等接口
"""


class TestAuth:
    """认证测试类"""

    async def test_register(self, client, test_user_data):
        """测试用户注册成功"""
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data

    async def test_register_duplicate_email(self, client, test_user_data):
        """测试重复邮箱注册失败"""
        # 第一次注册
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 第二次使用相同邮箱注册
        response = await client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "已被注册" in response.json()["detail"]

    async def test_register_duplicate_username(self, client, test_user_data):
        """测试重复用户名注册失败"""
        # 第一次注册
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 第二次使用相同用户名注册
        new_user = {
            "email": "another@example.com",
            "username": test_user_data["username"],
            "password": "Test123456"
        }
        response = await client.post("/api/v1/auth/register", json=new_user)
        assert response.status_code == 400
        assert "已被使用" in response.json()["detail"]

    async def test_login(self, client, test_user_data):
        """测试用户登录成功"""
        # 先注册用户
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 登录
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, test_user_data):
        """测试错误密码登录失败"""
        # 先注册用户
        await client.post("/api/v1/auth/register", json=test_user_data)
        # 使用错误密码登录
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录失败"""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "Test123456"
            }
        )
        assert response.status_code == 401

    async def test_get_current_user(self, auth_client):
        """测试获取当前用户信息"""
        response = await auth_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data

    async def test_unauthorized_access(self, client):
        """测试未认证访问受保护接口"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_logout(self, auth_client):
        """测试用户登出"""
        response = await auth_client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
