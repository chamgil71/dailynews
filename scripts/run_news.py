"""
뉴스 수집·분석·저장 실행 진입점.

실행: python scripts/run_news.py
      (또는 루트에서 python main.py — 동일)

흐름:
  1. 뉴스 수집 (RSS, 한국어+영어, 중복 제거)
  2. AI 분석 (카테고리별 프롬프트)
  3. Markdown 리포트 생성 (reports/news_YYYY-MM-DD.md)
  4. DB 누적 저장 (storage/news_db.xlsx)
  5. 품질 게이트 — AI 분석 실패 시 관리자 알림만 발송 후 종료

이메일·텔레그램 발송: scripts/send_news_email.py / scripts/send_news_telegram.py
(news.yml 에서 HTML 빌드·배포 완료 후 별도 실행)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
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
    from core.shared.report_date import kst_today
    date_tag   = kst_today()
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

    # ── 품질 게이트: 분석 실패 시 관리자 알림만 발송 ──────────────────────────
    if not analysis_ok:
        logger.warning(f"[5/5] 품질게이트 — AI 분석 실패 (fallback: {fallback_used})")
        from core.shared.alert import send_pipeline_alert
        fail_detail = ", ".join(filter(None, [
            "영어(EN)" if fallback_used.get("en") else "",
            "한국어(KO)" if fallback_used.get("ko") else "",
        ])) or "알 수 없음"
        send_pipeline_alert("news", date_tag, f"AI 분석 폴백 발생 — {fail_detail}")
        logger.info("     → 관리자 알림 발송 후 종료 (이메일/텔레그램은 send_news_*.py 에서 자동 건너뜀)")
        elapsed = (datetime.now() - start).seconds
        logger.info(f"완료(분석실패 종료). 소요 시간: {elapsed}초")
        return

    logger.info("[5/5] 완료 (이메일·텔레그램은 HTML 빌드·배포 후 별도 실행)")
    elapsed = (datetime.now() - start).seconds
    logger.info("=" * 60)
    logger.info(f"완료! 소요 시간: {elapsed}초")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
