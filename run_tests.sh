#!/bin/bash
# 测试运行脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
cd "$(dirname "$0")/.."

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Todo System 测试套件${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}检查测试依赖...${NC}"
pip3 show pytest &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}pytest 未安装${NC}"
    exit 1
fi

pip3 show pytest-asyncio &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}pytest-asyncio 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 测试依赖已安装${NC}"
echo ""

# 创建测试数据库
echo -e "${YELLOW}准备测试数据库...${NC}"
mkdir -p database
if [ -f "database/test_todo.db" ]; then
    rm "database/test_todo.db"
    echo -e "${GREEN}✓ 已清理旧测试数据库${NC}"
else
    echo -e "${GREEN}✓ 测试数据库已准备${NC}"
fi
echo ""

# 运行测试
echo -e "${YELLOW}运行测试...${NC}"
echo ""

# 检查参数
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    unit)
        echo -e "${GREEN}运行单元测试...${NC}"
        pytest tests/unit/ -v --cov=app --cov-report=term-missing
        ;;
    
    api)
        echo -e "${GREEN}运行 API 测试...${NC}"
        pytest tests/api/ -v
        ;;
    
    integration)
        echo -e "${GREEN}运行集成测试...${NC}"
        pytest tests/integration/ -v
        ;;
    
    e2e)
        echo -e "${GREEN}运行 E2E 测试（浏览器）...${NC}"
        if ! command -v playwright &> /dev/null; then
            echo -e "${RED}Playwright 未安装，跳过 E2E 测试${NC}"
            exit 0
        fi
        pytest tests/e2e/ -v --browser chromium --headed
        ;;
    
    all|*)
        echo -e "${GREEN}运行所有测试...${NC}"
        
        # 单元测试
        echo ""
        echo -e "${YELLOW}1. 单元测试${NC}"
        pytest tests/unit/ -v --cov=app --cov-report=term-missing || true
        
        # API 测试
        echo ""
        echo -e "${YELLOW}2. API 测试${NC}"
        pytest tests/api/ -v || true
        
        # 集成测试
        echo ""
        echo -e "${YELLOW}3. 集成测试${NC}"
        pytest tests/integration/ -v || true
        
        # E2E 测试
        echo ""
        echo -e "${YELLOW}4. E2E 测试${NC}"
        if command -v playwright &> /dev/null; then
            pytest tests/e2e/ -v --browser chromium --headed || true
        else
            echo -e "${YELLOW}Playwright 未安装，跳过 E2E 测试${NC}"
        fi
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}测试完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 清理测试数据库（可选）
read -p "是否清理测试数据库？[y/N] " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f database/test_todo.db
    echo -e "${GREEN}✓ 测试数据库已清理${NC}"
fi
