from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.models import init_db
from app.api import tasks, demo
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")
    logger.info(f"{settings.app_name} v{settings.version} 启动成功！")


# 注册路由
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(demo.router, prefix="/api", tags=["demo"])


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "message": "欢迎使用个人任务管理系统"
    }


# 健康检查
@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
