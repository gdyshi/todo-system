import httpx
# import smtplib  # 邮件功能已移除
# from email.mime.text import MIMEText  # 邮件功能已移除
from app.config import settings
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class ExternalServices:
    """外部服务调用类"""

    async def query_location(self, ip: str) -> Dict[str, Any]:
        """
        查询IP地理位置

        使用免费的IP地理位置查询API
        """
        try:
            # 使用ip-api.com的免费API
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://ip-api.com/json/{ip}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        return {
                            "country": data.get("country"),
                            "region": data.get("regionName"),
                            "city": data.get("city"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon"),
                            "isp": data.get("isp")
                        }
        except Exception as e:
            logger.error(f"查询IP地理位置失败: {e}")

        # 如果查询失败，返回默认值
        return {
            "country": "Unknown",
            "region": "Unknown",
            "city": "Unknown",
            "lat": 0,
            "lon": 0,
            "isp": "Unknown"
        }

    async def send_telegram_message(self, message: str) -> bool:
        """
        发送Telegram消息

        需要配置：
        - TELEGRAM_BOT_TOKEN
        - TELEGRAM_CHAT_ID
        """
        if not settings.telegram_bot_token or not settings.telegram_chat_id:
            logger.warning("Telegram配置未设置，跳过发送")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                    json={
                        "chat_id": settings.telegram_chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
                if response.status_code == 200:
                    logger.info(f"Telegram消息发送成功: {message[:50]}...")
                    return True
                else:
                    logger.error(f"Telegram消息发送失败: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"发送Telegram消息异常: {e}")
            return False

    # 邮件功能已移除
    # 如需添加邮件提醒，请在此实现
    # async def send_email(self, subject: str, message: str) -> bool:
    #     """发送邮件提醒"""
    #     pass

    async def trigger_render_deploy(self) -> bool:
        """
        触发Render部署

        需要配置：
        - RENDER_DEPLOY_HOOK
        """
        if not settings.render_deploy_hook:
            logger.warning("Render部署Webhook未配置，跳过")
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(settings.render_deploy_hook)
                if response.status_code == 200:
                    logger.info("Render部署触发成功")
                    return True
                else:
                    logger.error(f"Render部署触发失败: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"触发Render部署异常: {e}")
            return False


external_services = ExternalServices()
