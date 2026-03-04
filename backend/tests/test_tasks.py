import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base, get_db

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """设置测试数据库"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task():
    """测试创建任务"""
    response = client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "description": "这是一个测试任务",
            "priority": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试任务"
    assert data["description"] == "这是一个测试任务"
    assert data["priority"] == 5
    assert data["status"] == "pending"
    assert "id" in data


def test_get_tasks():
    """测试获取任务列表"""
    # 先创建一个任务
    client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "description": "这是一个测试任务"
        }
    )

    # 获取任务列表
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "测试任务"


def test_get_task():
    """测试获取单个任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "description": "这是一个测试任务"
        }
    )
    task_id = create_response.json()["id"]

    # 获取任务
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "测试任务"


def test_complete_task():
    """测试完成任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "description": "这是一个测试任务"
        }
    )
    task_id = create_response.json()["id"]

    # 完成任务
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_delete_task():
    """测试删除任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "description": "这是一个测试任务"
        }
    )
    task_id = create_response.json()["id"]

    # 删除任务
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200

    # 验证已删除
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_split_task():
    """测试拆解任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "父任务",
            "description": "这是一个父任务"
        }
    )
    task_id = create_response.json()["id"]

    # 拆解任务
    response = client.post(
        f"/api/tasks/{task_id}/split",
        json={
            "subtasks": ["子任务1", "子任务2", "子任务3"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "子任务1"
    assert data[0]["parent_id"] == task_id


def test_get_stats():
    """测试获取统计信息"""
    # 创建几个任务
    client.post("/api/tasks", json={"title": "任务1"})
    client.post("/api/tasks", json={"title": "任务2"})

    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "completed" in data
    assert "pending" in data
    assert "in_progress" in data
    assert "by_category" in data


def test_get_mode():
    """测试获取模式信息"""
    response = client.get("/api/mode")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "ip" in data


def test_set_manual_mode():
    """测试设置手动模式"""
    response = client.post(
        "/api/mode",
        json={
            "mode": "manual",
            "category": "work"
        }
    )
    assert response.status_code == 200

    # 验证模式已设置
    mode_response = client.get("/api/mode")
    mode_data = mode_response.json()
    assert mode_data["mode"] == "manual"
    assert mode_data["category"] == "work"


def test_set_auto_mode():
    """测试设置自动模式"""
    response = client.post("/api/mode", json={"mode": "auto"})
    assert response.status_code == 200

    # 验证模式已设置
    mode_response = client.get("/api/mode")
    mode_data = mode_response.json()
    assert mode_data["mode"] == "auto"


def test_complete_task_with_subtasks():
    """测试完成任务时检查子任务"""
    # 创建父任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "父任务",
            "subtasks": ["子任务1", "子任务2"]
        }
    )
    task_id = create_response.json()["id"]

    # 尝试完成父任务（应该失败）
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 400

    # 完成子任务
    subtasks = client.get("/api/tasks").json()
    parent_task = next(t for t in subtasks if t["id"] == task_id)
    for subtask in parent_task["subtasks"]:
        client.post(f"/api/tasks/{subtask['id']}/complete")

    # 再次完成父任务（应该成功）
    response = client.post(f"/api/tasks/{task_id}/complete")
    assert response.status_code == 200


def test_task_priority_filtering():
    """测试按优先级过滤任务"""
    # 创建不同优先级的任务
    client.post("/api/tasks", json={"title": "高优先级任务", "priority": 10})
    client.post("/api/tasks", json={"title": "中优先级任务", "priority": 5})
    client.post("/api/tasks", json={"title": "低优先级任务", "priority": 1})

    # 获取所有任务
    response = client.get("/api/tasks")
    tasks = response.json()

    # 验证优先级正确设置
    high_priority = [t for t in tasks if t["priority"] >= 8]
    assert len(high_priority) > 0
    assert any(t["title"] == "高优先级任务" for t in high_priority)
