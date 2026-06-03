# scripts/send_stock_telegram.py
"""
주식 시황 텔레그램 알림 독립 실행 스크립트.
reports/stock/stock_YYYY-MM-DD.md -> core/shared/telegram.py -> @msstockbrief 채널 발송.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

from scripts.build_stock_site import parse_stock_md
from core.shared.telegram import send_stock_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("send_stock_telegram")


def main() -> None:
    parser = argparse.ArgumentParser(description="주식 시황 텔레그램 발송기")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="대상 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    date_str = args.date
    md_path = Path(_ROOT) / "reports" / "stock" / f"stock_{date_str}.md"

    if not md_path.exists():
        logger.error(f"[텔레그램/주식] MD 파일이 존재하지 않습니다: {md_path}")
        sys.exit(1)

    logger.info(f"[텔레그램/주식] {date_str} 데이터 로드 중...")
    try:
        data = parse_stock_md(str(md_path), date_str)
    except Exception as e:
        logger.error(f"[텔레그램/주식] MD 파싱 에러: {e}")
        sys.exit(1)

    logger.info("[텔레그램/주식] 발송 요청 시작...")
    ok = send_stock_telegram(data, date_str)

    if ok:
        logger.info(f"[텔레그램/주식] {date_str} 텔레그램 메시지 발송 완료!")
    else:
        logger.warning("[텔레그램/주식] 발송 실패 또는 건너뜀 (설정 누락 등)")
        sys.exit(0)


if __name__ == "__main__":
    main()
