# scripts/update_history.py
"""
티커별 일별 종가 누적 이력 관리.
reports/history/{ticker}.md (MD 테이블, 최대 365행) 에 저장.

실행:
  python scripts/update_history.py              # 오늘 날짜, yfinance 수집
  python scripts/update_history.py --date 2026-05-18
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
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
logger = logging.getLogger(__name__)

_HISTORY_DIR = Path(__file__).parent.parent / "reports" / "history"
_MAX_ROWS = 365


def _safe_name(ticker: str) -> str:
    return ticker.replace("/", "_").replace("^", "")


def update_ticker_md(
    ticker: str,
    name: str,
    market: str,
    sector: str,
    entry: dict,
) -> None:
    """
    entry: {"date": "2026-05-18", "price": 135.72, "change_pct": 3.30}
    기존 파일에서 같은 날짜 행은 덮어쓰고, 365행 초과분은 오래된 것부터 제거.
    """
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = _HISTORY_DIR / f"{_safe_name(ticker)}.md"

    header     = f"# {ticker} — {name} ({market} · {sector})\n\n"
    tbl_header = "| 날짜 | 종가 | 등락률 | 메모 |\n|------|-----:|-------:|------|\n"

    rows: list[str] = []
    if path.exists():
        rows = [
            line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("| 20")
        ]

    today  = entry["date"]
    price  = entry.get("price")  or 0.0
    chg    = entry.get("change_pct") or 0.0
    new_row = f"| {today} | {price:,.2f} | {chg:+.2f}% | |"

    rows = [r for r in rows if not r.startswith(f"| {today}")]
    rows.append(new_row)
    rows = sorted(rows)[-_MAX_ROWS:]

    path.write_text(header + tbl_header + "\n".join(rows) + "\n", encoding="utf-8")
    logger.info(f"  {ticker}: {len(rows)}일치 → {path.name}")


def run(date_str: str | None = None) -> int:
    """watchlist.yaml 기반 전체 티커 이력 업데이트. 갱신된 티커 수 반환."""
    from config.watchlist import get_all_tickers
    from core.stock_collector import _fetch_ticker

    today   = date_str or datetime.now().strftime("%Y-%m-%d")
    tickers = get_all_tickers()
    logger.info(f"[update_history] {today} — {len(tickers)}개 티커 처리 시작")

    ok_count = 0
    for t in tickers:
        raw = _fetch_ticker(t["ticker"])
        if raw["close"] is None:
            logger.warning(f"  [skip] {t['ticker']}: 데이터 없음")
            continue
        update_ticker_md(
            ticker = t["ticker"],
            name   = t["name"],
            market = t["market"],
            sector = t["sector"],
            entry  = {
                "date":       today,
                "price":      raw["close"],
                "change_pct": raw["change_pct"] or 0.0,
            },
        )
        ok_count += 1

    logger.info(f"[update_history] 완료 — {ok_count}/{len(tickers)}개 갱신")
    return ok_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="티커 이력 업데이트")
    parser.add_argument("--date", default=None, help="날짜 (YYYY-MM-DD, 기본: 오늘)")
    args = parser.parse_args()
    run(args.date)
