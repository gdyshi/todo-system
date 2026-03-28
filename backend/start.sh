#!/bin/bash
# 快速启动脚本

echo "🚀 启动个人任务管理系统..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python 3.11+"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -q -r requirements.txt

# 初始化数据库
echo "🗄️  初始化数据库..."
python3 init_db.py

# 创建数据库目录
mkdir -p database

# 启动服务器
echo "✨ 启动服务器..."
echo ""
echo "📖 访问地址："
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 前端界面: 打开 ../frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
