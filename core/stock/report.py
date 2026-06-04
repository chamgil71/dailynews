# core/stock_report.py
"""
주식 시황 MD 리포트 생성 모듈.
templates/stock_report.md (Jinja2) 에 데이터를 주입해 MD 파일을 생성·저장한다.

경로: reports/stock/stock_YYYY-MM-DD.md
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, BaseLoader

logger = logging.getLogger(__name__)

STOCK_REPORTS_DIR = "reports/stock"
STOCK_TEMPLATE    = "templates/stock_report.md"


def _fmt(val: float | None, decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
    """숫자 포맷. None → 'N/A'."""
    if val is None:
        return "N/A"
    s = f"{val:,.{decimals}f}"
    return f"{prefix}{s}{suffix}"


def _chg(val: float | None, decimals: int = 2) -> str:
    """등락률 포맷. 양수에 + 부호."""
    if val is None:
        return "N/A"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.{decimals}f}"


def _build_sectors_table(sectors: list[dict]) -> str:
    """섹터 분석 테이블 MD 생성 (4열: 섹터, 대표종목, 방향, 핵심포인트)."""
    if not sectors:
        return "_데이터 없음_"
    lines = [
        "| 섹터 | 대표종목 | 방향 | 핵심 포인트 |",
        "|------|---------|:----:|------------|",
    ]
    for s in sectors:
        lines.append(
            f"| {s.get('name','')} | {s.get('symbol','')} "
            f"| {s.get('direction','')} | {s.get('point','')} |"
        )
    return "\n".join(lines)


def _build_events_table(events: list[dict]) -> str:
    """이벤트 테이블 MD 생성."""
    if not events:
        return "_이벤트 데이터 없음_"
    lines = [
        "| 날짜 | 이벤트 | 중요도 |",
        "|------|--------|:------:|",
    ]
    for e in events:
        lines.append(f"| {e.get('date','')} | {e.get('name','')} | {e.get('importance','★★')} |")
    return "\n".join(lines)


def generate(stock_data: dict, analysis: dict) -> str:
    """
    stock_data : core/stock_collector.build_stock_data() 반환값
    analysis   : core/stock_analyzer.analyze_stock() 반환값
    반환       : 완성된 MD 문자열
    """
    template_path = Path(STOCK_TEMPLATE)
    raw = template_path.read_text(encoding="utf-8")

    env = Environment(loader=BaseLoader())
    tpl = env.from_string(raw)

    m   = stock_data.get("market", {})
    now = datetime.now()

    # 보고서 날짜 = 데이터 기준 거래일 (실행 날짜가 아님)
    trading_date_str = stock_data.get("trading_date", now.strftime("%Y-%m-%d"))
    try:
        trading_dt = datetime.strptime(trading_date_str, "%Y-%m-%d")
    except ValueError:
        trading_dt = now
    _wd = ["월","화","수","목","금","토","일"][trading_dt.weekday()]
    report_date = f"{trading_date_str} ({_wd})"

    # 온도계 표시값 조립
    temp_raw     = analysis.get("temperature", "중립").strip()
    temp_emoji   = {"리스크오프": "🔴", "중립": "🟡", "리스크온": "🟢"}.get(temp_raw, "🟡")
    temp_display = f"{temp_emoji} {temp_raw}"

    return tpl.render(
        # 날짜/메타
        date              = report_date,
        generated_at      = now.strftime("%Y-%m-%d %H:%M KST"),
        market_close_time = stock_data.get("market_close_time", now.strftime("%Y-%m-%d 15:30 KST")),

        # 핵심 요약 (AI)
        summary           = analysis.get("summary", ""),

        # 국내 지수
        kospi_close  = _fmt(m.get("kospi",  {}).get("close")),
        kospi_chg    = _chg(m.get("kospi",  {}).get("change_pct")),
        kosdaq_close = _fmt(m.get("kosdaq", {}).get("close")),
        kosdaq_chg   = _chg(m.get("kosdaq", {}).get("change_pct")),
        usd_krw_close= _fmt(m.get("usd_krw",{}).get("close"), decimals=1),
        usd_krw_chg  = _chg(m.get("usd_krw",{}).get("change_pct")),

        # 국내 이슈 (AI)
        domestic_issues = analysis.get("domestic_issues", ""),

        # 글로벌 지수
        sp500_close  = _fmt(m.get("sp500",  {}).get("close")),
        sp500_chg    = _chg(m.get("sp500",  {}).get("change_pct")),
        nasdaq_close = _fmt(m.get("nasdaq", {}).get("close")),
        nasdaq_chg   = _chg(m.get("nasdaq", {}).get("change_pct")),
        dow_close    = _fmt(m.get("dow",    {}).get("close")),
        dow_chg      = _chg(m.get("dow",    {}).get("change_pct")),
        us10y_val    = _fmt(m.get("us10y",  {}).get("value"), decimals=3),
        us10y_bp     = _fmt(m.get("us10y",  {}).get("change_bp"), decimals=1),
        wti_close    = _fmt(m.get("wti",    {}).get("close"), decimals=2),
        wti_chg      = _chg(m.get("wti",    {}).get("change_pct")),

        # 글로벌 매크로 (AI)
        global_macro = analysis.get("global_macro", ""),

        # 핵심 키워드 TOP 5 (AI, ① ② ③ ④ ⑤ 포함 블록)
        keywords     = analysis.get("keywords", ""),

        # 섹터 테이블 (KR/US 분리)
        sectors_kr_table = _build_sectors_table([
            s for s in analysis.get("sectors", []) if s.get("market") != "US"
        ]),
        sectors_us_table = _build_sectors_table([
            s for s in analysis.get("sectors", []) if s.get("market") == "US"
        ]),

        # 이벤트 테이블
        events_table  = _build_events_table(stock_data.get("events", [])),

        # 장기투자 코멘트 (AI)
        lt_comment        = analysis.get("lt_comment", ""),

        # 시장 온도계 (AI)
        temperature_display = temp_display,
        temperature_reason  = analysis.get("temperature_reason", ""),
    )


def save(md_content: str, date_str: str | None = None) -> str:
    """MD 파일 저장. 저장 경로 반환."""
    os.makedirs(STOCK_REPORTS_DIR, exist_ok=True)
    tag      = date_str or datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(STOCK_REPORTS_DIR, f"stock_{tag}.md")
    Path(filepath).write_text(md_content, encoding="utf-8")
    logger.info(f"[주식 리포트 저장] {filepath}")
    return filepath
