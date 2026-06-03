# scripts/send_news_email.py
"""
뉴스 이메일 독립 발송 스크립트.
reports/news_YYYY-MM-DD.md → core/shared/mailer.py → Gmail 개별 발송.
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

from core.shared.mailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("send_news_email")


def main() -> None:
    parser = argparse.ArgumentParser(description="뉴스 이메일 발송기")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="대상 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    date_str = args.date
    md_path   = Path(_ROOT) / "reports" / f"news_{date_str}.md"
    json_path = Path(_ROOT) / "reports" / f"news_{date_str}.json"

    if not md_path.exists():
        logger.error(f"[이메일/뉴스] MD 파일이 존재하지 않습니다: {md_path}")
        sys.exit(1)

    # AI 분석 실패 시 구독자 발송 건너뜀 (관리자 알림은 run_news.py에서 처리)
    if json_path.exists():
        try:
            meta = json.loads(json_path.read_text(encoding="utf-8"))
            if not meta.get("analysis_ok", True):
                logger.warning("[이메일/뉴스] AI 분석 실패 플래그 감지 — 구독자 발송 건너뜀")
                sys.exit(0)
        except Exception:
            pass

    logger.info(f"[이메일/뉴스] {date_str} MD 로드 중...")
    md_content = md_path.read_text(encoding="utf-8")

    logger.info("[이메일/뉴스] 발송 요청 시작...")
    ok = send_email(md_content)

    if ok:
        logger.info(f"[이메일/뉴스] {date_str} 이메일 발송 완료!")
    else:
        logger.warning("[이메일/뉴스] 발송 실패 또는 건너뜀 (설정 누락 등)")
        sys.exit(0)


if __name__ == "__main__":
    main()
