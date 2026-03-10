# core/mailer.py
"""
이메일 발송 모듈 (Resend API)
- 수신자: RECIPIENT_EMAIL 환경변수 (쉼표 구분 복수 지원)
- HTML 이메일: Markdown → 기본 HTML 변환
- 발송 실패 시 로그만 남기고 전체 프로세스 계속
"""

import logging
import os
from datetime import datetime
import markdown

import requests

from config.settings import EMAIL_FROM, EMAIL_SUBJECT, EMAIL_TO, RESEND_API_KEY

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def _md_to_html(md: str) -> str:
    body = markdown.markdown(
        md,
        extensions=["tables", "fenced_code"]
    )
    return f"""
<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px">
{body}
<br><hr>
<small style="color:#888">AI News Daily — {datetime.now().strftime('%Y-%m-%d')}</small>
</body></html>
"""

def send_email(md_content: str) -> bool:
    """
    이메일 발송.
    반환: True(성공) / False(실패)
    """
    if not RESEND_API_KEY:
        logger.warning("[이메일] RESEND_API_KEY 미설정 — 발송 건너뜀")
        return False

    if not EMAIL_TO:
        logger.warning("[이메일] RECIPIENT_EMAIL 미설정 — 발송 건너뜀")
        return False

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject  = EMAIL_SUBJECT.format(date=date_str)
    html     = _md_to_html(md_content)

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json={
                "from":    EMAIL_FROM,
                "to":      EMAIL_TO,
                "subject": subject,
                "html":    html,
            },
            timeout=15,
            verify=False,
        )
        if resp.status_code in (200, 201):
            logger.info(f"[이메일 발송] 성공 → {EMAIL_TO}")
            return True
        else:
            logger.error(f"[이메일 발송 실패] {resp.status_code}: {resp.text}")
            return False

    except Exception as e:
        logger.error(f"[이메일 발송 오류] {e}")
        return False
