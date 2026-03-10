from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.models import init_db
from app.api import tasks, demo
from app.orchestrator.context_manager import ContextManager
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局上下文管理器（应用级别）
_global_context_manager: ContextManager = None
_global_scheduler = None

def get_context_manager() -> ContextManager:
    """获取全局上下文管理器"""
    global _global_context_manager
    if _global_context_manager is None:
        # 创建一个临时的 executor 用于初始化
        from app.executor.task_executor import TaskExecutor
        from app.models import get_db

        db = next(get_db())
        executor = TaskExecutor(db)
        _global_context_manager = ContextManager(executor)
    return _global_context_manager


def get_scheduler():
    """获取全局调度器（确保单例）"""
    global _global_scheduler
    from app.orchestrator.reminder_scheduler import ReminderScheduler
    from app.models import get_db
    from app.executor.task_executor import TaskExecutor

    if _global_scheduler is None:
        db = next(get_db())
        executor = TaskExecutor(db)
        _global_scheduler = ReminderScheduler(executor, auto_start=False)
        _global_scheduler.scheduler.start()
    return _global_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("正在初始化数据库...")
    init_db()
    logger.info("数据库初始化完成")

    # 启动全局调度器
    logger.info("启动调度器...")
    scheduler = get_scheduler()
    if scheduler:
        await scheduler.start()
        logger.info("调度器启动完成")
    else:
        logger.warning("调度器未创建，可能是在测试环境")

    logger.info(f"{settings.app_name} v{settings.version} 启动成功！")

    yield

    # 关闭时
    logger.info("应用关闭中...")
    if _global_scheduler:
        _global_scheduler.shutdown()
        logger.info("调度器已关闭")
    logger.info("应用已关闭")


# 创建应用
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "message": "欢迎使用个人任务管理系统",
    }


# 健康检查
@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
