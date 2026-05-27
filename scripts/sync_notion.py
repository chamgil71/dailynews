"""
Notion 데이터베이스 동기화 독립 스크립트.

사용법:
  python scripts/sync_notion.py --type news  [--date 2026-05-27]
  python scripts/sync_notion.py --type stock [--date 2026-05-27]
  python scripts/sync_notion.py --type ai-issue [--date 2026-06-01]

GitHub Actions에서 이메일·텔레그램과 동일하게 별도 스텝으로 실행.
환경변수: NOTION_API_KEY, NOTION_DATABASE_ID_NEWS, NOTION_DATABASE_ID_STOCK,
          NOTION_DATABASE_ID_AI_ISSUE
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
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
logger = logging.getLogger("sync_notion")

_REPORTS_DIR = Path(_ROOT) / "reports"


# ──────────────────────────────────────────────
# 뉴스 동기화
# ──────────────────────────────────────────────

def sync_news(date_str: str) -> int:
    """reports/news_YYYY-MM-DD.json → Notion 뉴스 DB"""
    json_path = _REPORTS_DIR / f"news_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[뉴스] 파일 없음: {json_path}")
        return 0

    data = json.loads(json_path.read_text(encoding="utf-8"))
    news_items = data.get("all", data.get("news_en", []) + data.get("news_ko", []))

    if not news_items:
        logger.warning(f"[뉴스] {date_str} 동기화할 기사 없음.")
        return 0

    from core.shared.notion import sync_news_to_notion
    count = sync_news_to_notion(news_items, date_str)
    logger.info(f"[뉴스] {date_str} → Notion {count}건 완료")
    return count


# ──────────────────────────────────────────────
# 주식 동기화
# ──────────────────────────────────────────────

def _parse_stock_md(md_path: Path) -> tuple[str, dict]:
    """stock_YYYY-MM-DD.md에서 핵심 요약과 주요 지표 파싱"""
    text = md_path.read_text(encoding="utf-8")

    # 핵심 요약 3줄
    summary_lines = []
    in_summary = False
    for line in text.splitlines():
        if "핵심 요약" in line:
            in_summary = True
            continue
        if in_summary:
            stripped = line.strip()
            if stripped.startswith("- "):
                summary_lines.append(stripped[2:])
            elif stripped.startswith("#") and summary_lines:
                break
    summary = "\n".join(summary_lines[:3])

    # 주요 지표 파싱 (테이블에서 수치 추출)
    market_data = {}
    patterns = {
        "kospi":         r"코스피\s*\|\s*([\d,\.]+)",
        "kosdaq":        r"코스닥\s*\|\s*([\d,\.]+)",
        "exchange_rate": r"원/달러\s*\|\s*([\d,\.]+)",
        "sp500":         r"S&P\s*500\s*\|\s*([\d,\.]+)",
        "nasdaq":        r"나스닥\s*\|\s*([\d,\.]+)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            try:
                market_data[key] = float(m.group(1).replace(",", ""))
            except ValueError:
                pass

    return summary, market_data


def sync_stock(date_str: str) -> bool:
    """reports/stock/stock_YYYY-MM-DD.md → Notion 주식 DB"""
    md_path = _REPORTS_DIR / "stock" / f"stock_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[주식] 파일 없음: {md_path}")
        return False

    summary, market_data = _parse_stock_md(md_path)

    from core.shared.notion import sync_stock_to_notion
    ok = sync_stock_to_notion(date_str, summary, market_data)
    logger.info(f"[주식] {date_str} → Notion {'완료' if ok else '실패'}")
    return ok


# ──────────────────────────────────────────────
# AI Issue 동기화
# ──────────────────────────────────────────────

def sync_ai_issue(date_str: str) -> int:
    """reports/ai-issue/ai_issue_YYYY-MM-DD.json → Notion AI Issue DB"""
    json_path = _REPORTS_DIR / "ai-issue" / f"ai_issue_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[AI이슈] 파일 없음: {json_path}")
        return 0

    data = json.loads(json_path.read_text(encoding="utf-8"))
    top10   = data.get("top10", [])
    period  = data.get("period", "")
    outlook = data.get("next_week_outlook", "")

    from core.shared.notion import sync_ai_issue_to_notion
    count = sync_ai_issue_to_notion(date_str, period, top10, outlook)
    logger.info(f"[AI이슈] {date_str} → Notion {count}건 완료")
    return count


# ──────────────────────────────────────────────
# CLI 진입점
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Notion DB 동기화")
    parser.add_argument(
        "--type", required=True,
        choices=["news", "stock", "ai-issue"],
        help="동기화 대상 유형"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="대상 날짜 (기본: 오늘, 형식: YYYY-MM-DD)"
    )
    args = parser.parse_args()

    logger.info(f"Notion 동기화 시작: type={args.type}, date={args.date}")

    if args.type == "news":
        count = sync_news(args.date)
        sys.exit(0 if count >= 0 else 1)

    elif args.type == "stock":
        ok = sync_stock(args.date)
        sys.exit(0 if ok else 1)

    elif args.type == "ai-issue":
        count = sync_ai_issue(args.date)
        sys.exit(0 if count >= 0 else 1)


if __name__ == "__main__":
    main()
