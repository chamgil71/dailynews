# core/mailer.py
"""
이메일 발송 모듈 (Resend Batch API)
- 수신자: RECIPIENT_EMAILS 환경변수 (쉼표 구분)
- 개별 발송: 수신자끼리 서로 이메일 주소 안 보임
- 구독 취소: 메일 하단 HMAC 토큰 링크 → Vercel API 처리
"""

import hashlib
import hmac
import logging
import os
from datetime import datetime
from pathlib import Path

import markdown2
import requests

from config.settings import (
    EMAIL_FROM,
    EMAIL_SUBJECT,
    GH_CONTENTS_TOKEN,
    GITHUB_REPOSITORY,
    RECIPIENT_EMAILS,
    RESEND_API_KEY,
    SITE_BASE_URL,
    UNSUBSCRIBE_SECRET,
)

logger = logging.getLogger(__name__)

_UNSUB_FILE = Path(__file__).parent.parent / "storage" / "unsubscribed.txt"


def _get_unsubscribed() -> set[str]:
    if not _UNSUB_FILE.exists():
        return set()
    return {line.strip().lower() for line in _UNSUB_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}


def _get_recipients() -> list[str]:
    unsubscribed = _get_unsubscribed()
    return [e for e in RECIPIENT_EMAILS if e.lower() not in unsubscribed]


def _make_token(email: str) -> str:
    key = (UNSUBSCRIBE_SECRET or "fallback-secret").encode()
    return hmac.new(key, email.lower().encode(), hashlib.sha256).hexdigest()[:16]


def _md_to_html(md: str, recipient_email: str) -> str:
    body = markdown2.markdown(md, extras=["tables", "fenced-code-blocks"])

    if SITE_BASE_URL:
        token = _make_token(recipient_email)
        import urllib.parse
        encoded = urllib.parse.quote(recipient_email)
        unsubscribe_url = f"{SITE_BASE_URL}/api/unsubscribe?email={encoded}&token={token}"
        unsub_link = f'<a href="{unsubscribe_url}" style="color:#aaa">구독 취소</a>'
    else:
        unsub_link = ""

    return f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:20px">
{body}
<br><hr>
<small style="color:#888">
  AI News Daily — {datetime.now().strftime('%Y-%m-%d')}
  {f"&nbsp;|&nbsp;{unsub_link}" if unsub_link else ""}
</small>
</body></html>"""


def send_email(md_content: str) -> bool:
    if not RESEND_API_KEY:
        logger.warning("[이메일] RESEND_API_KEY 미설정 — 발송 건너뜀")
        return False

    recipients = _get_recipients()
    if not recipients:
        logger.warning("[이메일] 발송 대상 없음 (RECIPIENT_EMAILS 미설정 또는 전원 구독 취소)")
        return False

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject  = EMAIL_SUBJECT.format(date=date_str)

    batch_payload = [
        {
            "from":    EMAIL_FROM,
            "to":      [email],
            "subject": subject,
            "html":    _md_to_html(md_content, email),
        }
        for email in recipients
    ]

    try:
        resp = requests.post(
            "https://api.resend.com/emails/batch",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type":  "application/json",
            },
            json=batch_payload,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            logger.info(f"[이메일 발송] 성공 → {len(recipients)}명")
            return True
        else:
            logger.error(f"[이메일 발송 실패] {resp.status_code}: {resp.text}")
            return False

    except Exception as e:
        logger.error(f"[이메일 발송 오류] {e}")
        return False
