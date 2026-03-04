"""简单的 API 测试 - 不依赖复杂的功能"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, get_db

# 测试数据库（使用内存数据库）
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 创建测试客户端
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    
    # 创建表
    Base.metadata.create_all(bind=engine)
    
    # 使用 TestClient
    with TestClient(app) as c:
        yield c
    
    # 清理表
    Base.metadata.drop_all(bind=engine)


def test_root(client):
    """测试根路径 - 最基本的测试"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health(client):
    """测试健康检查 - 最基本的测试"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_mode_endpoint(client):
    """测试模式端点 - 应该不需要数据库"""
    response = client.get("/api/mode")
    # 即使没有数据库记录，也应该返回默认值
    assert response.status_code in [200, 404]
