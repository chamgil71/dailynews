# main.py
"""
AI 자동 뉴스 리포트 — 메인 실행 파일

실행 순서:
  1. 뉴스 수집 (RSS, 한국어+영어, 중복 제거)
  2. AI 분석 (카테고리별 프롬프트, 조건부 모델 선택)
  3. Markdown 리포트 생성 (날짜별 파일명)
  4. GitHub 저장 (Actions에서 자동 커밋)
  5. 이메일 발송 (Resend)
"""

import logging
import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()  # 로컬 개발 시 .env 로드

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main")


def main():
    start = datetime.now()
    logger.info("=" * 60)
    logger.info("AI News Daily 시작")
    logger.info("=" * 60)

    # ── Step 1: 뉴스 수집 ────────────────────────────────────
    from core.collector import collect_news
    logger.info("[1/4] 뉴스 수집 중...")
    news_data = collect_news()
    stats = news_data["stats"]
    logger.info(f"     → 총 {stats['total']}건 수집 "
                f"(EN:{stats['en']} KO:{stats['ko']}) | "
                f"중복 제외:{stats['skipped_dup']}건")

    if stats["total"] == 0:
        logger.warning("수집된 뉴스가 없습니다. 종료합니다.")
        sys.exit(0)

    # ── Step 2: AI 분석 ──────────────────────────────────────
    from core.analyzer import analyze
    logger.info("[2/4] AI 분석 중...")
    analysis = analyze(news_data)
    logger.info("     → 분석 완료")

    # ── Step 3: 리포트 생성 및 저장 ──────────────────────────
    from core.report import generate, save_report
    logger.info("[3/4] 리포트 생성 중...")
    md_content = generate(news_data, analysis)
    filepath   = save_report(md_content)
    logger.info(f"     → 저장: {filepath}")

    # ── Step 4: 이메일 발송 ──────────────────────────────────
    from core.mailer import send_email
    logger.info("[4/4] 이메일 발송 중...")
    ok = send_email(md_content)
    logger.info(f"     → {'성공' if ok else '실패(로그 확인)'}")

    elapsed = (datetime.now() - start).seconds
    logger.info("=" * 60)
    logger.info(f"완료! 소요 시간: {elapsed}초")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
