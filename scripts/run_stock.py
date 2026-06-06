"""
주식 시황 수집·분석·저장·발송 실행 진입점.

실행: python scripts/run_stock.py
      (또는 python scripts/stock_main.py — 동일)

흐름:
  1. 실행 시각 검증 (주말·장 전 경고)
  2. yfinance + Naver API로 시장 데이터 수집
  3. LLM 분석 (Gemini/GPT/Claude)
  4. MD 리포트 생성 및 저장 (reports/stock/stock_YYYY-MM-DD.md)
  5. 품질 게이트 — 분석 비어있으면 이메일 발송 차단, 관리자 알림
  6. 이메일 발송 (Gmail SMTP)
"""
from __future__ import annotations

import logging
import os
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def _weekday_ko(wd: int) -> str:
    return ["월", "화", "수", "목", "금", "토", "일"][wd]


def _is_analysis_complete(analysis: dict) -> bool:
    """핵심 요약 또는 시장 온도계 근거가 있으면 분석 완료로 판단."""
    summary = (analysis.get("summary") or "").strip()
    reason  = (analysis.get("temperature_reason") or "").strip()
    return bool(summary and reason)


def _send_failure_alert(date_str: str, reason: str) -> None:
    """분석 실패 시 관리자(GMAIL_USER)에게만 알림 발송."""
    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_pw   = os.getenv("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_pw:
        logger.warning("[품질게이트] GMAIL 미설정 — 관리자 알림 발송 불가")
        return
    try:
        subject = f"[DailyNews] ⚠ {date_str} 주식 시황 분석 실패"
        body    = f"날짜: {date_str}\n사유: {reason}\n\nAI 분석이 비어있어 이메일/발송을 건너뛰었습니다."
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"]    = gmail_user
        msg["To"]      = gmail_user
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(gmail_user, gmail_pw)
            s.sendmail(gmail_user, [gmail_user], msg.as_string())
        logger.info(f"[품질게이트] 관리자 알림 발송: {gmail_user}")
    except Exception as e:
        logger.error(f"[품질게이트] 알림 발송 실패: {e}")


def main() -> None:
    logger.info("=" * 55)
    logger.info("Stock Briefing — 주식 시황 실행")
    logger.info("=" * 55)

    now_weekday = datetime.now().weekday()

    # ── 주말 체크 ─────────────────────────────────────────────────────────────
    if now_weekday >= 5:
        logger.warning(f"[주말 감지] — 주식 시장 휴장. 수집만 하고 이메일은 건너뜀.")

    # ── [1/5] 시장 데이터 수집 ────────────────────────────────────────────────
    logger.info("[1/5] 시장 데이터 수집 중...")
    from core.stock.collector import build_stock_data
    stock_data = build_stock_data()

    # 파일명·이메일 등 모든 날짜는 실제 거래일 기준
    date_str = stock_data.get("trading_date", datetime.now().strftime("%Y-%m-%d"))
    weekday  = datetime.strptime(date_str, "%Y-%m-%d").weekday()
    logger.info(f"[거래일 기준] date_str={date_str}")

    _primary_ran = Path(f"reports/stock/stock_{date_str}.md").exists()

    # 장 전/장중 경고 로깅
    if not stock_data.get("after_market_close", True):
        logger.warning(
            f"[장 마감 전] 실행 시각이 15:30 KST 이전 — "
            f"데이터 기준일: {date_str} (전 거래일)"
        )

    # ── [2/5] LLM 분석 ────────────────────────────────────────────────────────
    logger.info("[2/5] LLM 분석 중...")
    from core.stock.analyzer import analyze_stock
    analysis = analyze_stock(stock_data)
    logger.info(f"     시장 온도계: {analysis.get('temperature_display', '?')}")

    # ── [3/5] 품질 게이트 + 리포트 생성 및 저장 ──────────────────────────────
    logger.info("[3/5] 리포트 생성 및 저장 중...")
    from core.stock.report import generate, save
    md_content = generate(stock_data, analysis)

    # 분석 완료 여부를 저장 전에 판단 — 미완성이면 MD를 저장하지 않음
    analysis_ok = _is_analysis_complete(analysis)
    if not analysis_ok:
        logger.warning("[품질게이트] AI 분석 미완성 — MD 저장 및 이메일/발송 차단")
        _send_failure_alert(date_str,
            f"summary={'있음' if analysis.get('summary') else '없음'}, "
            f"temperature_reason={'있음' if analysis.get('temperature_reason') else '없음'}"
        )
        logger.info("=" * 55)
        logger.info(f"분석 실패로 종료 — MD 파일 미저장 ({date_str})")
        logger.info("=" * 55)
        return

    filepath = save(md_content, date_str)
    logger.info(f"     저장: {filepath}")

    # ── [5/5] 이메일 발송 ────────────────────────────────────────────────────
    if _primary_ran:
        logger.info("[5/5] Primary 경로 실행 확인 — 이메일 발송 건너뜀")
    elif weekday >= 5:
        logger.info("[5/5] 주말 — 이메일 발송 건너뜀")
    else:
        logger.info("[5/5] 이메일 발송 중...")
        from core.shared.mailer import send_email
        from config.settings import STOCK_EMAIL_SUBJECT
        parts = [f"# 📊 주식 시황 브리핑 — {date_str}"]
        if analysis.get("summary"):
            parts += ["\n## ■ 핵심 요약 (3줄)", analysis["summary"]]
        if analysis.get("keywords"):
            parts += ["\n## 핵심 키워드 TOP 5", analysis["keywords"]]
        temp   = analysis.get("temperature_display", "🟡 중립")
        reason = analysis.get("temperature_reason", "")
        parts += [f"\n## 시장 온도계: {temp}", f"> {reason}", "\n---\n※ 투자 권유 아님."]
        email_md = "\n\n".join(parts)
        ok = send_email(email_md, template="stock", subject_override=STOCK_EMAIL_SUBJECT.format(
            date=date_str,
            weekday=_weekday_ko(weekday),
        ))
        logger.info(f"     이메일: {'성공' if ok else '실패(로그 확인)'}")

    logger.info("=" * 55)
    logger.info(f"완료 → {filepath}")
    logger.info("=" * 55)


if __name__ == "__main__":
    main()
