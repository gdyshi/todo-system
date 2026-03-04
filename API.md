# API文档

本系统提供RESTful API接口，所有接口返回JSON格式数据。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **Content-Type**: `application/json`

## 认证

当前版本不需要认证（个人使用）。

## 接口列表

### 任务管理

#### 获取任务列表

```
GET /api/tasks
```

**查询参数**：
- `category` (可选): 任务分类（work/life/education）
- `status` (可选): 任务状态（pending/in_progress/completed）

**响应示例**：
```json
[
  {
    "id": 1,
    "title": "完成项目报告",
    "description": "需要在周五之前完成",
    "category": "work",
    "status": "pending",
    "parent_id": null,
    "priority": 5,
    "due_time": "2026-03-05T18:00:00",
    "location": null,
    "reminder_sent": false,
    "created_at": "2026-03-01T12:00:00",
    "updated_at": "2026-03-01T12:00:00",
    "subtasks": []
  }
]
```

#### 获取单个任务

```
GET /api/tasks/{task_id}
```

**响应示例**：同上

#### 创建任务

```
POST /api/tasks
```

**请求体**：
```json
{
  "title": "完成项目报告",
  "description": "需要在周五之前完成",
  "category": "work",
  "priority": 5,
  "due_time": "2026-03-05T18:00:00",
  "location": "{\"lat\": 31.2304, \"lon\": 121.4737}",
  "subtasks": ["收集数据", "写分析", "做PPT"]
}
```

**字段说明**：
- `title` (必填): 任务标题
- `description` (可选): 任务描述
- `category` (可选): 任务分类（不填则自动检测）
- `priority` (可选): 优先级 0-9，默认0
- `due_time` (可选): 截止时间（ISO 8601格式）
- `location` (可选): 地点坐标（JSON字符串）
- `subtasks` (可选): 子任务列表

**响应示例**：
```json
{
  "id": 1,
  "title": "完成项目报告",
  "description": "需要在周五之前完成",
  "category": "work",
  "status": "pending",
  "parent_id": null,
  "priority": 5,
  "due_time": "2026-03-05T18:00:00",
  "location": "{\"lat\": 31.2304, \"lon\": 121.4737}",
  "reminder_sent": false,
  "created_at": "2026-03-01T12:00:00",
  "updated_at": "2026-03-01T12:00:00",
  "subtasks": [
    {
      "id": 2,
      "title": "收集数据",
      "category": "work",
      "status": "pending"
    }
  ]
}
```

#### 更新任务

```
PUT /api/tasks/{task_id}
```

**请求体**：
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "priority": 9
}
```

**响应示例**：同创建任务

#### 完成任务

```
POST /api/tasks/{task_id}/complete
```

**响应示例**：
```json
{
  "id": 1,
  "status": "completed",
  ...
}
```

**注意**：如果任务有未完成的子任务，会返回错误：
```json
{
  "detail": "请先完成所有子任务"
}
```

#### 拆解任务

```
POST /api/tasks/{task_id}/split
```

**请求体**：
```json
{
  "subtasks": ["子任务1", "子任务2", "子任务3"]
}
```

**响应示例**：
```json
[
  {
    "id": 2,
    "title": "子任务1",
    "category": "work",
    "status": "pending",
    "parent_id": 1
  },
  {
    "id": 3,
    "title": "子任务2",
    "category": "work",
    "status": "pending",
    "parent_id": 1
  }
]
```

#### 删除任务

```
DELETE /api/tasks/{task_id}
```

**响应示例**：
```json
{
  "message": "任务删除成功"
}
```

**注意**：会级联删除所有子任务

### 分类模式管理

#### 设置分类模式

```
POST /api/mode
```

**请求体**：
```json
{
  "mode": "manual",
  "category": "work"
}
```

**字段说明**：
- `mode`: 模式（auto/manual）
- `category`: 手动模式下指定的分类（必填）

**响应示例**：
```json
{
  "message": "模式已设置为: manual"
}
```

#### 获取当前模式

```
GET /api/mode
```

**响应示例**：
```json
{
  "mode": "auto",
  "category": "work",
  "ip": "192.168.1.100",
  "location": {
    "country": "China",
    "region": "Shanghai",
    "city": "Shanghai",
    "lat": 31.2304,
    "lon": 121.4737,
    "isp": "China Telecom"
  }
}
```

### IP映射管理

#### 获取所有IP映射

```
GET /api/ip-mappings
```

**响应示例**：
```json
[
  {
    "id": 1,
    "ip_pattern": "192.168.1.100",
    "category": "work",
    "auto": true,
    "manual_override": false,
    "created_at": "2026-03-01T12:00:00",
    "updated_at": "2026-03-01T12:00:00"
  }
]
```

#### 删除IP映射

```
DELETE /api/ip-mappings/{mapping_id}
```

**响应示例**：
```json
{
  "message": "IP映射删除成功"
}
```

### 统计信息

#### 获取统计信息

```
GET /api/stats
```

**响应示例**：
```json
{
  "total": 10,
  "completed": 5,
  "pending": 3,
  "in_progress": 2,
  "by_category": {
    "work": {
      "total": 6,
      "completed": 3
    },
    "life": {
      "total": 3,
      "completed": 2
    },
    "education": {
      "total": 1,
      "completed": 0
    }
  }
}
```

### 系统信息

#### 根路径

```
GET /
```

**响应示例**：
```json
{
  "name": "Todo System",
  "version": "1.0.0",
  "message": "欢迎使用个人任务管理系统"
}
```

#### 健康检查

```
GET /health
```

**响应示例**：
```json
{
  "status": "healthy"
}
```

## 错误响应

所有错误响应格式：

```json
{
  "detail": "错误信息"
}
```

### HTTP状态码

- `200`: 成功
- `400`: 请求错误
- `404`: 资源不存在
- `500`: 服务器错误

## 交互式文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
