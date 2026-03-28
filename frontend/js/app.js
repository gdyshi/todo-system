// API配置 - 使用绝对 URL，避免跨端口访问问题
const API_BASE_URL = 'http://localhost:8000/api';

// 应用状态
let currentFilter = 'all';
let currentStatuses = ['pending', 'in_progress', 'completed'];
let tasks = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadStats();
    loadModeInfo();
    loadIPMappings();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 添加任务表单
    document.getElementById('add-task-form').addEventListener('submit', handleAddTask);

    // 筛选按钮
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            renderTasks();
        });
    });

    // 状态筛选
    document.querySelectorAll('.status-filter').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            currentStatuses = Array.from(document.querySelectorAll('.status-filter:checked')).map(cb => cb.value);
            renderTasks();
        });
    });
}

// 加载任务列表
async function loadTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks?category=${currentFilter === 'all' ? '' : currentFilter}`);
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('加载任务失败:', error);
        showError('加载任务失败');
    }
}

// 渲染任务列表
function renderTasks() {
    const container = document.getElementById('tasks-container');

    // 筛选任务
    const filteredTasks = tasks.filter(task => {
        const statusMatch = currentStatuses.includes(task.status);
        const categoryMatch = currentFilter === 'all' || task.category === currentFilter;
        return statusMatch && categoryMatch;
    });

    // 更新计数
    document.getElementById('task-count').textContent = `(${filteredTasks.length})`;

    if (filteredTasks.length === 0) {
        container.innerHTML = '<p class="loading">暂无任务</p>';
        return;
    }

    container.innerHTML = filteredTasks.map(task => createTaskHTML(task)).join('');

    // 绑定事件
    container.querySelectorAll('.btn-complete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            completeTask(taskId);
        });
    });

    container.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            deleteTask(taskId);
        });
    });

    container.querySelectorAll('.btn-split').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            promptSplitTask(taskId);
        });
    });
}

// 创建任务HTML
function createTaskHTML(task) {
    const categoryLabels = {
        work: '工作',
        life: '生活',
        education: '教育'
    };

    const statusLabels = {
        pending: '待处理',
        in_progress: '进行中',
        completed: '已完成'
    };

    const subtasksHTML = task.subtasks && task.subtasks.length > 0
        ? `<div class="subtasks">
            ${task.subtasks.map(st => `
                <div class="subtask-item">
                    <span class="task-badge ${st.category}">${categoryLabels[st.category]}</span>
                    ${st.title}
                    ${st.status === 'completed' ? '✓' : ''}
                </div>
            `).join('')}
           </div>`
        : '';

    return `
        <div class="task-item" data-task-id="${task.id}">
            <div class="task-header">
                <h3 class="task-title">${task.title}</h3>
                <div class="task-meta">
                    <span class="task-badge ${task.category}">${categoryLabels[task.category]}</span>
                    <span class="task-badge ${task.status}">${statusLabels[task.status]}</span>
                    <span class="task-badge">优先级: ${task.priority}</span>
                </div>
            </div>

            ${task.description ? `<p class="task-description">${task.description}</p>` : ''}

            ${task.due_time ? `<p class="task-description">⏰ 截止时间: ${formatDateTime(task.due_time)}</p>` : ''}

            ${subtasksHTML}

            <div class="task-actions">
                ${task.status !== 'completed' ? `
                    <button class="btn btn-success btn-complete" data-task-id="${task.id}">
                        ✓ 完成
                    </button>
                    <button class="btn btn-split" data-task-id="${task.id}">
                        ⚡ 拆解任务
                    </button>
                ` : ''}
                <button class="btn btn-danger btn-delete" data-task-id="${task.id}">
                    🗑️ 删除
                </button>
            </div>
        </div>
    `;
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 添加任务
async function handleAddTask(e) {
    e.preventDefault();

    const title = document.getElementById('task-title').value.trim();
    const description = document.getElementById('task-description').value.trim();
    const categorySelect = document.getElementById('task-category').value;
    const priority = parseInt(document.getElementById('task-priority').value);
    const dueTime = document.getElementById('task-due-time').value;
    const location = document.getElementById('task-location').value.trim();
    const subtasksText = document.getElementById('task-subtasks').value.trim();

    if (!title) {
        showError('请输入任务标题');
        return;
    }

    const taskData = {
        title,
        description,
        priority,
    };

    if (categorySelect !== 'auto') {
        taskData.category = categorySelect;
    }

    if (dueTime) {
        taskData.due_time = new Date(dueTime).toISOString();
    }

    if (location) {
        taskData.location = location;
    }

    if (subtasksText) {
        taskData.subtasks = subtasksText.split('\n').filter(st => st.trim());
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '服务器返回未知错误' }));
            throw new Error(errorData.detail || '添加任务失败');
        }

        // 清空表单
        document.getElementById('add-task-form').reset();

        // 重新加载任务
        await loadTasks();
        await loadStats();

        showSuccess('任务添加成功！');
    } catch (error) {
        console.error('添加任务失败:', error);
        showError('添加任务失败');
    }
}

// 完成任务
async function completeTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/complete`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '完成任务失败');
        }

        await loadTasks();
        await loadStats();
        showSuccess('任务已完成！');
    } catch (error) {
        console.error('完成任务失败:', error);
        showError(error.message || '完成任务失败');
    }
}

// 删除任务
async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '服务器返回未知错误' }));
            throw new Error(errorData.detail || '删除任务失败');
        }

        await loadTasks();
        await loadStats();
        showSuccess('任务已删除！');
    } catch (error) {
        console.error('删除任务失败:', error);
        showError('删除任务失败');
    }
}

// 拆解任务
async function promptSplitTask(taskId) {
    const subtasksInput = prompt('请输入子任务，每行一个：');
    if (!subtasksInput) {
        return;
    }

    const subtasks = subtasksInput.split('\n').filter(st => st.trim());
    if (subtasks.length === 0) {
        showError('请至少输入一个子任务');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/split`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subtasks })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '服务器返回未知错误' }));
            throw new Error(errorData.detail || '拆解任务失败');
        }

        await loadTasks();
        showSuccess('任务拆解成功！');
    } catch (error) {
        console.error('拆解任务失败:', error);
        showError('拆解任务失败');
    }
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        renderStats(stats);
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

// 渲染统计信息
function renderStats(stats) {
    const container = document.getElementById('stats-container');

    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">${stats.total}</div>
                <div class="stat-label">总任务</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.completed}</div>
                <div class="stat-label">已完成</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.pending}</div>
                <div class="stat-label">待处理</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.in_progress}</div>
                <div class="stat-label">进行中</div>
            </div>
        </div>
    `;
}

// 加载模式信息
async function loadModeInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/mode`);
        const modeInfo = await response.json();

        const container = document.getElementById('mode-info');
        const categoryLabels = {
            work: '工作',
            life: '生活',
            education: '教育',
            auto: '自动检测'
        };

        container.innerHTML = `
            <span>模式: ${modeInfo.mode === 'auto' ? '自动' : '手动'}</span>
            <span> | </span>
            <span>分类: ${modeInfo.category ? categoryLabels[modeInfo.category] || modeInfo.category : '未检测'}</span>
            <span> | </span>
            <span>IP: ${modeInfo.ip}</span>
            ${modeInfo.location && modeInfo.location.city ? `<span> | </span><span>📍 ${modeInfo.location.city}</span>` : ''}
        `;
    } catch (error) {
        console.error('加载模式信息失败:', error);
    }
}

// 加载IP映射
async function loadIPMappings() {
    try {
        const response = await fetch(`${API_BASE_URL}/ip-mappings`);
        const mappings = await response.json();
        renderIPMappings(mappings);
    } catch (error) {
        console.error('加载IP映射失败:', error);
    }
}

// 渲染IP映射
function renderIPMappings(mappings) {
    const container = document.getElementById('ip-mappings-container');

    if (mappings.length === 0) {
        container.innerHTML = '<p class="loading">暂无IP映射规则（系统会自动学习）</p>';
        return;
    }

    const categoryLabels = {
        work: '工作',
        life: '生活',
        education: '教育'
    };

    container.innerHTML = mappings.map(mapping => `
        <div class="ip-mapping-item">
            <div>
                <strong>${mapping.ip_pattern}</strong>
                <span class="task-badge ${mapping.category}">${categoryLabels[mapping.category]}</span>
                <small>${mapping.auto ? '自动生成' : '手动设置'}</small>
            </div>
            ${!mapping.auto ? `<button class="btn btn-danger" onclick="deleteIPMapping(${mapping.id})">删除</button>` : ''}
        </div>
    `).join('');
}

// 删除IP映射
async function deleteIPMapping(mappingId) {
    if (!confirm('确定要删除这个IP映射吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/ip-mappings/${mappingId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '服务器返回未知错误' }));
            throw new Error(errorData.detail || '删除IP映射失败');
        }

        await loadIPMappings();
        showSuccess('IP映射已删除！');
    } catch (error) {
        console.error('删除IP映射失败:', error);
        showError('删除IP映射失败');
    }
}

// 显示成功消息
function showSuccess(message) {
    showToast(message, 'success');
}

// 显示错误消息
function showError(message) {
    showToast(message, 'error');
}

// 显示Toast消息
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 添加动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
