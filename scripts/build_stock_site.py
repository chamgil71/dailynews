# scripts/build_stock_site.py
"""
주식 시황 MD → HTML 빌더.

reports/stock/stock_*.md → publish/stock/*.html
                          + publish/stock/index.html
                          + publish/stock/archive.html
                          + publish/stock/stock-data.json

실행: python scripts/build_stock_site.py
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import markdown2
from dotenv import load_dotenv
load_dotenv()

from config.settings import SITE_BASE_URL
from config.theme_config import SECTION_THEMES, SITE_THEME, SITE_TITLE, SUBSCRIBE_URL
from themes import load_theme

STOCK_REPORTS_DIR = "reports/stock"
STOCK_PUBLISH_DIR = "publish/stock"

os.makedirs(STOCK_PUBLISH_DIR, exist_ok=True)


# ── MD 파싱 ──────────────────────────────────────────────────────────────────

def _parse_temperature(raw: str) -> dict:
    """'## 시장 온도계: 🔴/🟡/🟢 ...' 파싱."""
    m = re.search(r'## 시장 온도계:\s*([🔴🟡🟢])\s*(\S+)', raw)
    if m:
        emoji  = m.group(1)
        label  = m.group(2).strip()
        level  = {"🔴": "risk_off", "🟡": "neutral", "🟢": "risk_on"}.get(emoji, "neutral")
        return {"emoji": emoji, "label": label, "display": f"{emoji} {label}", "level": level}
    return {"emoji": "🟡", "label": "중립", "display": "🟡 중립", "level": "neutral"}


def _parse_market_table(raw: str) -> dict:
    """국내/글로벌 지수 테이블에서 숫자 추출."""
    result = {}
    patterns = {
        "kospi":   r'\| 코스피 \| ([^\|]+) \| ([^\|]+) \|',
        "kosdaq":  r'\| 코스닥 \| ([^\|]+) \| ([^\|]+) \|',
        "usd_krw": r'\| 원/달러 \| ([^\|]+)원 \| ([^\|]+) \|',
        "sp500":   r'\| S&P 500 \| ([^\|]+) \| ([^\|]+) \|',
        "nasdaq":  r'\| 나스닥 \| ([^\|]+) \| ([^\|]+) \|',
        "us10y":   r'\| 미국 10년물 금리 \| ([^\|]+)% \| ([^\|]+)bp \|',
        "wti":     r'\| WTI 유가 \| \$([^\|]+) \| ([^\|]+) \|',
    }
    for key, pat in patterns.items():
        m = re.search(pat, raw)
        if m:
            result[key] = {"close_str": m.group(1).strip(), "chg_str": m.group(2).strip()}
    return result


def _parse_keywords(raw: str) -> list[dict]:
    """핵심 키워드 TOP 5 (① ② ③ ④ ⑤ 마커) 파싱."""
    keywords = []
    m_section = re.search(r'## 3\. 핵심 키워드 TOP 5\n([\s\S]*?)(?=\n## |\Z)', raw)
    if not m_section:
        return keywords
    block = m_section.group(1)
    for kw_m in re.finditer(r'\*\*[①②③④⑤]\s+(.+?)\*\*\n([\s\S]*?)(?=\*\*[①②③④⑤]|\Z)', block):
        title = kw_m.group(1).strip()
        body  = kw_m.group(2).strip()
        keywords.append({"title": title, "body": body})
    return keywords


def _parse_summary(raw: str) -> str:
    """핵심 요약 3줄 추출."""
    m = re.search(r'## ■ 핵심 요약.*?\n([\s\S]*?)(?=\n---|\n## )', raw)
    return m.group(1).strip() if m else ""


def _preprocess_raw_md(raw: str) -> str:
    """핵심 요약의 '제목 — 내용' 형식을 '제목 \n  - 내용'으로 변환."""
    return re.sub(
        r'^-\s+\*\*\[(.+?)\]\*\*\s+(?:—|-)\s+(.+)$',
        r'- **[\1]**\n  - \2',
        raw,
        flags=re.MULTILINE
    )


def parse_stock_md(md_path: str, date_str: str) -> dict:
    """
    stock MD 파일 → 구조화 데이터.
    build_stock_report_ctx() 와 stock-data.json 에 사용.
    """
    raw = Path(md_path).read_text(encoding="utf-8")
    raw = _preprocess_raw_md(raw)
    return {
        "date":        date_str,
        "temperature": _parse_temperature(raw),
        "market":      _parse_market_table(raw),
        "summary":     _parse_summary(raw),
        "keywords":    _parse_keywords(raw),
    }


# ── ctx 빌더 ─────────────────────────────────────────────────────────────────

def _display_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    except ValueError:
        return date_str


def build_stock_report_ctx(md_path: str, date_str: str, data: dict) -> dict:
    raw      = Path(md_path).read_text(encoding="utf-8")
    raw      = _preprocess_raw_md(raw)
    md_html  = markdown2.markdown(
        raw,
        extras=["tables", "fenced-code-blocks", "strike", "cuddled-lists", "header-ids"],
    )
    # 이메일용 축약 (핵심 요약 + 키워드 섹션만)
    email_parts = re.findall(
        r'(?:## ■ 핵심 요약|## 3\. 핵심 키워드|## 6\. 장기투자|## 시장 온도계)([\s\S]*?)(?=\n---|\n## |\Z)',
        raw,
    )
    email_md = "\n\n".join(email_parts).strip() or raw
    email_html = markdown2.markdown(email_md, extras=["tables", "fenced-code-blocks"])

    return {
        "display_date":     _display_date(date_str),
        "date_str":         date_str,
        "md_html":          md_html,
        "email_html":       email_html,
        "site_title":       SITE_TITLE,
        "now":              datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data":             data,
        "items":            [],
        "site_url":         SITE_BASE_URL or "https://chamgil71.github.io/dailynews/",
        "subscribe_url":    SUBSCRIBE_URL,
        "unsubscribe_url":  "",
    }


def build_stock_archive_ctx(pages: list[tuple[str, str]]) -> dict:
    items = [{"date": d, "display": _display_date(d)} for d, _ in pages]
    return {
        "display_date":     "주식 시황 전체 목록",
        "date_str":         "",
        "md_html":          "",
        "email_html":       "",
        "site_title":       SITE_TITLE,
        "now":              datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data":             {"temperature": {}, "market": {}, "keywords": []},
        "items":            items,
        "site_url":         SITE_BASE_URL or "",
        "subscribe_url":    SUBSCRIBE_URL,
        "unsubscribe_url":  "",
    }


# ── 메인 빌드 ─────────────────────────────────────────────────────────────────

def build(theme_name: str | None = None) -> None:
    active_theme = theme_name or SECTION_THEMES.get("stock", SITE_THEME)
    theme = load_theme(active_theme)
    print(f"[stock-build] theme={active_theme}")

    md_files = sorted(glob.glob(f"{STOCK_REPORTS_DIR}/stock_*.md"), reverse=True)
    if not md_files:
        print(f"  reports/stock/ 에 MD 파일 없음")
        return

    pages:       list[tuple[str, str]] = []
    stock_data:  list[dict]            = []

    for md_path in md_files:
        date_str = Path(md_path).name.replace("stock_", "").replace(".md", "")
        data     = parse_stock_md(md_path, date_str)
        ctx      = build_stock_report_ctx(md_path, date_str, data)

        # 테마에 render_stock_report 가 있으면 사용, 없으면 render_report fallback
        renderer = getattr(theme, "render_stock_report", None) or theme.render_report
        html     = renderer(ctx)

        out_path = os.path.join(STOCK_PUBLISH_DIR, f"{date_str}.html")
        Path(out_path).write_text(html, encoding="utf-8")
        pages.append((date_str, out_path))
        stock_data.append(data)
        print(f"  + stock/{date_str}.html")

    # index.html = 최신 리포트
    latest_ctx = build_stock_report_ctx(md_files[0], pages[0][0], stock_data[0])
    renderer   = getattr(theme, "render_stock_report", None) or theme.render_report
    Path(STOCK_PUBLISH_DIR, "index.html").write_text(
        renderer(latest_ctx), encoding="utf-8"
    )
    print("  + stock/index.html")

    # archive.html
    archive_ctx = build_stock_archive_ctx(pages)
    arch_renderer = getattr(theme, "render_stock_archive", None) or theme.render_archive
    Path(STOCK_PUBLISH_DIR, "archive.html").write_text(
        arch_renderer(archive_ctx), encoding="utf-8"
    )
    print("  + stock/archive.html")

    # stock-data.json
    Path(STOCK_PUBLISH_DIR, "stock-data.json").write_text(
        json.dumps(stock_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  + stock/stock-data.json ({len(stock_data)} reports)")
    print(f"\nDone: {len(pages)} stock reports -> {STOCK_PUBLISH_DIR}/")


if __name__ == "__main__":
    cli_theme = sys.argv[1] if len(sys.argv) > 1 else None
    build(cli_theme)
