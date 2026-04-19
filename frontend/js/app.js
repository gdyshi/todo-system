// API配置 - 使用绝对 URL，避免跨端口访问问题
// 开发环境使用 localhost，生产环境使用 Render 后端地址
// 支持 URL 参数覆盖：?api=http://xxx/api
const urlParams = new URLSearchParams(window.location.search);
const apiOverride = urlParams.get('api');
const API_BASE_URL = apiOverride 
    || (window.location.hostname === 'localhost' 
        ? 'https://todo-system-msvx.onrender.com/api'  // 本地开发也使用远程后端
        : 'https://todo-system-msvx.onrender.com/api');

// 应用状态
let currentFilter = 'all';
let currentStatuses = ['in_progress', 'pending']; // 默认不显示已完成
let showCompleted = false; // 已完成任务的显示状态
let tasks = [];

// 通用重试函数 - 应对 Render 免费版冷启动超时
async function fetchWithRetry(url, options = {}, retries = 2, delay = 3000) {
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response;
        } catch (error) {
            if (attempt === retries) {
                throw error;
            }
            console.warn(`请求失败，${delay / 1000}秒后重试 (${attempt + 1}/${retries})...`, url);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadStats();
    loadModeInfo();
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

    // 已完成任务的显示/隐藏按钮
    const completedCheckbox = document.getElementById('completed-filter');
    const toggleBtn = document.getElementById('toggle-completed');
    
    // 默认隐藏已完成任务
    completedCheckbox.checked = false;
    toggleBtn.style.display = 'inline-block';
    toggleBtn.textContent = '显示已完成';
    
    toggleBtn.addEventListener('click', () => {
        showCompleted = !showCompleted;
        completedCheckbox.checked = showCompleted;
        
        if (showCompleted) {
            currentStatuses = ['in_progress', 'pending', 'completed'];
            toggleBtn.textContent = '隐藏已完成';
        } else {
            currentStatuses = ['in_progress', 'pending'];
            toggleBtn.textContent = '显示已完成';
        }
        
        renderTasks();
    });
}

// 加载任务列表
async function loadTasks() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/tasks?category=${currentFilter === 'all' ? '' : currentFilter}`);
        tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('加载任务失败:', error);
        showError('后端服务正在启动中，请稍候刷新页面');
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

    // 按状态排序：进行中 → 待处理 → 已完成
    const statusOrder = {
        'in_progress': 0,
        'pending': 1,
        'completed': 2
    };
    
    filteredTasks.sort((a, b) => {
        // 先按状态排序
        const statusDiff = statusOrder[a.status] - statusOrder[b.status];
        if (statusDiff !== 0) return statusDiff;
        
        // 同状态按优先级排序（高优先级在前）
        return b.priority - a.priority;
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

    container.querySelectorAll('.btn-complete-subtask').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const taskId = parseInt(e.target.dataset.taskId);
            completeTask(taskId);
        });
    });

    // 更新状态栏中的简要统计
    updateStatusBar();
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
                <div class="subtask-item ${st.status === 'completed' ? 'completed' : ''}">
                    <span class="task-badge ${st.category}">${categoryLabels[st.category]}</span>
                    ${st.title}
                    ${st.status === 'completed' 
                        ? '<span class="subtask-status completed">✓ 已完成</span>'
                        : `<button class="btn btn-sm btn-success btn-complete-subtask" data-task-id="${st.id}">✓ 完成</button>`}
                </div>
            `).join('')}
           </div>`
        : '';

    return `
        <div class="task-item ${task.status === 'completed' ? 'completed' : ''}" data-task-id="${task.id}">
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

    const input = document.getElementById('task-input').value.trim();

    if (!input) {
        showError('请输入任务描述');
        return;
    }

    const taskData = {
        title: input,
        priority: 0,
    };

    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '服务器返回未知错误' }));
            throw new Error(errorData.detail || '添加任务失败');
        }

        // 清空输入框
        document.getElementById('task-input').value = '';

        // 重新加载任务
        await loadTasks();
        await loadStats();

        showSuccess('任务添加成功！AI 正在生成子任务...');
    } catch (error) {
        console.error('添加任务失败:', error);
        showError('添加任务失败: ' + (error.message || '未知错误'));
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
        const response = await fetchWithRetry(`${API_BASE_URL}/stats`);
        const stats = await response.json();
        updateStatusBar(stats);
    } catch (error) {
        console.error('加载统计失败:', error);
    }
}

// 更新状态栏
function updateStatusBar(stats) {
    const statsBrief = document.getElementById('stats-brief');
    
    if (stats) {
        const inProgress = stats.in_progress || 0;
        const pending = stats.pending || 0;
        const completed = stats.completed || 0;
        const total = stats.total || 0;
        
        statsBrief.textContent = `📊 总计: ${total} | 进行中: ${inProgress} | 待处理: ${pending} | 已完成: ${completed}`;
    } else {
        statsBrief.textContent = '加载中...';
    }
}

// 加载模式信息
async function loadModeInfo() {
    try {
        const response = await fetchWithRetry(`${API_BASE_URL}/mode`);
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
