# core/shared/alert.py
"""
파이프라인 품질 게이트 실패 시 공통 알림 — 텔레그램 + 관리자 이메일.

news/stock/ai-issue 3채널이 각자 SMTP·텔레그램 발송을 따로 구현하던 것을
하나로 통합. 한쪽 채널이 끊겨도 다른 쪽은 best-effort로 계속 시도한다.
"""
from __future__ import annotations

import logging
import os

import requests

from core.shared.mailer import send_admin_alert

logger = logging.getLogger(__name__)

_CHANNEL_LABEL = {"news": "뉴스", "stock": "주식 시황", "ai-issue": "AI이슈"}


def send_pipeline_alert(channel: str, date_str: str, reason: str) -> None:
    """채널 품질 게이트 실패 시 텔레그램 + 관리자 이메일로 알림.

    channel: 'news' | 'stock' | 'ai-issue'
    """
    label = _CHANNEL_LABEL.get(channel, channel)
    subject = f"[DailyNews] ⚠ {date_str} {label} 분석 실패"
    body = (
        f"날짜: {date_str}\n"
        f"사유: {reason}\n\n"
        f"AI 분석이 비어있어 저장/발송을 건너뛰었습니다.\n"
        f"GitHub Actions에서 수동 재실행하거나 LLM 상태를 확인하세요."
    )

    _send_telegram(subject, body)

    if not send_admin_alert(subject, body, level="warning"):
        logger.warning(f"[{channel}] 관리자 이메일 알림 미발송 (GMAIL 미설정 또는 발송 실패)")


def _send_telegram(subject: str, body: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        logger.warning("[알림] TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID 미설정 — 텔레그램 알림 발송 불가")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": f"{subject}\n\n{body}"},
            timeout=10,
        )
        logger.info("[알림] 텔레그램 발송 완료")
    except Exception as e:
        logger.error(f"[알림] 텔레그램 발송 실패: {e}")
