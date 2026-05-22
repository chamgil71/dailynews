"""
주식 시황 수집·분석·저장·발송 실행 진입점.

실행: python scripts/run_stock.py
      (또는 python scripts/stock_main.py — 동일)

흐름:
  1. yfinance + Naver API로 시장 데이터 수집
  2. LLM 분석 (Gemini/GPT/Claude)
  3. MD 리포트 생성 및 저장 (reports/stock/stock_YYYY-MM-DD.md)
  4. 이메일 발송 (Gmail SMTP)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

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


def main() -> None:
    logger.info("=" * 55)
    logger.info("Stock Briefing — 주식 시황 실행")
    logger.info("=" * 55)

    date_str = datetime.now().strftime("%Y-%m-%d")
    _primary_ran = Path(f"reports/stock/stock_{date_str}.md").exists()

    logger.info("[1/4] 시장 데이터 수집 중...")
    from core.stock.collector import build_stock_data
    stock_data = build_stock_data()

    logger.info("[2/4] LLM 분석 중...")
    from core.stock.analyzer import analyze_stock
    analysis = analyze_stock(stock_data)
    logger.info(f"     시장 온도계: {analysis.get('temperature_display', '?')}")

    logger.info("[3/4] 리포트 생성 및 저장 중...")
    from core.stock.report import generate, save
    md_content = generate(stock_data, analysis)
    filepath = save(md_content, date_str)
    logger.info(f"     저장: {filepath}")

    if _primary_ran:
        logger.info("[4/4] Primary 경로 실행 확인 — 이메일 발송 건너뜀")
    else:
        logger.info("[4/4] 이메일 발송 중...")
        from core.shared.mailer import send_email
        from config.settings import STOCK_EMAIL_SUBJECT
        parts = [f"# 📊 주식 시황 브리핑 — {date_str}"]
        if analysis.get("summary"):
            parts += ["\n## ■ 핵심 요약 (3줄)", analysis["summary"]]
        if analysis.get("keywords"):
            parts += ["\n## 핵심 키워드 TOP 5", analysis["keywords"]]
        temp = analysis.get("temperature_display", "🟡 중립")
        reason = analysis.get("temperature_reason", "")
        parts += [f"\n## 시장 온도계: {temp}", f"> {reason}", "\n---\n※ 투자 권유 아님."]
        email_md = "\n\n".join(parts)
        ok = send_email(email_md, template="stock", subject_override=STOCK_EMAIL_SUBJECT.format(
            date=date_str,
            weekday=_weekday_ko(datetime.now().weekday()),
        ))
        logger.info(f"     이메일: {'성공' if ok else '실패(로그 확인)'}")

    logger.info("=" * 55)
    logger.info(f"완료 → {filepath}")
    logger.info("=" * 55)


if __name__ == "__main__":
    main()
