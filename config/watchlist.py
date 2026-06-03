# config/watchlist.py
"""watchlist.yaml 로더."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_YAML_PATH = Path(__file__).parent / "watchlist.yaml"


@lru_cache(maxsize=1)
def load_watchlist() -> dict[str, Any]:
    """watchlist.yaml 로드 후 캐시한다."""
    with _YAML_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_enabled_sectors() -> list[dict]:
    """enabled: true 인 섹터 리스트 반환."""
    data = load_watchlist()
    return [s for s in data.get("sectors", []) if s.get("enabled", True)]


def get_all_tickers() -> list[dict[str, str]]:
    """
    enabled 섹터의 모든 종목 flat list 반환.
    각 항목: {ticker, name, market, sector}
    """
    result: list[dict[str, str]] = []
    for sector in get_enabled_sectors():
        sector_name = sector.get("name", "")
        for stock in sector.get("stocks", []):
            result.append({
                "ticker": stock["ticker"],
                "name":   stock["name"],
                "market": stock.get("market", ""),
                "sector": sector_name,
            })
    return result


def get_sector_tickers_dict() -> dict[str, str]:
    """{종목명: ticker} 형태 반환 (SECTOR_TICKERS 대체)."""
    return {t["name"]: t["ticker"] for t in get_all_tickers()}
