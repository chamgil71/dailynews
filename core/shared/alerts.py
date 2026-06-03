"""
LLM 오류 알림 유틸리티.

GitHub Actions 환경에서 ::error:: / ::warning:: 어노테이션을 출력하고,
GMAIL이 설정된 경우 관리자 이메일로 알림을 발송한다.
"""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# 모델 만료·불가 관련 오류 키워드
_MODEL_EXPIRED_KEYWORDS = (
    "deprecated", "not found", "does not exist",
    "model_not_found", "404", "INVALID_ARGUMENT",
    "not supported", "unavailable model",
)


def is_model_error(err: Exception) -> bool:
    """모델명 만료·미존재로 인한 오류인지 판단."""
    s = str(err).lower()
    return any(kw in s for kw in _MODEL_EXPIRED_KEYWORDS)


def gha_error(msg: str) -> None:
    """GitHub Actions ::error:: 어노테이션 출력 (CI 로그에 빨간 오류 표시)."""
    print(f"::error::{msg}", flush=True)
    logger.error(msg)


def gha_warning(msg: str) -> None:
    """GitHub Actions ::warning:: 어노테이션 출력 (CI 로그에 노란 경고 표시)."""
    print(f"::warning::{msg}", flush=True)
    logger.warning(msg)


def send_llm_failure_alert(
    provider: str,
    model: str,
    error: Exception,
    context: str = "",
) -> None:
    """
    LLM 분석 실패 시 관리자(GMAIL_USER)에게 이메일 알림 발송.
    GMAIL_USER / GMAIL_APP_PASSWORD 미설정 시 로그만 출력.
    """
    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_pw   = os.getenv("GMAIL_APP_PASSWORD", "")

    err_str  = str(error)
    expired  = is_model_error(error)
    tag      = "🔴 모델 만료/미존재" if expired else "⚠ LLM 호출 실패"
    subject  = f"[DailyNews] {tag} — {provider}/{model}"

    body_lines = [
        f"제공자: {provider}",
        f"모델명: {model}",
        f"오류: {err_str}",
    ]
    if context:
        body_lines.append(f"컨텍스트: {context}")
    if expired:
        body_lines += [
            "",
            "⚠ 모델명이 만료되었거나 존재하지 않습니다.",
            "config/settings.py 의 GEMINI_MODEL_FULL / GEMINI_MODEL_MINI 를 최신 모델명으로 교체하세요.",
        ]
    body = "\n".join(body_lines)

    gha_error(f"LLM 분석 실패 [{provider}/{model}]: {err_str[:120]}")

    if not gmail_user or not gmail_pw:
        logger.warning("[alerts] GMAIL 미설정 — 이메일 알림 불가")
        return

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"]    = gmail_user
        msg["To"]      = gmail_user
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(gmail_user, gmail_pw)
            s.sendmail(gmail_user, [gmail_user], msg.as_string())
        logger.info(f"[alerts] 관리자 알림 발송 → {gmail_user}")
    except Exception as mail_err:
        logger.error(f"[alerts] 이메일 발송 실패: {mail_err}")
