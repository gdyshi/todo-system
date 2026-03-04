"""Tasks API 测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


def test_create_task(client):
    """测试：创建任务"""
    response = client.post(
        "/api/tasks",
        json={
            "title": "测试任务",
            "category": "work",
            "priority": 5,
            "description": "这是一个测试描述"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试任务"
    assert data["category"] == "work"
    assert data["priority"] == 5
    assert data["description"] == "这是一个测试描述"
    assert data["status"] == "pending"


def test_create_task_invalid_title(client):
    """测试：创建任务（无效标题）"""
    response = client.post(
        "/api/tasks",
        json={
            "title": "",  # 空标题
            "category": "work"
        }
    )
    
    assert response.status_code == 422  # Unprocessable Entity


def test_create_task_auto_category(client):
    """测试：创建任务（自动分类）"""
    response = client.post(
        "/api/tasks",
        json={
            "title": "自动分类任务",
            "category": "auto"  # 自动分类
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "自动分类任务"
    assert data["category"] == "work" or data["category"] == "life" or data["category"] == "education"


def test_get_tasks(client):
    """测试：获取任务列表"""
    # 先创建几个任务
    client.post("/api/tasks", json={"title": "任务1", "category": "work"})
    client.post("/api/tasks", json={"title": "任务2", "category": "life"})
    
    # 获取所有任务
    response = client.get("/api/tasks")
    
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 2


def test_get_tasks_with_filter(client):
    """测试：获取任务列表（带筛选）"""
    # 创建不同分类的任务
    client.post("/api/tasks", json={"title": "工作任务", "category": "work"})
    client.post("/api/tasks", json={"title": "生活任务", "category": "life"})
    
    # 筛选工作任务
    response = client.get("/api/tasks?category=work")
    
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["category"] == "work" for task in tasks)


def test_get_task_by_id(client):
    """测试：根据 ID 获取任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={"title": "待查询任务"}
    )
    task_id = create_response.json()["id"]
    
    # 根据 ID 获取任务
    response = client.get(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == "待查询任务"


def test_get_task_not_found(client):
    """测试：根据 ID 获取任务（不存在）"""
    response = client.get("/api/tasks/99999")
    
    assert response.status_code == 404


def test_update_task(client):
    """测试：更新任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={"title": "原标题", "priority": 5}
    )
    task_id = create_response.json()["id"]
    
    # 更新任务
    response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "更新后的标题",
            "priority": 9
        }
    )
    
    assert response.status_code == 200
    task = response.json()
    assert task["title"] == "更新后的标题"
    assert task["priority"] == 9


def test_complete_task(client):
    """测试：完成任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={"title": "待完成任务"}
    )
    task_id = create_response.json()["id"]
    
    # 完成任务
    response = client.post(f"/api/tasks/{task_id}/complete")
    
    assert response.status_code == 200
    task = response.json()
    assert task["status"] == "completed"


def test_complete_task_with_incomplete_subtasks(client):
    """测试：完成任务时有未完成的子任务"""
    # 创建带子任务的任务
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "父任务",
            "subtasks": ["子任务1", "子任务2"]
        }
    )
    task_id = create_response.json()["id"]
    
    # 只完成一个子任务
    all_tasks = client.get("/api/tasks").json()
    subtask = [t for t in all_tasks if t["parent_id"] == task_id][0]
    client.post(f"/api/tasks/{subtask['id']}/complete")
    
    # 尝试完成父任务
    response = client.post(f"/api/tasks/{task_id}/complete")
    
    assert response.status_code == 400  # Bad Request
    assert "请先完成所有子任务" in response.json()["detail"]


def test_delete_task(client):
    """测试：删除任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={"title": "待删除任务"}
    )
    task_id = create_response.json()["id"]
    
    # 删除任务
    response = client.delete(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "任务已删除"


def test_delete_task_not_found(client):
    """测试：删除任务（不存在）"""
    response = client.delete("/api/tasks/99999")
    
    assert response.status_code == 404


def test_split_task(client):
    """测试：拆解任务"""
    # 创建任务
    create_response = client.post(
        "/api/tasks",
        json={"title": "待拆解任务", "category": "work"}
    )
    task_id = create_response.json()["id"]
    
    # 拆解任务
    response = client.post(
        f"/api/tasks/{task_id}/split",
        json={"subtasks": ["子任务1", "子任务2", "子任务3"]}
    )
    
    assert response.status_code == 200
    subtasks = response.json()
    assert len(subtasks) == 3
    assert subtasks[0]["title"] == "子任务1"


def test_get_stats(client):
    """测试：获取统计信息"""
    # 创建一些任务
    client.post("/api/tasks", json={"title": "任务1", "category": "work", "status": "completed"})
    client.post("/api/tasks", json={"title": "任务2", "category": "work", "status": "pending"})
    client.post("/api/tasks", json={"title": "任务3", "category": "life", "status": "in_progress"})
    
    # 获取统计
    response = client.get("/api/stats")
    
    assert response.status_code == 200
    stats = response.json()
    assert stats["total"] == 3
    assert stats["completed"] == 1
    assert stats["pending"] == 1
    assert stats["in_progress"] == 1


def test_get_mode(client):
    """测试：获取模式信息"""
    response = client.get("/api/mode")
    
    assert response.status_code == 200
    mode_info = response.json()
    assert "mode" in mode_info
    assert "ip" in mode_info


def test_set_manual_mode(client):
    """测试：设置手动模式"""
    response = client.post(
        "/api/mode",
        json={"mode": "manual", "category": "work"}
    )
    
    assert response.status_code == 200
    mode_info = response.json()
    assert mode_info["mode"] == "manual"
    assert mode_info["category"] == "work"


def test_set_auto_mode(client):
    """测试：设置自动模式"""
    response = client.post(
        "/api/mode",
        json={"mode": "auto"}
    )
    
    assert response.status_code == 200
    mode_info = response.json()
    assert mode_info["mode"] == "auto"


def test_health_check(client):
    """测试：健康检查"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(client):
    """测试：根路径"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
