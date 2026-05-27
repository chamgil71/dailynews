"""
뉴스 수집·분석·저장·발송 실행 진입점.

실행: python scripts/run_news.py
      (또는 루트에서 python main.py — 동일)

흐름:
  1. 뉴스 수집 (RSS, 한국어+영어, 중복 제거)
  2. AI 분석 (카테고리별 프롬프트)
  3. Markdown 리포트 생성 (reports/news_YYYY-MM-DD.md)
  4. DB 누적 저장 (storage/news_db.xlsx)
  5. 이메일 발송 (Gmail SMTP)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# SSL 검증 복원 완료 (안전화)

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
    logger.info("[1/5] 뉴스 수집 중...")
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
    logger.info("[2/5] AI 분석 중...")
    analysis = analyze(news_data)
    logger.info("     → 분석 완료")

    from core.news.report import generate, save_report
    logger.info("[3/5] 리포트 생성 중...")
    md_content = generate(news_data, analysis)
    filepath = save_report(md_content, structured=analysis.get("structured"))
    logger.info(f"     → 저장: {filepath}")

    from core.shared.db import append_news
    logger.info("[4/5] DB 누적 저장 중...")
    date_tag = datetime.now().strftime("%Y-%m-%d")
    added = append_news(news_data.get("all", []), date_tag)
    logger.info(f"     → 엑셀 DB: {added}건 저장 완료")
    # ※ Notion 동기화는 workflows에서 scripts/sync_notion.py --type news 로 별도 실행

    from core.shared.mailer import send_email
    logger.info("[5/5] 이메일 발송 중...")
    ok = send_email(md_content)
    logger.info(f"     → {'성공' if ok else '실패(로그 확인)'}")

    # [6/6] 텔레그램 카드뉴스 발송
    structured_data = analysis.get("structured")
    if structured_data:
        from core.shared.telegram import send_telegram_cardnews
        logger.info("[6/6] 텔레그램 카드뉴스 발송 중...")
        tg_ok = send_telegram_cardnews(structured_data, date_tag)
        logger.info(f"     → {'성공' if tg_ok else '실패(로그 확인)'}")
    else:
        logger.info("[6/6] 구조화된 분석 데이터가 없어 텔레그램 발송을 건너뜁니다.")

    elapsed = (datetime.now() - start).seconds
    logger.info("=" * 60)
    logger.info(f"완료! 소요 시간: {elapsed}초")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
