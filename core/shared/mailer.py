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

_TEMPLATE_FILE       = Path(__file__).parent.parent.parent / "templates" / "email_news.html"
_STOCK_TEMPLATE_FILE = Path(__file__).parent.parent.parent / "templates" / "email_stock.html"


def _get_email_theme() -> str:
    try:
        from config.theme_config import SECTION_THEMES
        return SECTION_THEMES.get("email", "classic")
    except Exception:
        return "classic"

logger = logging.getLogger(__name__)

# [구독취소 기능 주석 처리 - 향후 Supabase 이전 계획 반영 예정]
# _UNSUB_FILE = Path(__file__).parent.parent / "storage" / "unsubscribed.txt"
# 
# def _get_unsubscribed() -> set[str]:
#     # 구독 취소 비활성화 (공식 대시보드 방문 대체)
#     return set()


def _get_recipients() -> list[str]:
    # 구독 취소 필터링 없이 전체 수신자 목록 다이렉트 반환 (향후 Supabase DB 연동 계획)
    return RECIPIENT_EMAILS


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
    except Exception as e:
        logger.info(f"[SMTP] Port 587 STARTTLS 연결 실패({e}) → 465 SSL 폴백 연결 개시")
        return smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)


def _parse_md_for_email(md: str) -> dict:
    """MD 리포트에서 EN/KO 분석, 뉴스 목록, 통계 추출."""
    # 통계 파싱
    stats = {"total": 0, "en": 0, "ko": 0, "sent_to_ai": 0}
    m = re.search(r'총\s*(\d+)건.*EN:\s*(\d+).*KO:\s*(\d+).*AI 분석:\s*(\d+)', md)
    if m:
        stats = {"total": int(m.group(1)), "en": int(m.group(2)),
                 "ko": int(m.group(3)), "sent_to_ai": int(m.group(4))}

    # 분석 섹션 — KO는 키워드 섹션 직전까지, 키워드는 별도 추출
    en_m      = re.search(r'## 🌐 Global News Analysis\n([\s\S]*?)(?=---\n\n## 🇰🇷|## 🔍|## 📋|$)', md)
    ko_m      = re.search(r'## 🇰🇷 국내 뉴스 분석\n([\s\S]*?)(?=## 🔍|## 📋|$)', md)
    keyword_m = re.search(r'## 🔍 키워드 매칭 기사[^\n]*\n([\s\S]*?)(?=---\n\n## 📋|## 📋|$)', md)

    extras = ["tables", "cuddled-lists"]
    analysis_en  = markdown2.markdown(en_m.group(1).strip(),      extras=extras) if en_m      else ""
    analysis_ko  = markdown2.markdown(ko_m.group(1).strip(),      extras=extras) if ko_m      else ""
    keyword_html = markdown2.markdown(keyword_m.group(1).strip(), extras=extras) if keyword_m else ""

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

    return {"stats": stats, "analysis_en": analysis_en, "analysis_ko": analysis_ko,
            "keyword_html": keyword_html, "news_en": news_en, "news_ko": news_ko}


def _render_email_template(md: str, recipient_email: str, theme_name: str = "classic",
                           report_date: str | None = None) -> str | None:
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

        # 구독 취소 URL (백엔드 제거에 따라 홈페이지 바로가기 링크로 우회 대체)
        unsubscribe_url = SITE_BASE_URL or ""

        sections = _parse_md_for_email(md)
        dt = datetime.strptime(report_date, "%Y-%m-%d") if report_date else datetime.now()

        env = Environment(loader=FileSystemLoader(str(_TEMPLATE_FILE.parent)),
                          autoescape=False)
        tmpl = env.get_template(_TEMPLATE_FILE.name)

        return tmpl.render(
            c=c, t=t,
            date=dt.strftime("%Y-%m-%d"),
            display_date=dt.strftime("%Y년 %m월 %d일"),
            site_title="AI News Daily",
            site_url=SITE_BASE_URL,
            unsubscribe_url=unsubscribe_url,
            **sections,
        )
    except Exception as e:
        logger.warning(f"[이메일 템플릿 렌더링 실패] {e} → 기본 방식으로 폴백")
        return None


def _parse_md_for_stock_email(md: str) -> dict:
    """주식 MD에서 이메일 섹션 추출."""
    _SEP = r'(?=\n---|\n## |\Z)'
    summary_m  = re.search(r'## ■ 핵심 요약[^\n]*\n([\s\S]*?)' + _SEP, md, re.M)
    keywords_m = re.search(r'## (?:3\. )?핵심 키워드[^\n]*\n([\s\S]*?)' + _SEP, md, re.M)
    notable_m  = re.search(r'## (?:4\. )?주목 섹터[^\n]*\n([\s\S]*?)' + _SEP, md, re.M)
    risk_m     = re.search(r'## (?:5\. )?리스크[^\n]*\n([\s\S]*?)' + _SEP, md, re.M)
    lt_m       = re.search(r'## (?:6\. )?장기투자[^\n]*\n([\s\S]*?)' + _SEP, md, re.M)
    temp_m     = re.search(r'## 시장 온도계[:\s]*(.*)', md)
    reason_m   = re.search(r'## 시장 온도계.*\n+>\s*(.*)', md)

    _ext = ["tables", "cuddled-lists"]
    summary_html    = markdown2.markdown(summary_m.group(1).strip(),  extras=_ext) if summary_m  else ""
    keywords_html   = markdown2.markdown(keywords_m.group(1).strip(), extras=_ext) if keywords_m else ""
    notable_html    = markdown2.markdown(notable_m.group(1).strip(),  extras=_ext) if notable_m  else ""
    risk_html       = markdown2.markdown(risk_m.group(1).strip(),     extras=_ext) if risk_m     else ""
    lt_comment_html = markdown2.markdown(lt_m.group(1).strip(),       extras=_ext) if lt_m       else ""

    temperature_display = temp_m.group(1).strip() if temp_m else "🟡 중립"
    temperature_reason  = reason_m.group(1).strip() if reason_m else ""

    if "리스크오프" in temperature_display or "🔴" in temperature_display:
        temperature_color = "#dc2626"
    elif "🔵" in temperature_display or "침체" in temperature_display:
        temperature_color = "#2563eb"
    elif "리스크온" in temperature_display or "🟢" in temperature_display:
        temperature_color = "#16a34a"
    else:
        temperature_color = "#ca8a04"

    return {
        "summary_html":        summary_html,
        "keywords_html":       keywords_html,
        "notable_html":        notable_html,
        "risk_html":           risk_html,
        "lt_comment_html":     lt_comment_html,
        "temperature_display": temperature_display,
        "temperature_color":   temperature_color,
        "temperature_reason":  temperature_reason,
    }


def _render_stock_email_template(md: str, recipient_email: str, theme_name: str = "classic",
                                  report_date: str | None = None) -> str | None:
    """주식 시황 전용 Jinja2 템플릿 렌더링. 실패 시 None 반환."""
    if not _STOCK_TEMPLATE_FILE.exists():
        logger.debug("[주식 이메일 템플릿] stock_email_template.html 없음 → 기본 방식 사용")
        return None
    try:
        from jinja2 import Environment, FileSystemLoader

        try:
            mod = importlib.import_module(f"themes.{theme_name}")
            tokens = mod.TOKENS
        except (ModuleNotFoundError, AttributeError):
            from themes.classic import TOKENS as tokens  # type: ignore

        c = tokens["colors"]
        t = tokens["typography"]

        unsubscribe_url = SITE_BASE_URL or ""

        sections = _parse_md_for_stock_email(md)
        dt = datetime.strptime(report_date, "%Y-%m-%d") if report_date else datetime.now()

        env = Environment(loader=FileSystemLoader(str(_STOCK_TEMPLATE_FILE.parent)),
                          autoescape=False)
        tmpl = env.get_template(_STOCK_TEMPLATE_FILE.name)

        return tmpl.render(
            c=c, t=t,
            date=dt.strftime("%Y-%m-%d"),
            display_date=dt.strftime("%Y년 %m월 %d일"),
            site_url=SITE_BASE_URL,
            unsubscribe_url=unsubscribe_url,
            **sections,
        )
    except Exception as e:
        logger.warning(f"[주식 이메일 템플릿 렌더링 실패] {e} → 기본 방식으로 폴백")
        return None


def _md_to_html(md: str, recipient_email: str) -> str:
    body = markdown2.markdown(md, extras=["tables", "fenced-code-blocks"])

    if SITE_BASE_URL:
        unsub_link = f'<a href="{SITE_BASE_URL}" style="color:#aaa">AI News Daily 대시보드 바로가기</a>'
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


def send_email(md_content: str = "", html_content: str | None = None,
               theme_name: str | None = None,
               subject_override: str | None = None,
               template: str | None = None,
               report_date: str | None = None) -> bool:
    """이메일 발송.
    template: "stock" → stock_email_template.html, None/"news" → email_template.html
    report_date: 이메일 본문에 표시할 리포트 날짜 (YYYY-MM-DD). 미전달 시 실행일 사용.
    우선순위: html_content > template 렌더러 > _md_to_html() 폴백
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
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"] = GMAIL_USER
                    msg["To"] = email
                    if html_content:
                        body = html_content
                    elif template == "stock":
                        _theme = theme_name or _get_email_theme()
                        body = (_render_stock_email_template(md_content, email, _theme, report_date)
                                or _md_to_html(md_content, email))
                    else:
                        _theme = theme_name or _get_email_theme()
                        body = (_render_email_template(md_content, email, _theme, report_date)
                                or _md_to_html(md_content, email))
                    msg.attach(MIMEText(body, "html", "utf-8"))
                    smtp.sendmail(GMAIL_USER, email, msg.as_string())
                    success_count += 1
                    logger.info(f"[이메일 발송] → {email}")
                except Exception as ex:
                    logger.error(f"[이메일 개별 발송 실패] 대상: {email}, 오류: {ex}")
    except smtplib.SMTPAuthenticationError:
        logger.error("[이메일 발송 실패] Gmail 인증 오류 — 앱 비밀번호를 확인하세요")
        return False
    except Exception as e:
        logger.error(f"[이메일 연결/로그인 오류] {e}")
        return False

    logger.info(f"[이메일 발송] 완료 → {success_count}/{len(recipients)}명")
    return success_count > 0
