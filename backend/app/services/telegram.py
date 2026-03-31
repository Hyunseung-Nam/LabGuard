"""
Telegram 알림 서비스.
AlertEvent 생성 시 호출되어 텔레그램 메시지를 발송합니다.
"""

import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def send_alert(message: str) -> None:
    """
    목적: Telegram 봇으로 알림 메시지를 발송합니다.
    Args:
        message: 전송할 텍스트 메시지.
    Returns: 없음.
    Side Effects: Telegram API HTTP 요청 발생.
    Raises: 없음 (오류는 로그로만 처리, 알림 실패가 측정값 저장을 막으면 안 됨).
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.debug("Telegram 미설정 — 알림 스킵")
        return

    url = TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            logger.info("Telegram 알림 발송 완료")
    except Exception as e:
        logger.error("Telegram 알림 발송 실패: %s", e)
