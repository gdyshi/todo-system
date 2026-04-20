from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # 应用信息
    app_name: str = "Todo System"
    version: str = "2.0.0"
    debug: bool = True

    # 数据库
    database_path: str = "database/todo.db"
    database_url: str = "sqlite:///./database/todo.db"

    # Telegram配置（用于提醒）
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Render配置（用于后端部署）
    render_deploy_hook: Optional[str] = None

    # GitHub配置（用于自动审查和通知）
    github_username: Optional[str] = None
    github_repo: Optional[str] = None
    github_token: Optional[str] = None

    # AI 模型 API 配置（环境变量：MODEL_URL, MODEL_NAME, MODEL_KEY）
    model_url: str = "https://open.ospreyai.cn/v1/chat/completions"
    model_name: str = "minimax-m2.5-highspeed"
    model_key: Optional[str] = None

    # 日志配置
    log_level: str = "INFO"


settings = Settings()
