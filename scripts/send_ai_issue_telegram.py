# scripts/send_ai_issue_telegram.py
"""
주간 AI 이슈 텔레그램 알림 독립 실행 스크립트.
reports/ai-issue/ai_issue_YYYY-MM-DD.json -> core/shared/telegram.py -> 텔레그램 채널 발송.
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

from core.shared.telegram import send_ai_issue_telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("send_ai_issue_telegram")


def main() -> None:
    parser = argparse.ArgumentParser(description="주간 AI 이슈 텔레그램 발송기")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="대상 주간 일요일 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()
    
    date_str = args.date
    json_path = Path(_ROOT) / "reports" / "ai-issue" / f"ai_issue_{date_str}.json"
    
    if not json_path.exists():
        logger.error(f"[텔레그램] 주간 JSON 파일이 존재하지 않습니다: {json_path}")
        sys.exit(1)
        
    logger.info(f"[텔레그램] {date_str} 주간 데이터 로드 중...")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[텔레그램] JSON 파싱 에러: {e}")
        sys.exit(1)
        
    logger.info("[텔레그램] 발송 요청 시작...")
    ok = send_ai_issue_telegram(data, date_str)
    
    if ok:
        logger.info(f"[텔레그램] {date_str} 주간 텔레그램 메시지 발송 완료!")
    else:
        logger.warning(f"[텔레그램] 발송 실패 또는 건너뜀 (설정 누락 등)")
        # API 토큰이나 채팅 ID가 없어서 건너뛴 경우도 에러로 처리하지는 않음 (GHA 전체가 깨지는 것을 방지)
        sys.exit(0)


if __name__ == "__main__":
    main()
