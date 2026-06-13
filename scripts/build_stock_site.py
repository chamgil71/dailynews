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
    """'## 시장 온도계: 🔴/🟠/🟡/🟢/🔵 ...' 파싱."""
    m = re.search(r'## 시장 온도계[:\s]+([🔴🟠🟡🟢🔵])\s*(\S+)', raw)
    if m:
        emoji  = m.group(1)
        label  = m.group(2).strip()
        level  = {"🔴": "risk_off", "🟠": "rising", "🟡": "neutral",
                  "🟢": "risk_on",  "🔵": "recession"}.get(emoji, "neutral")
        return {"emoji": emoji, "label": label, "display": f"{emoji} {label}", "level": level}
    return {"emoji": "🟡", "label": "중립", "display": "🟡 중립", "level": "neutral"}


def _parse_market_table(raw: str) -> dict:
    """국내/글로벌 지수 테이블에서 숫자 추출 (v5 포맷 + 구 포맷 동시 지원)."""
    result = {}
    patterns = {
        "kospi":   r'\| 코스피 \| ([^\|]+?) \| ([^\|]+?) \|',
        "kosdaq":  r'\| 코스닥 \| ([^\|]+?) \| ([^\|]+?) \|',
        "usd_krw": r'\| 원/달러 \| ([^\|]+?) \| ([^\|]+?) \|',
        "sp500":   r'\| S&P 500 \| ([^\|]+?) \| ([^\|]+?) \|',
        "nasdaq":  r'\| 나스닥 \| ([^\|]+?) \| ([^\|]+?) \|',
        # v5: '| 미 10년물 |', 구: '| 미국 10년물 금리 |'
        "us10y":   r'\| 미(?:국 10년물 금리| 10년물) \| ([^\|]+?) \| ([^\|]+?) \|',
        # v5: '| 89.45 달러 |', 구: '| $86.64 |'
        "wti":     r'\| WTI 유가 \| \$?([0-9,.]+)(?:\s*달러)? \| ([^\|]+?) \|',
    }
    for key, pat in patterns.items():
        m = re.search(pat, raw)
        if m:
            close = m.group(1).strip().rstrip('원').strip()
            result[key] = {"close_str": close, "chg_str": m.group(2).strip()}
    return result


def _parse_keywords(raw: str) -> list[dict]:
    """핵심 키워드 TOP 5 파싱.
    - v6 포맷: ① 제목: 설명 (한 줄)
    - 구 포맷: **① [제목]** + 설명
    - v5 포맷: #태그1 #태그2 ...
    """
    keywords = []
    m_section = re.search(r'## (?:3\. )?핵심 키워드[^\n]*\n([\s\S]*?)(?=\n---|\n## |\Z)', raw)
    if not m_section:
        return keywords
    block = m_section.group(1).strip()

    # v6 포맷: ① 제목: 설명 (볼드 없음, 한 줄)
    v6_kws = re.findall(r'[①②③④⑤]\s+([^:\n]+):\s*(.+)', block)
    if v6_kws:
        for title, body in v6_kws:
            keywords.append({"title": title.strip(), "body": body.strip()})
        return keywords

    # 구 포맷: **① [제목]** + 본문
    old_kws = re.findall(r'\*\*[①②③④⑤]\s+(.+?)\*\*([\s\S]*?)(?=\*\*[①②③④⑤]|\Z)', block)
    if old_kws:
        for title, body in old_kws:
            keywords.append({"title": title.strip(), "body": body.strip()})
        return keywords

    # v5 포맷: #태그1 #태그2 ...
    hashtags = re.findall(r'#(\S+)', block)
    for tag in hashtags:
        keywords.append({"title": tag, "body": ""})
    return keywords


def _parse_summary(raw: str) -> str:
    """핵심 요약 3줄 추출."""
    m = re.search(r'## ■ 핵심 요약.*?\n([\s\S]*?)(?=\n---|\n## )', raw)
    return m.group(1).strip() if m else ""


def _parse_sectors(raw: str) -> list[dict]:
    """섹터 동향 테이블 파싱.
    v6: ### 2-1. 섹터 요약 (카드뉴스용) — 섹터당 1행, 9행
    구  : ## 2. 섹터 동향 — flat 단일 테이블
    반환: [{"sector": str, "name": str, "price": str, "change": str}, ...]
    """
    # v6: 2-1. 섹터 요약 서브섹션 우선
    m = re.search(
        r'### 2-1\. 섹터 요약[^\n]*\n([\s\S]*?)(?=###|\n---|\n## |\Z)', raw
    )
    if not m:
        # 구 포맷: ## 2. 섹터 동향 단일 테이블
        m = re.search(
            r'## 2\. 섹터 동향[^\n]*\n([\s\S]*?)(?=\n---|\n## |\Z)', raw
        )
    if not m:
        return []

    sectors: list[dict] = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p != ""]
        if len(parts) < 4:
            continue
        sector, name, price, change = parts[0], parts[1], parts[2], parts[3]
        if not sector or sector == "섹터":
            continue
        sectors.append({"sector": sector, "name": name, "price": price, "change": change})
    return sectors


# ── 주간 MD 파서 ──────────────────────────────────────────────────────────────

def _parse_week_range(raw: str) -> str:
    """'> 기간: ...' 에서 주간 범위 추출."""
    m = re.search(r'기간:\s*([^|\n]+?)(?:\s*\||\n)', raw)
    return m.group(1).strip() if m else ""


def _parse_weekly_summary(raw: str) -> str:
    """## ■ 주간 한줄 총평 파싱."""
    m = re.search(r'## ■ 주간 한줄 총평[^\n]*\n([\s\S]*?)(?=\n---|\n## )', raw)
    return m.group(1).strip() if m else ""


def _parse_weekly_temperature(raw: str) -> dict:
    """## 주간 온도계: 🟠 강세 파싱."""
    m = re.search(r'## 주간 온도계[:\s]+([🔴🟠🟡🟢🔵])\s*(\S+)', raw)
    if m:
        emoji = m.group(1)
        label = m.group(2).strip()
        level = {"🔴": "risk_off", "🟠": "rising", "🟡": "neutral",
                 "🟢": "risk_on",  "🔵": "recession"}.get(emoji, "neutral")
        return {"emoji": emoji, "label": label, "display": f"{emoji} {label}", "level": level}
    return {"emoji": "🟡", "label": "중립", "display": "🟡 중립", "level": "neutral"}


def _parse_weekly_indices(raw: str) -> list[dict]:
    """## 1. 주간 지수 성과 테이블 파싱 → [{"label","open","close","change"}, ...]"""
    m = re.search(r'## 1\. 주간 지수 성과[^\n]*\n([\s\S]*?)(?=\n---|\n## )', raw)
    if not m:
        return []
    rows = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p != ""]
        if len(parts) < 4:
            continue
        label, open_val, close_val, change = parts[0], parts[1], parts[2], parts[3]
        if not label or label in ("지수", "항목"):
            continue
        rows.append({"label": label, "open": open_val, "close": close_val, "change": change})
    return rows


def _parse_weekly_sectors(raw: str) -> list[dict]:
    """## 2. 섹터 주간 성과 (상위+하위) → [{"sector","name","price","change"}, ...]"""
    m = re.search(r'## 2\. 섹터 주간 성과[^\n]*\n([\s\S]*?)(?=\n---|\n## )', raw)
    if not m:
        return []
    sectors = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p != ""]
        if len(parts) < 3:
            continue
        sector, name, change = parts[0], parts[1], parts[2]
        if not sector or sector in ("섹터",):
            continue
        sectors.append({"sector": sector, "name": name, "price": "", "change": change})
    return sectors


def _parse_hot_themes(raw: str) -> list[dict]:
    """## 3. 이번 주 핫 테마 TOP 3 파싱 → [{"rank","title","description"}, ...]"""
    m = re.search(r'## 3\. 이번 주 핫 테마[^\n]*\n([\s\S]*?)(?=\n---|\n## |\Z)', raw)
    if not m:
        return []
    block = m.group(1)
    themes = []
    blocks = re.findall(
        r'### [①②③]\s*\[?([^\]\n]+)\]?\n([\s\S]*?)(?=### [①②③]|\Z)', block
    )
    for i, (title, body) in enumerate(blocks):
        themes.append({"rank": i + 1, "title": title.strip(), "description": body.strip()})
    return themes


def _parse_next_week_schedule(raw: str) -> list[dict]:
    """## 4. 차주 주요 일정 테이블 → [{"date","event","impact"}, ...]"""
    m = re.search(r'## 4\. 차주 주요 일정[^\n]*\n([\s\S]*?)(?=\n---|\n## |\Z)', raw)
    if not m:
        return []
    rows = []
    for line in m.group(1).split("\n"):
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p != ""]
        if len(parts) < 3:
            continue
        date_val, event, impact = parts[0], parts[1], parts[2]
        if not date_val or date_val in ("날짜",):
            continue
        rows.append({"date": date_val, "event": event, "impact": impact})
    return rows


def parse_weekly_md(md_path: str, date_str: str) -> dict:
    """weekly_*.md → 구조화 데이터. data.json 에 포함됨."""
    raw = Path(md_path).read_text(encoding="utf-8")
    return {
        "date":               date_str,
        "type":               "weekly",
        "week_range":         _parse_week_range(raw),
        "temperature":        _parse_weekly_temperature(raw),
        "market":             {},
        "summary":            _parse_weekly_summary(raw),
        "keywords":           [],
        "sectors":            _parse_weekly_sectors(raw),
        "weekly_indices":     _parse_weekly_indices(raw),
        "hot_themes":         _parse_hot_themes(raw),
        "next_week_schedule": _parse_next_week_schedule(raw),
    }


def _preprocess_raw_md(raw: str) -> str:
    """핵심 요약의 '제목 — 내용' 형식을 '제목 \n  - 내용'으로 변환."""
    return re.sub(
        r'^-\s+\*\*\[(.+?)\]\*\*\s+(?:—|-)\s+(.+)$',
        r'- **[\1]**\n  - \2',
        raw,
        flags=re.MULTILINE
    )


def _preprocess_display(raw: str) -> str:
    """HTML 렌더링용 추가 전처리.
    - 핵심 요약 각 줄 → - bullet (단락 분리)
    - 핵심 키워드 ① 제목: 설명 → - **[제목]** 설명 (제목 강조)
    """
    def _bulletize_summary(m):
        header = m.group(1)
        body = m.group(2)
        lines = [l for l in body.split('\n') if l.strip()]
        return header + '\n' + '\n'.join('- ' + l for l in lines) + '\n'
    raw = re.sub(
        r'(## ■ 핵심 요약[^\n]*\n)([\s\S]*?)(?=\n---|\n##\s)',
        _bulletize_summary,
        raw,
    )
    raw = re.sub(
        r'[①②③④⑤]\s+([^:\n]+?):\s*(.+)',
        lambda m: f'- **[{m.group(1).strip()}]** {m.group(2).strip()}',
        raw,
    )
    return raw


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
        "sectors":     _parse_sectors(raw),
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
    raw      = _preprocess_display(raw)
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


def build_stock_archive_ctx(pages: list[tuple[str, str, str]]) -> dict:
    """pages: [(date_str, html_path, "daily"|"weekly"), ...]"""
    items = [{"date": d, "display": _display_date(d), "type": t} for d, _, t in pages]
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

    daily_files  = sorted(glob.glob(f"{STOCK_REPORTS_DIR}/stock_*.md"),  reverse=True)
    weekly_files = sorted(glob.glob(f"{STOCK_REPORTS_DIR}/weekly_*.md"), reverse=True)
    # 날짜 기준 내림차순 통합 정렬
    all_files = sorted(
        daily_files + weekly_files,
        key=lambda p: re.sub(r'^(stock|weekly)_', '', Path(p).stem),
        reverse=True,
    )
    if not all_files:
        print("  reports/stock/ 에 MD 파일 없음")
        return

    pages:      list[tuple[str, str, str]] = []  # (date_str, html_path, type)
    stock_data: list[dict] = []
    latest_daily_md:   str | None  = None
    latest_daily_data: dict | None = None

    renderer = getattr(theme, "render_stock_report", None) or theme.render_report

    for md_path in all_files:
        stem      = Path(md_path).name
        is_weekly = stem.startswith("weekly_")
        if is_weekly:
            date_str = stem.replace("weekly_", "").replace(".md", "")
            data     = parse_weekly_md(md_path, date_str)
        else:
            date_str = stem.replace("stock_", "").replace(".md", "")
            data     = parse_stock_md(md_path, date_str)

        ctx  = build_stock_report_ctx(md_path, date_str, data)
        html = renderer(ctx)

        out_path = os.path.join(STOCK_PUBLISH_DIR, f"{date_str}.html")
        Path(out_path).write_text(html, encoding="utf-8")

        stock_json_path = os.path.join(STOCK_PUBLISH_DIR, f"{date_str}.json")
        Path(stock_json_path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        ptype = "weekly" if is_weekly else "daily"
        pages.append((date_str, out_path, ptype))
        stock_data.append(data)
        print(f"  + stock/{date_str}.html [{ptype}] + {date_str}.json")

        if not is_weekly and latest_daily_md is None:
            latest_daily_md   = md_path
            latest_daily_data = data

    # index.html = 최신 일일 리포트 (주간 제외)
    if latest_daily_md and latest_daily_data:
        index_ctx = build_stock_report_ctx(latest_daily_md, latest_daily_data["date"], latest_daily_data)
    else:
        index_ctx = build_stock_report_ctx(all_files[0], pages[0][0], stock_data[0])
    Path(STOCK_PUBLISH_DIR, "index.html").write_text(renderer(index_ctx), encoding="utf-8")
    print("  + stock/index.html")

    # archive.html
    archive_ctx   = build_stock_archive_ctx(pages)
    arch_renderer = getattr(theme, "render_stock_archive", None) or theme.render_archive
    Path(STOCK_PUBLISH_DIR, "archive.html").write_text(arch_renderer(archive_ctx), encoding="utf-8")
    print("  + stock/archive.html")

    # data.json
    Path(STOCK_PUBLISH_DIR, "data.json").write_text(
        json.dumps(stock_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  + stock/data.json ({len(stock_data)} reports)")
    print(f"\nDone: {len(pages)} stock reports -> {STOCK_PUBLISH_DIR}/")


if __name__ == "__main__":
    cli_theme = sys.argv[1] if len(sys.argv) > 1 else None
    build(cli_theme)
