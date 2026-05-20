# scripts/stock_main.py
"""
주식 시황 브리핑 자동화 진입점 (GitHub Actions 백업 경로).

실행: python scripts/stock_main.py

흐름:
  1. yfinance + Naver API 로 시장 데이터 수집
  2. LLM 분석 (Gemini/GPT/Claude)
  3. MD 리포트 생성 및 저장 (reports/stock/stock_YYYY-MM-DD.md)
  4. 이메일 발송 (core/mailer.py — 기존 SMTP)

  HTML 빌드 및 Pages 배포는 GitHub Actions (stock_build.yml) 가 이 스크립트 실행 후
  별도 step 으로 build_stock_site.py / build_site.py 를 호출하여 처리한다.

Claude Code 루틴 경로에서는 이 스크립트 대신
config/stock_prompts.py 의 STOCK_ROUTINE_PROMPT 를 사용한다.
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 설정
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


def main() -> None:
    logger.info("=" * 55)
    logger.info("Stock Briefing — Automated Backup Path")
    logger.info("=" * 55)

    date_str = datetime.now().strftime("%Y-%m-%d")

    # Primary 경로(Claude 루틴) 실행 여부 — MD 파일이 이미 존재하면 중복 실행
    _primary_ran = Path(f"reports/stock/stock_{date_str}.md").exists()

    # ── 1. 데이터 수집 ──────────────────────────────────────────
    logger.info("[1/4] 시장 데이터 수집 중...")
    from core.stock_collector import build_stock_data
    stock_data = build_stock_data()

    # ── 2. LLM 분석 ────────────────────────────────────────────
    logger.info("[2/4] LLM 분석 중...")
    from core.stock_analyzer import analyze_stock
    analysis = analyze_stock(stock_data)
    logger.info(f"     시장 온도계: {analysis.get('temperature_display','?')}")

    # ── 3. MD 생성 및 저장 ──────────────────────────────────────
    logger.info("[3/4] 리포트 생성 및 저장 중...")
    from core.stock_report import generate, save
    md_content = generate(stock_data, analysis)
    filepath   = save(md_content, date_str)
    logger.info(f"     저장: {filepath}")

    # ── 4. 이메일 발송 ──────────────────────────────────────────
    if _primary_ran:
        logger.info("[4/4] Primary 경로(루틴) 실행 확인 — 이메일 발송 건너뜀 (중복 방지)")
    else:
        logger.info("[4/4] 이메일 발송 중...")
        from core.mailer import send_email
        from config.settings import STOCK_EMAIL_SUBJECT
        ok = send_email(md_content, template="stock", subject_override=STOCK_EMAIL_SUBJECT.format(
            date=date_str,
            weekday=_weekday_ko(datetime.now().weekday()),
        ))
        logger.info(f"     이메일: {'성공' if ok else '실패(로그 확인)'}")

    logger.info("=" * 55)
    logger.info(f"완료 → {filepath}")
    logger.info("=" * 55)


def _weekday_ko(wd: int) -> str:
    return ["월","화","수","목","금","토","일"][wd]


if __name__ == "__main__":
    main()
