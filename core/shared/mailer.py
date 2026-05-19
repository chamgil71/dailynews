# core/mailer.py
"""
이메일 발송 모듈 (Gmail SMTP)
- 수신자: RECIPIENT_EMAILS 환경변수 (쉼표 구분)
- 개별 발송: 수신자끼리 서로 이메일 주소 안 보임
- 구독 취소: 메일 하단 HMAC 토큰 링크 → Vercel API 처리
- 템플릿: storage/email_template.html (Jinja2) → 테마 토큰 반영
"""

import hashlib
import hmac
import importlib
import logging
import os
import re
import smtplib
import urllib.parse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import markdown2

from config.settings import (
    EMAIL_SUBJECT,
    GMAIL_APP_PASSWORD,
    GMAIL_USER,
    RECIPIENT_EMAILS,
    SITE_BASE_URL,
    UNSUBSCRIBE_SECRET,
)

_TEMPLATE_FILE = Path(__file__).parent.parent.parent / "storage" / "email_template.html"


def _get_email_theme() -> str:
    try:
        from config.theme_config import SECTION_THEMES
        return SECTION_THEMES.get("email", "classic")
    except Exception:
        return "classic"

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


def _connect_smtp() -> smtplib.SMTP:
    """587(STARTTLS) 우선 시도, 실패 시 465(SSL) 폴백 — Windows 포트 차단 대응."""
    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        smtp.ehlo()
        smtp.starttls()
        return smtp
    except Exception:
        return smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)


def _parse_md_for_email(md: str) -> dict:
    """MD 리포트에서 EN/KO 분석, 뉴스 목록, 통계 추출."""
    # 통계 파싱
    stats = {"total": 0, "en": 0, "ko": 0, "sent_to_ai": 0}
    m = re.search(r'총\s*(\d+)건.*EN:\s*(\d+).*KO:\s*(\d+).*AI 분석:\s*(\d+)', md)
    if m:
        stats = {"total": int(m.group(1)), "en": int(m.group(2)),
                 "ko": int(m.group(3)), "sent_to_ai": int(m.group(4))}

    # 분석 섹션 (헤더 내용만, 뉴스 목록 제외)
    en_m = re.search(r'## 🌐 Global News Analysis\n([\s\S]*?)(?=---\n\n## 🇰🇷|## 📋|$)', md)
    ko_m = re.search(r'## 🇰🇷 국내 뉴스 분석\n([\s\S]*?)(?=## 📋|$)', md)
    analysis_en = markdown2.markdown(en_m.group(1).strip(), extras=["tables"]) if en_m else ""
    analysis_ko = markdown2.markdown(ko_m.group(1).strip(), extras=["tables"]) if ko_m else ""

    # 뉴스 목록 (## 📋 섹션)
    news_en: list[dict] = []
    news_ko: list[dict] = []
    for sec in md.split("### "):
        is_en = sec.startswith("🌐 영어")
        is_ko = sec.startswith("🇰🇷 한국어")
        if not is_en and not is_ko:
            continue
        for line in sec.splitlines():
            pat = re.match(r'^- \*\*\[(.+?)\]\*\* \[(.+?)\]\((.+?)\)', line)
            if pat:
                item = {"label": pat.group(1), "title": pat.group(2), "link": pat.group(3)}
                (news_en if is_en else news_ko).append(item)

    return {"stats": stats, "analysis_en": analysis_en,
            "analysis_ko": analysis_ko, "news_en": news_en, "news_ko": news_ko}


def _render_email_template(md: str, recipient_email: str, theme_name: str = "classic") -> str | None:
    """Jinja2 템플릿으로 이메일 HTML 렌더링. 실패 시 None 반환(폴백 허용)."""
    if not _TEMPLATE_FILE.exists():
        logger.debug("[이메일 템플릿] storage/email_template.html 없음 → 기본 방식 사용")
        return None
    try:
        from jinja2 import Environment, FileSystemLoader

        # 테마 토큰 로드
        try:
            mod = importlib.import_module(f"themes.{theme_name}")
            tokens = mod.TOKENS
        except (ModuleNotFoundError, AttributeError):
            from themes.classic import TOKENS as tokens  # type: ignore

        c = tokens["colors"]
        t = tokens["typography"]

        # 구독 취소 URL (수신자별)
        unsubscribe_url = ""
        if SITE_BASE_URL:
            token = _make_token(recipient_email)
            encoded = urllib.parse.quote(recipient_email)
            unsubscribe_url = f"{SITE_BASE_URL}/api/unsubscribe?email={encoded}&token={token}"

        sections = _parse_md_for_email(md)
        now = datetime.now()

        env = Environment(loader=FileSystemLoader(str(_TEMPLATE_FILE.parent)),
                          autoescape=False)
        tmpl = env.get_template(_TEMPLATE_FILE.name)

        return tmpl.render(
            c=c, t=t,
            date=now.strftime("%Y-%m-%d"),
            display_date=now.strftime("%Y년 %m월 %d일"),
            site_title="AI News Daily",
            site_url=SITE_BASE_URL,
            unsubscribe_url=unsubscribe_url,
            **sections,
        )
    except Exception as e:
        logger.warning(f"[이메일 템플릿 렌더링 실패] {e} → 기본 방식으로 폴백")
        return None


def _md_to_html(md: str, recipient_email: str) -> str:
    body = markdown2.markdown(md, extras=["tables", "fenced-code-blocks"])

    if SITE_BASE_URL:
        token = _make_token(recipient_email)
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


def send_email(md_content: str, html_content: str | None = None,
               theme_name: str | None = None,
               subject_override: str | None = None) -> bool:
    """이메일 발송.
    우선순위: html_content > email_template.html > _md_to_html() 폴백
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        logger.warning("[이메일] GMAIL_USER 또는 GMAIL_APP_PASSWORD 미설정 — 발송 건너뜀")
        return False

    recipients = _get_recipients()
    if not recipients:
        logger.warning("[이메일] 발송 대상 없음 (RECIPIENT_EMAILS 미설정 또는 전원 구독 취소)")
        return False

    date_str = datetime.now().strftime("%Y-%m-%d")
    subject = subject_override if subject_override else EMAIL_SUBJECT.format(date=date_str)

    success_count = 0
    try:
        smtp = _connect_smtp()
        with smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            for email in recipients:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = GMAIL_USER
                msg["To"] = email
                if html_content:
                    body = html_content
                else:
                    _theme = theme_name or _get_email_theme()
                    body = (_render_email_template(md_content, email, _theme)
                            or _md_to_html(md_content, email))
                msg.attach(MIMEText(body, "html", "utf-8"))
                smtp.sendmail(GMAIL_USER, email, msg.as_string())
                success_count += 1
                logger.info(f"[이메일 발송] → {email}")
    except smtplib.SMTPAuthenticationError:
        logger.error("[이메일 발송 실패] Gmail 인증 오류 — 앱 비밀번호를 확인하세요")
        return False
    except Exception as e:
        logger.error(f"[이메일 발송 오류] {e}")
        return False

    logger.info(f"[이메일 발송] 완료 → {success_count}/{len(recipients)}명")
    return success_count > 0
