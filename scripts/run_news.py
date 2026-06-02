"""
뉴스 수집·분석·저장·발송 실행 진입점.

실행: python scripts/run_news.py
      (또는 루트에서 python main.py — 동일)

흐름:
  1. 뉴스 수집 (RSS, 한국어+영어, 중복 제거)
  2. AI 분석 (카테고리별 프롬프트)
  3. Markdown 리포트 생성 (reports/news_YYYY-MM-DD.md)
  4. DB 누적 저장 (storage/news_db.xlsx)
  5. 품질 게이트 — AI 분석 실패 시 발송 차단, 관리자 알림만 발송
  6. 이메일 발송 (Gmail SMTP)
  7. 텔레그램 카드뉴스 발송
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
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_news")


def _send_failure_alert(date_tag: str, fallback_used: dict) -> None:
    """AI 분석 실패 시 관리자(GMAIL_USER)에게만 알림 메일 발송."""
    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_pw   = os.getenv("GMAIL_APP_PASSWORD", "")
    if not gmail_user or not gmail_pw:
        logger.warning("[품질게이트] GMAIL 미설정 — 관리자 알림 발송 불가")
        return

    en_fail = fallback_used.get("en", False)
    ko_fail = fallback_used.get("ko", False)
    fail_detail = ", ".join(filter(None, [
        "영어(EN)" if en_fail else "",
        "한국어(KO)" if ko_fail else "",
    ]))

    subject = f"[DailyNews] ⚠ {date_tag} 뉴스 분석 실패 — 재분석 필요"
    body = (
        f"날짜: {date_tag}\n"
        f"실패 항목: {fail_detail}\n\n"
        f"AI 분석 결과가 없어 이메일/텔레그램 발송을 건너뛰었습니다.\n"
        f"GitHub Actions에서 수동 재실행하거나 LLM 상태를 확인하세요.\n\n"
        f"workflow_dispatch → news.yml → Run workflow"
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = gmail_user
    msg["To"]      = gmail_user

    try:
        smtp = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, gmail_pw)
        smtp.sendmail(gmail_user, [gmail_user], msg.as_string())
        smtp.quit()
        logger.info(f"[품질게이트] 관리자 알림 발송 완료 → {gmail_user}")
    except Exception as e:
        logger.error(f"[품질게이트] 관리자 알림 발송 실패: {e}")


def main() -> None:
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("AI News Daily 시작")
    logger.info("=" * 60)

    from core.news.collector import collect_news
    logger.info("[1/7] 뉴스 수집 중...")
    news_data = collect_news()
    stats = news_data["stats"]
    logger.info(f"     → 총 {stats['total']}건 수집 "
                f"(EN:{stats['en']} KO:{stats['ko']}) | "
                f"키워드:{stats['keyword_matches']}건 | "
                f"중복 제외:{stats['skipped_dup']}건")

    if stats["total"] == 0:
        logger.warning("수집된 뉴스가 없습니다. 종료합니다.")
        sys.exit(0)

    from core.news.analyzer import analyze
    logger.info("[2/7] AI 분석 중...")
    analysis = analyze(news_data)
    analysis_ok   = analysis.get("analysis_ok", False)
    fallback_used = analysis.get("fallback_used", {})
    logger.info(f"     → 분석 완료 (analysis_ok={analysis_ok}, fallback={fallback_used})")

    from core.news.report import generate, save_report
    logger.info("[3/7] 리포트 생성 중...")
    md_content = generate(news_data, analysis)
    date_tag   = datetime.now().strftime("%Y-%m-%d")
    # analysis_ok / fallback_used 플래그를 JSON 사이드카에 포함
    structured = analysis.get("structured") or {}
    structured["date"]          = date_tag
    structured["analysis_ok"]   = analysis_ok
    structured["fallback_used"] = fallback_used
    filepath = save_report(md_content, structured=structured)
    logger.info(f"     → 저장: {filepath}")

    from core.shared.db import append_news
    logger.info("[4/7] DB 누적 저장 중...")
    added = append_news(news_data.get("all", []), date_tag)
    logger.info(f"     → 엑셀 DB: {added}건 저장 완료")
    # ※ Notion 동기화는 workflows에서 scripts/sync_notion.py --type news 로 별도 실행

    # ── 품질 게이트: 분석 실패 시 발송 차단 ────────────────────────────────────
    if not analysis_ok:
        logger.warning(f"[5/7] 품질게이트 차단 — AI 분석 실패 (fallback: {fallback_used})")
        _send_failure_alert(date_tag, fallback_used)
        logger.info("     → 관리자 알림 발송 후 종료 (이메일/텔레그램 전체 발송 건너뜀)")
        elapsed = (datetime.now() - start).seconds
        logger.info(f"완료(분석실패 종료). 소요 시간: {elapsed}초")
        return

    from core.shared.mailer import send_email
    logger.info("[5/7] 이메일 발송 중...")
    ok = send_email(md_content)
    logger.info(f"     → {'성공' if ok else '실패(로그 확인)'}")

    # 텔레그램 카드뉴스 발송
    logger.info("[6/7] 텔레그램 카드뉴스 발송 중...")
    structured_data = analysis.get("structured")
    if structured_data:
        from core.shared.telegram import send_telegram_cardnews
        tg_ok = send_telegram_cardnews(structured_data, date_tag)
        logger.info(f"     → {'성공' if tg_ok else '실패(로그 확인)'}")
    else:
        logger.info("     → 구조화된 분석 데이터가 없어 텔레그램 발송을 건너뜁니다.")

    logger.info("[7/7] 완료")
    elapsed = (datetime.now() - start).seconds
    logger.info("=" * 60)
    logger.info(f"완료! 소요 시간: {elapsed}초")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
