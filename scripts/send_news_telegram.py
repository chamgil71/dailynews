# scripts/send_news_telegram.py
"""
뉴스 텔레그램 독립 발송 스크립트.
reports/news_YYYY-MM-DD.json → core/shared/telegram.py → 텔레그램 채널 발송.
analysis_ok=False(AI 분석 실패) 인 경우 발송 건너뜀.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

from core.shared.telegram import send_telegram_cardnews

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("send_news_telegram")


def main() -> None:
    parser = argparse.ArgumentParser(description="뉴스 텔레그램 발송기")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="대상 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    date_str  = args.date
    json_path = Path(_ROOT) / "reports" / f"news_{date_str}.json"

    if not json_path.exists():
        logger.error(f"[텔레그램/뉴스] JSON 파일이 존재하지 않습니다: {json_path}")
        sys.exit(1)

    logger.info(f"[텔레그램/뉴스] {date_str} JSON 로드 중...")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[텔레그램/뉴스] JSON 파싱 에러: {e}")
        sys.exit(1)

    # AI 분석 실패 시 발송 건너뜀
    if not data.get("analysis_ok", True):
        logger.warning("[텔레그램/뉴스] AI 분석 실패 플래그 감지 — 발송 건너뜀")
        sys.exit(0)

    logger.info("[텔레그램/뉴스] 발송 요청 시작...")
    ok = send_telegram_cardnews(data, date_str)

    if ok:
        logger.info(f"[텔레그램/뉴스] {date_str} 텔레그램 메시지 발송 완료!")
    else:
        logger.warning("[텔레그램/뉴스] 발송 실패 또는 건너뜀 (설정 누락 등)")
        sys.exit(0)


if __name__ == "__main__":
    main()
