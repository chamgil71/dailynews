# core/stock_collector.py
"""
주식 시황 데이터 수집 모듈 (GitHub Actions 백업 경로).

yfinance 로 지수·환율·금리·유가·섹터 종목을 수집한다.
Claude Code 루틴 경로에서는 이 모듈 대신 MCP 도구(UsStockInfo)를 사용한다.

의존성: yfinance (requirements.txt 에 추가 필요)
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# yfinance 는 선택적 의존성 — import 실패 시 fallback dict 반환
try:
    import yfinance as yf
    _YF_AVAILABLE = True
except ImportError:
    _YF_AVAILABLE = False
    logger.warning("[stock_collector] yfinance 미설치 — pip install yfinance")

from config.stock_prompts import MARKET_TICKERS
from config.watchlist import get_sector_tickers_dict


def _fetch_ticker(ticker: str) -> dict:
    """단일 티커 현재가·등락률 조회. 오류 시 None 값 dict 반환."""
    if not _YF_AVAILABLE:
        return {"close": None, "change_pct": None, "prev_close": None}
    try:
        t    = yf.Ticker(ticker)
        info = t.fast_info
        close      = getattr(info, "last_price",      None)
        prev_close = getattr(info, "previous_close",  None)
        change_pct = None
        if close and prev_close and prev_close != 0:
            change_pct = round((close - prev_close) / prev_close * 100, 2)
        return {
            "close":      round(close,      2) if close      else None,
            "prev_close": round(prev_close, 2) if prev_close else None,
            "change_pct": change_pct,
        }
    except Exception as e:
        logger.warning(f"[stock_collector] {ticker} 조회 실패: {e}")
        return {"close": None, "change_pct": None, "prev_close": None}


def _fetch_us10y(ticker: str = "^TNX") -> dict:
    """10년물 금리 (단위 %). bp 변화 포함."""
    raw = _fetch_ticker(ticker)
    result = {"value": raw["close"], "change_bp": None}
    if raw["close"] and raw["prev_close"]:
        result["change_bp"] = round((raw["close"] - raw["prev_close"]) * 100, 1)
    return result


def collect_market_data() -> dict:
    """지수·환율·금리·유가 수집. 반환: market dict."""
    market: dict = {}

    # 일반 지수·환율·유가
    for key, ticker in MARKET_TICKERS.items():
        if key == "us10y":
            market[key] = _fetch_us10y(ticker)
        else:
            market[key] = _fetch_ticker(ticker)
        logger.info(f"[수집] {key}({ticker}): {market[key].get('close')}")

    return market


def collect_sectors() -> dict:
    """섹터 대표 종목 수집. watchlist.yaml 기반. 반환: {종목명: {close, change_pct}} dict."""
    sectors: dict = {}
    for name, ticker in get_sector_tickers_dict().items():
        sectors[name] = _fetch_ticker(ticker)
        logger.info(f"[수집] {name}({ticker}): {sectors[name].get('close')}")
    return sectors


def collect_news_ko(query: str = "코스피 오늘 증시 시황") -> list[dict]:
    """
    Naver News API로 국내 뉴스 수집.
    NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수 필요.
    미설정 시 빈 리스트 반환 (프로세스 중단 없음).
    """
    import os, requests, re, html
    client_id     = os.getenv("NAVER_CLIENT_ID", "")
    client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        logger.warning("[stock_collector] NAVER_CLIENT_ID/SECRET 미설정 — 뉴스 수집 건너뜀")
        return []
    try:
        resp = requests.get(
            "https://openapi.naver.com/v1/search/news.json",
            headers={
                "X-Naver-Client-Id":     client_id,
                "X-Naver-Client-Secret": client_secret,
            },
            params={"query": query, "display": 5, "sort": "date"},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        def clean_naver_title(raw_title: str) -> str:
            # 모든 HTML 태그 제거
            cleaned = re.sub(r'<[^>]+>', '', raw_title)
            # HTML 엔터티 (&amp;, &#039; 등) 완벽 복원
            return html.unescape(cleaned).strip()

        return [
            {
                "title":   clean_naver_title(item.get("title", "")),
                "url":     item.get("originallink") or item.get("link", ""),
                "source":  clean_naver_title(item.get("description", ""))[:80],
            }
            for item in items
        ]
    except Exception as e:
        logger.warning(f"[stock_collector] 뉴스 수집 실패: {e}")
        return []


def build_stock_data() -> dict:
    """
    전체 수집 통합 함수.
    scripts/stock_main.py 의 진입점에서 호출.

    반환 구조:
    {
        "market":           { kospi, kosdaq, usd_krw, sp500, nasdaq, dow, us10y, wti },
        "sectors":          { 삼성전자: {...}, ... },
        "news_ko":          [ {title, url, source}, ... ],
        "events":           [],   # 수동 입력 또는 향후 자동화
        "market_close_time": "YYYY-MM-DD 15:30 KST",
        "generated_at":     "YYYY-MM-DD HH:MM KST",
    }
    """
    logger.info("[stock_collector] 데이터 수집 시작")
    now = datetime.now()
    data = {
        "market":            collect_market_data(),
        "sectors":           collect_sectors(),
        "news_ko":           collect_news_ko("코스피 오늘 증시 시황"),
        "events":            [],   # 향후: 경제 캘린더 API 연동
        "market_close_time": now.strftime("%Y-%m-%d 15:30 KST"),
        "generated_at":      now.strftime("%Y-%m-%d %H:%M KST"),
    }
    logger.info(
        f"[stock_collector] 완료 — market {len(data['market'])}개, "
        f"sector {len(data['sectors'])}개, news {len(data['news_ko'])}건"
    )
    return data
