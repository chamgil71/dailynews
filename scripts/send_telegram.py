# scripts/send_telegram.py
"""
통합 텔레그램 발송 스크립트.
--type news|stock|ai-issue 로 채널 선택.
core/shared/telegram.py 가 실제 발송 담당.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("send_telegram")

KST_TODAY = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")


# ── news ──────────────────────────────────────────────────────────────────────
def _send_news(date_str: str, force: bool = False) -> None:
    from core.shared.telegram import send_telegram_cardnews

    json_path = Path(_ROOT) / "reports" / f"news_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[텔레그램/뉴스] JSON 파일 없음: {json_path}")
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[텔레그램/뉴스] JSON 파싱 에러: {e}")
        sys.exit(1)

    if not force and not data.get("analysis_ok", True):
        logger.warning("[텔레그램/뉴스] AI 분석 실패 플래그 감지 — 발송 건너뜀 (강제 발송: --force 사용)")
        return

    if force:
        logger.info("[텔레그램/뉴스] 강제 발송 모드 — analysis_ok 플래그 무시")
    ok = send_telegram_cardnews(data, date_str)
    logger.info(f"[텔레그램/뉴스] {'완료' if ok else '실패 또는 건너뜀'}")


# ── stock ─────────────────────────────────────────────────────────────────────
def _send_stock(date_str: str) -> None:
    from core.shared.telegram import send_stock_telegram
    from scripts.build_stock_site import parse_stock_md

    md_path = Path(_ROOT) / "reports" / "stock" / f"stock_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[텔레그램/주식] MD 파일 없음: {md_path}")
        sys.exit(1)

    try:
        data = parse_stock_md(str(md_path), date_str)
    except Exception as e:
        logger.error(f"[텔레그램/주식] MD 파싱 에러: {e}")
        sys.exit(1)

    ok = send_stock_telegram(data, date_str)
    logger.info(f"[텔레그램/주식] {'완료' if ok else '실패 또는 건너뜀'}")


# ── weekly-stock ─────────────────────────────────────────────────────────────
def _send_weekly_stock(date_str: str) -> None:
    from core.shared.telegram import send_weekly_stock_telegram
    from scripts.build_stock_site import parse_weekly_md

    md_path = Path(_ROOT) / "reports" / "stock" / f"weekly_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[텔레그램/주간주식] MD 파일 없음: {md_path}")
        sys.exit(1)

    try:
        data = parse_weekly_md(str(md_path), date_str)
    except Exception as e:
        logger.error(f"[텔레그램/주간주식] MD 파싱 에러: {e}")
        sys.exit(1)

    ok = send_weekly_stock_telegram(data, date_str)
    logger.info(f"[텔레그램/주간주식] {'완료' if ok else '실패 또는 건너뜀'}")


# ── ai-issue ──────────────────────────────────────────────────────────────────
def _send_ai_issue(date_str: str) -> None:
    from core.shared.telegram import send_ai_issue_telegram

    json_path = Path(_ROOT) / "reports" / "ai-issue" / f"ai_issue_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[텔레그램/AI이슈] JSON 파일 없음: {json_path}")
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[텔레그램/AI이슈] JSON 파싱 에러: {e}")
        sys.exit(1)

    if not data.get("top10"):
        logger.error("[텔레그램/AI이슈] top10 공란 — 불완전 보고서로 판단, 발송 건너뜀")
        sys.exit(1)

    ok = send_ai_issue_telegram(data, date_str)
    logger.info(f"[텔레그램/AI이슈] {'완료' if ok else '실패 또는 건너뜀'}")


# ── 진입점 ────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="통합 텔레그램 발송기")
    parser.add_argument("--type", choices=["news", "stock", "weekly-stock", "ai-issue"], required=True)
    parser.add_argument("--date", default=KST_TODAY, help="대상 날짜 (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="AI 분석 실패 플래그 무시하고 강제 발송 (news 전용)")
    args = parser.parse_args()

    logger.info(f"[텔레그램] type={args.type} date={args.date} force={args.force}")
    if args.type == "news":
        _send_news(args.date, force=args.force)
    else:
        {"stock": _send_stock, "weekly-stock": _send_weekly_stock, "ai-issue": _send_ai_issue}[args.type](args.date)


if __name__ == "__main__":
    main()
