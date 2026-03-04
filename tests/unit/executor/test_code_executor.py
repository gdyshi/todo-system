"""CodeExecutor 单元测试（使用 mock）"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.executor.code_executor import CodeExecutor


@pytest.mark.asyncio
async def test_code_executor_init(mock_api_key):
    """测试：CodeExecutor 初始化"""
    executor = CodeExecutor(api_key=mock_api_key, model="glm-4.7")
    
    assert executor.api_key == mock_api_key
    assert executor.model == "glm-4.7"


@pytest.mark.asyncio
async def test_build_prompt_with_context(mock_api_key):
    """测试：构建 prompt（带上下文）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    task_prompt = "写一个函数"
    context = "额外的上下文信息"
    
    full_prompt = executor._build_prompt(task_prompt, context)
    
    assert "你是一个专业的代码助手" in full_prompt
    assert task_prompt in full_prompt
    assert context in full_prompt


@pytest.mark.asyncio
async def test_build_prompt_without_context(mock_api_key):
    """测试：构建 prompt（无上下文）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    task_prompt = "写一个函数"
    full_prompt = executor._build_prompt(task_prompt, None)
    
    assert task_prompt in full_prompt
    assert "额外的上下文信息" not in full_prompt


@pytest.mark.asyncio
async def test_extract_code_from_text_python_block(mock_api_key):
    """测试：从文本中提取代码（Python 块）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    text = """
说明如下：

```python
def hello():
    return "Hello, World!"
```
"""
    
    code = executor._extract_code_from_text(text)
    
    assert code is not None
    assert "def hello():" in code
    assert 'return "Hello, World!"' in code


@pytest.mark.asyncio
async def test_extract_code_from_text_no_block(mock_api_key):
    """测试：从文本中提取代码（无代码块）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    text = "这是一段代码：def hello(): return 'hi'"
    
    code = executor._extract_code_from_text(text)
    
    # 没有代码块标记，应该返回 None
    assert code is None


@pytest.mark.asyncio
async def test_extract_explanation_from_text(mock_api_key):
    """测试：从文本中提取说明"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    text = """
这是代码说明：函数会打印 Hello

```python
print("Hello")
```
更多说明...
"""
    
    explanation = executor._extract_explanation_from_text(text)
    
    # 应该移除代码块后的内容
    assert "这是代码说明：函数会打印 Hello" in explanation
    assert "```python" not in explanation


@pytest.mark.asyncio
async def test_parse_output_success(mock_api_key, mock_claude_response_json):
    """测试：解析成功输出"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    result = executor._parse_output(mock_claude_response_json)
    
    assert result["success"] == True
    assert result["code"] == "生成的代码"
    assert result["explanation"] is not None


@pytest.mark.asyncio
async def test_parse_output_text(mock_api_key):
    """测试：解析纯文本输出"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    text_output = {
        "type": "result",
        "result": "```python\ndef test():\n    pass\n```"
    }
    
    result = executor._parse_output(text_output)
    
    assert result["success"] == True
    assert "def test():" in result["code"]


@pytest.mark.asyncio
async def test_execute_code_task_mock_success(mock_api_key, mock_claude_response_json):
    """测试：执行代码任务（mock 成功）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (
        mock_claude_response_json["result"].encode(),
        b""
    )
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        with patch('asyncio.wait_for', return_value=(mock_process.communicate.return_value, None)):
            result = await executor.execute_code_task("写一个函数")
    
    assert result["success"] == True
    assert result["code"] is not None


@pytest.mark.asyncio
async def test_execute_code_task_mock_failure(mock_api_key):
    """测试：执行代码任务（mock 失败）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"", b"API Error: Failed")
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process):
        with patch('asyncio.wait_for', return_value=(mock_process.communicate.return_value, None)):
            result = await executor.execute_code_task("Write a function")
    
    assert result["success"] == False
    assert result["error"] is not None
    assert "Error" in result["error"]


@pytest.mark.asyncio
async def test_execute_sql_query_mock(mock_api_key):
    """测试：执行 SQL 查询（mock）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    with patch.object(executor, 'execute_code_task', return_value={"success": True, "code": "SQL代码"}):
        result = await executor.execute_sql_query("查询任务", "查询描述")
    
    assert result["success"] == True
    assert result["sql"] == "SQL代码"
    assert result["type"] == "sql"


@pytest.mark.asyncio
async def test_generate_api_endpoint_mock(mock_api_key):
    """测试：生成 API 端点（mock）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    input_schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    output_schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
    
    with patch.object(executor, 'execute_code_task', return_value={"success": True, "code": "API代码"}):
        result = await executor.generate_api_endpoint("创建任务", "POST", input_schema, output_schema)
    
    assert result["success"] == True
    assert result["code"] == "API代码"


@pytest.mark.asyncio
async def test_execute_code_task_timeout(mock_api_key):
    """测试：执行代码任务超时"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        mock_process = AsyncMock()
        mock_exec.return_value = mock_process
        
        # 模拟超时
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError):
            result = await executor.execute_code_task("写一个函数")
        
        assert result["success"] == False
        assert "超时" in result["error"]


@pytest.mark.asyncio
async def test_test_connection_mock(mock_api_key):
    """测试：连接测试（mock）"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    with patch.object(executor, 'execute_code_task', return_value={"success": True}):
        result = await executor.test_connection()
    
    assert result["success"] == True
    assert result["message"] == "连接成功"


@pytest.mark.asyncio
async def test_execute_code_task_with_environment(mock_api_key):
    """测试：执行代码任务时设置环境变量"""
    executor = CodeExecutor(api_key=mock_api_key)
    
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"code", b"")
    
    captured_env = {}
    
    def capture_env(**kwargs):
        captured_env.update(kwargs)
        return mock_process
    
    with patch('asyncio.create_subprocess_exec', new=capture_env):
        with patch('asyncio.wait_for', return_value=(mock_process.communicate.return_value, None)):
            result = await executor.execute_code_task("写一个函数")
    
    # 验证环境变量设置
    assert "ANTHROPIC_API_KEY" in captured_env
    assert captured_env["ANTHROPIC_API_KEY"] == mock_api_key
