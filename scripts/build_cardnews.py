"""
카드뉴스 HTML 생성기 — 3채널 지원

출력 경로:
  publish/cardnews/news/YYYY-MM-DD.html     + data.json
  publish/cardnews/ai-issue/YYYY-MM-DD.html + data.json
  publish/cardnews/stock/YYYY-MM-DD.html    + data.json

각 HTML은 ?card=N 파라미터로 특정 슬라이드만 표시 (Playwright 스크린샷용)

사용법:
  python scripts/build_cardnews.py                           # 뉴스 최신
  python scripts/build_cardnews.py --type ai-issue           # AI이슈 최신
  python scripts/build_cardnews.py --type stock              # 주식 최신
  python scripts/build_cardnews.py --type news --date 2026-06-04
  python scripts/build_cardnews.py --type news --all
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

PUBLISH   = Path(_ROOT, "publish")
CARDNEWS  = PUBLISH / "cardnews"
_THEMES_FILE = Path(_ROOT, "config", "cardnews_themes.json")
_CSS_FILE    = Path(_ROOT, "templates", "cardnews_card.css")


def _load_channel_cfg(channel: str) -> dict:
    cfg = json.loads(_THEMES_FILE.read_text(encoding="utf-8"))
    return cfg["channels"][channel]


def _render_css(accent: str, topbar: str) -> str:
    variables = f":root {{ --accent: {accent}; --topbar: {topbar}; }}"
    return variables + "\n" + _CSS_FILE.read_text(encoding="utf-8")


CATEGORY_LABELS = {
    "ai_ml": "AI·ML", "technology": "기술", "economy": "경제",
    "global_news": "글로벌", "korean_news": "국내",
    "korean_economy": "한국경제", "korean_tech": "한국기술",
    "security": "보안", "startup": "스타트업",
    "model": "모델", "service": "서비스", "research": "연구",
    "policy": "정책", "industry": "산업", "infra": "인프라",
    "investment": "투자",
}

ISSUE_COLORS = ["#f59e0b", "#818cf8", "#34d399"]
ISSUE_ICONS  = ["&#128293;", "&#128226;", "&#128161;"]  # 🔥📢💡
TREND_ICONS  = ["&#128202;", "&#127919;", "&#9889;"]    # 📊🎯⚡


# ── 공통 유틸 ─────────────────────────────────────────────────────────────────
def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        wd = ["월","화","수","목","금","토","일"][dt.weekday()]
        return f"{dt.year}년 {dt.month}월 {dt.day}일 ({wd})"
    except ValueError:
        return date_str


def _cat(cat: str) -> str:
    return CATEGORY_LABELS.get(cat, cat)


def _trunc(text: str, max_len: int) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


def _render_label(ch: dict) -> str:
    label   = ch.get("label", "")
    keyword = ch.get("keyword", "")
    accent  = ch.get("accent", "")
    if keyword and accent:
        colored = f'<span style="color:{accent}">{keyword}</span>'
        return label.replace(keyword, colored, 1)
    return label


def _chg_color(chg: str) -> str:
    if "▲" in chg or (chg.startswith("+") and "▼" not in chg):
        return "#34d399"
    if "▼" in chg or chg.startswith("-"):
        return "#f87171"
    return "#94a3b8"


def _stat_row(col1: str, col2: str, col3: str, *, col1_w: str = "130px") -> str:
    """3열 통계 행 (label | value | change) — 섹터·지수 공용."""
    return (
        f'<div class="stat-row">'
        f'<span class="stat-col1" style="width:{col1_w}">{col1}</span>'
        f'<span class="stat-col2">{col2}</span>'
        f'<span class="stat-col3" style="color:{_chg_color(col3)}">{col3}</span>'
        f'</div>'
    )


def _stat_section(icon: str, title: str, rows_html: str) -> str:
    """아이콘·제목 헤더 + 통계 행 묶음."""
    return (
        '<div class="trends-header">'
        f'<span class="trends-icon">{icon}</span>'
        f'<span class="trends-title">{title}</span>'
        '</div>'
        f'<div class="stat-body">{rows_html}</div>'
    )


# ── 공통 카드 HTML 래퍼 ───────────────────────────────────────────────────────
def _card(idx: int, total: int, content: str, date_disp: str,
          layout: str = "", site_tag: str = "ms-dailynews.vercel.app") -> str:
    dots = "".join(
        f'<span class="dot {"active" if i == idx else ""}"></span>'
        for i in range(total)
    )
    cls = f"card-inner{' layout-' + layout if layout else ''}"
    return f"""
<div class="card" id="card-{idx}">
  <div class="card-topbar"></div>
  <div class="{cls}">{content}</div>
  <div class="card-footer">
    <span class="site-tag">{site_tag}</span>
    <div class="dots">{dots}</div>
    <span class="date-tag">{date_disp}</span>
  </div>
</div>"""


def _html_wrapper(title: str, css: str, cards_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=1080">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>{css}</style>
</head><body>
{cards_html}
<script>
(function(){{
  const i=parseInt(new URLSearchParams(location.search).get('card')||'0');
  document.querySelectorAll('.card').forEach((c,j)=>c.classList.toggle('active',j===i));
}})();
</script>
</body></html>"""


# ── 뉴스 카드 빌더 ────────────────────────────────────────────────────────────
def _news_cover(issues: list[dict], date_str: str, total: int,
                accent: str, ch: dict) -> str:
    lines = ""
    for i, iss in enumerate(issues[:3]):
        lines += (
            f'<div class="cover-issue">'
            f'<span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>'
            f'<span class="cover-issue-text">{_trunc(iss.get("title",""), 34)}</span>'
            f'</div>'
        )
    content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{_render_label(ch)}</div>
      <div class="logo-sub">{ch['sublabel']}</div>
    </div>
  </div>
  <div class="cover-date">{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 핵심 이슈</div>
  <div class="cover-issues">{lines}</div>
  <div class="cover-tags">{ch['hashtags']}</div>"""
    return _card(0, total, content, _fmt_date(date_str))


def _news_issue(issue: dict, rank: int, date_str: str,
                idx: int, total: int) -> str:
    color = ISSUE_COLORS[rank - 1]
    icon  = ISSUE_ICONS[rank - 1]
    cat   = _cat(issue.get("category", ""))
    src   = issue.get("sources", [])
    url   = src[0].get("url", "") if src else ""
    link  = f"&nbsp;·&nbsp;<a href='{url}'>원문 보기 →</a>" if url else ""
    content = f"""
  <div class="issue-top" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">핵심 이슈 {rank}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-body">
    <div class="issue-title">{issue.get('title','')}</div>
    <div class="issue-divider" style="background:{color}"></div>
    <div class="issue-summary">{issue.get('summary','')}</div>
  </div>
  <div class="issue-bottom">&#128206; 출처 {len(src)}개{link}</div>"""
    return _card(idx, total, content, _fmt_date(date_str), layout="issue")


def _news_trends(trends: list[dict], date_str: str, idx: int, total: int) -> str:
    items = ""
    for i, t in enumerate(trends[:3]):
        items += (
            f'<div class="trend-item">'
            f'<div class="trend-header">'
            f'<span class="trend-icon">{TREND_ICONS[i]}</span>'
            f'<span class="trend-keyword">#{t.get("keyword","")}</span>'
            f'</div>'
            f'<div class="trend-desc">{_trunc(t.get("description",""), 80)}</div>'
            f'</div>'
        )
    content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주목할 트렌드 키워드</span>
  </div>
  <div class="trends-list">{items}</div>"""
    return _card(idx, total, content, _fmt_date(date_str), layout="trends")


def build_news_html(date_str: str, entry: dict) -> str | None:
    ko = entry.get("structured", {}).get("ko", {})
    if not ko.get("issues"):
        return None
    ch     = _load_channel_cfg("news")
    issues = ko["issues"][:3]
    trends = ko.get("trends", [])[:3]
    accent = ch["accent"]
    css    = _render_css(accent, ch["topbar"])
    total  = 1 + len(issues) + (1 if trends else 0)
    cards  = _news_cover(issues, date_str, total, accent, ch)
    for i, iss in enumerate(issues):
        cards += _news_issue(iss, i + 1, date_str, i + 1, total)
    if trends:
        cards += _news_trends(trends, date_str, 1 + len(issues), total)
    return _html_wrapper(f"AI 뉴스 카드뉴스 {date_str}", css, cards)


# ── AI이슈 카드 빌더 ──────────────────────────────────────────────────────────
def build_ai_issue_html(date_str: str, data: dict) -> str:
    ch     = _load_channel_cfg("ai-issue")
    top10  = data.get("top10", [])
    top3   = top10[:3]
    accent = ch["accent"]
    css    = _render_css(accent, ch["topbar"])
    period = data.get("period", date_str)
    extras = data.get("paper_picks", []) or data.get("weekly_tips", [])
    total  = 1 + len(top3) + (1 if extras else 0)

    lines = "".join(
        f'<div class="cover-issue">'
        f'<span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>'
        f'<span class="cover-issue-text">{_trunc(item.get("title",""), 34)}</span>'
        f'</div>'
        for i, item in enumerate(top3)
    )
    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{_render_label(ch)}</div>
      <div class="logo-sub">{period}</div>
    </div>
  </div>
  <div class="cover-date">{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">이번 주 TOP 이슈</div>
  <div class="cover-issues">{lines}</div>
  <div class="cover-tags">{ch['hashtags']}</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    for i, item in enumerate(top3):
        color = ISSUE_COLORS[i]
        icon  = ISSUE_ICONS[i]
        cat   = _cat(item.get("category", ""))
        srcs  = item.get("sources", [])
        url   = srcs[0].get("url", "") if srcs else ""
        link  = f"&nbsp;·&nbsp;<a href='{url}'>원문 →</a>" if url else ""
        content = f"""
  <div class="issue-top" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">TOP {item.get('rank', i+1)}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-body">
    <div class="issue-title">{item.get('title','')}</div>
    <div class="issue-divider" style="background:{color}"></div>
    <div class="issue-summary">{_trunc(item.get('summary',''), 120)}</div>
  </div>
  <div class="issue-bottom">&#128206; 출처 {len(srcs)}개{link}</div>"""
        cards += _card(i + 1, total, content, _fmt_date(date_str), layout="issue")

    if extras:
        items_html = "".join(
            f'<div class="trend-item">'
            f'<div class="trend-header">'
            f'<span class="trend-icon">{TREND_ICONS[j % 3]}</span>'
            f'<span class="trend-keyword">'
            f'{_trunc(ex if isinstance(ex, str) else ex.get("title", str(ex)), 30)}'
            f'</span>'
            f'</div></div>'
            for j, ex in enumerate(extras[:3])
        )
        extra_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128240;</span>
    <span class="trends-title">주목할 AI 연구·논문</span>
  </div>
  <div class="trends-list">{items_html}</div>"""
        cards += _card(1 + len(top3), total, extra_content,
                       _fmt_date(date_str), layout="trends")

    return _html_wrapper(f"AI이슈 카드뉴스 {date_str}", css, cards)


# ── 주식 카드 빌더 ────────────────────────────────────────────────────────────
def build_stock_html(date_str: str, data: dict) -> str:
    ch      = _load_channel_cfg("stock")
    accent  = ch["accent"]
    css     = _render_css(accent, ch["topbar"])
    temp_disp = data.get("temperature", {}).get("display", "")
    market  = data.get("market", {})
    summary_lines = [l.strip().lstrip("- ") for l in
                     data.get("summary", "").split("\n") if l.strip()][:3]
    keywords = data.get("keywords", [])[:4]
    sectors  = data.get("sectors", [])
    total   = 2 + (1 if keywords else 0) + (1 if sectors else 0)

    sum_html = ""
    for line in summary_lines:
        parts = line.split("—", 1)
        bold  = parts[0].strip() if len(parts) > 1 else ""
        rest  = parts[1].strip() if len(parts) > 1 else line
        if bold:
            sum_html += (
                f'<div class="cover-issue">'
                f'<div>'
                f'<div class="sum-title">{_trunc(bold, 30)}</div>'
                f'<div class="sum-body">{_trunc(rest, 60)}</div>'
                f'</div></div>'
            )
        else:
            sum_html += (
                f'<div class="cover-issue">'
                f'<span class="cover-issue-text">{_trunc(line, 60)}</span>'
                f'</div>'
            )

    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">&#128200;</div>
    <div>
      <div class="logo-main">{_render_label(ch)}</div>
      <div class="logo-sub">{ch['sublabel']}</div>
    </div>
  </div>
  <div class="cover-date cover-date-lg">{temp_disp}&nbsp;&nbsp;{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 시황 요약</div>
  <div class="cover-issues">{sum_html}</div>
  <div class="cover-tags">{ch['hashtags']}</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    def _mkt_row(key: str, label: str) -> str:
        info = market.get(key, {})
        if not info:
            return ""
        close = info.get("close_str", "")
        chg   = info.get("chg_str", "")
        return (
            f'<div class="trend-item" style="border-left-color:{accent}">'
            f'<div class="trend-header mkt-header">'
            f'<span class="trend-keyword mkt-keyword">{label}</span>'
            f'<span class="mkt-close">{close}</span>'
            f'</div>'
            f'<div class="trend-desc mkt-chg">{chg}</div>'
            f'</div>'
        )

    mkt_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주요 시장 지표</span>
  </div>
  <div class="trends-list">
    {_mkt_row('kospi',   '코스피')}
    {_mkt_row('kosdaq',  '코스닥')}
    {_mkt_row('usd_krw', 'USD/KRW')}
    {_mkt_row('wti',     'WTI')}
  </div>"""
    cards += _card(1, total, mkt_content, _fmt_date(date_str), layout="trends")

    kw_idx = 2
    if keywords:
        kw_items = "".join(
            f'<div class="trend-item">'
            f'<div class="trend-header">'
            f'<span class="trend-icon">{TREND_ICONS[j % 3]}</span>'
            f'<span class="trend-keyword">'
            f'{_trunc(kw.get("title","") if isinstance(kw, dict) else str(kw), 22)}'
            f'</span></div>'
            f'<div class="trend-desc">'
            f'{_trunc(kw.get("body","") if isinstance(kw, dict) else "", 80)}'
            f'</div></div>'
            for j, kw in enumerate(keywords[:3])
        )
        kw_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128269;</span>
    <span class="trends-title">핵심 키워드</span>
  </div>
  <div class="trends-list">{kw_items}</div>"""
        cards += _card(kw_idx, total, kw_content, _fmt_date(date_str), layout="trends")
        kw_idx += 1

    if sectors:
        rows = "".join(
            _stat_row(s.get("sector",""), s.get("name",""), s.get("change",""))
            for s in sectors[:9]
        )
        cards += _card(kw_idx, total,
                       _stat_section("&#128202;", "섹터 동향", rows),
                       _fmt_date(date_str))

    return _html_wrapper(f"주식 카드뉴스 {date_str}", css, cards)


# ── 주간 주식 카드 빌더 ──────────────────────────────────────────────────────
def build_weekly_stock_html(date_str: str, data: dict) -> str:
    ch         = _load_channel_cfg("stock")
    accent     = ch["accent"]
    css        = _render_css(accent, ch["topbar"])
    temp_disp  = data.get("temperature", {}).get("display", "")
    summary    = data.get("summary", "")
    week_range = data.get("week_range", "")
    hot_themes = data.get("hot_themes", [])[:3]
    total = 4

    theme_preview = "".join(
        f'<div class="cover-issue">'
        f'<span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>'
        f'<span class="cover-issue-text">{_trunc(t.get("title",""), 34)}</span>'
        f'</div>'
        for i, t in enumerate(hot_themes)
    )
    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">&#128197;</div>
    <div>
      <div class="logo-main">주간 시황 종합</div>
      <div class="logo-sub">{week_range or _fmt_date(date_str)}</div>
    </div>
  </div>
  <div class="cover-date">{temp_disp}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">주간 총평</div>
  <div class="cover-issues">
    <div class="cover-issue">
      <span class="cover-issue-text">{_trunc(summary, 100)}</span>
    </div>
    {theme_preview}
  </div>
  <div class="cover-tags">{ch['hashtags']}</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    idx_rows = "".join(
        _stat_row(r.get("label",""), r.get("close",""), r.get("change",""), col1_w="110px")
        for r in data.get("weekly_indices", [])[:6]
    )
    cards += _card(1, total,
                   _stat_section("&#128200;", "주간 지수 성과", idx_rows),
                   _fmt_date(date_str))

    theme_items = "".join(
        f'<div class="theme-item">'
        f'<div class="theme-header">'
        f'<span class="theme-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>'
        f'<span class="theme-title">{_trunc(t.get("title",""), 24)}</span>'
        f'</div>'
        f'<div class="theme-desc">'
        f'{_trunc((t.get("description","") or "").split(chr(10))[0].strip(), 70)}'
        f'</div></div>'
        for i, t in enumerate(hot_themes)
    )
    cards += _card(2, total,
                   _stat_section("&#128293;", "이번 주 핫 테마 TOP 3", theme_items),
                   _fmt_date(date_str))

    sched_rows = "".join(
        f'<div class="sched-row">'
        f'<span class="sched-date" style="color:{accent}">{r.get("date","")}</span>'
        f'<div class="sched-body">'
        f'<div class="sched-event">{_trunc(r.get("event",""), 28)}</div>'
        f'<div class="sched-impact">{_trunc(r.get("impact",""), 36)}</div>'
        f'</div></div>'
        for r in data.get("next_week_schedule", [])[:6]
    )
    cards += _card(3, total,
                   _stat_section("&#128197;", "차주 주요 일정", sched_rows),
                   _fmt_date(date_str))

    return _html_wrapper(f"주간 주식 시황 {date_str}", css, cards)


# ── 인덱스 업데이트 ───────────────────────────────────────────────────────────
def _update_index(type_dir: Path, channel: str,
                  extra_data: dict[str, dict] | None = None) -> None:
    # 기존 index 로드 — 이전 빌드의 extra 필드(summary 등) 보존
    index_path = type_dir / "data.json"
    existing: dict[str, dict] = {}
    if index_path.exists():
        try:
            for e in json.loads(index_path.read_text(encoding="utf-8")):
                existing[e["date"]] = e
        except Exception:
            pass

    index = []
    for html in sorted(type_dir.glob("[0-9][0-9][0-9][0-9]-??-??.html"), reverse=True):
        date_str = html.stem
        entry = {**existing.get(date_str, {})}
        entry.update({
            "date":    date_str,
            "display": _fmt_date(date_str),
            "type":    channel,
            "html":    f"cardnews/{channel}/{date_str}.html",
        })
        if extra_data and date_str in extra_data:
            entry.update(extra_data[date_str])
        index.append(entry)
    (type_dir / "data.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  + cardnews/{channel}/data.json ({len(index)}개)")


# ── 메인 빌드 함수 ────────────────────────────────────────────────────────────
def build_news(date_str: str | None = None, rebuild_all: bool = False) -> None:
    out_dir = CARDNEWS / "news"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = json.loads((PUBLISH / "news" / "data.json").read_text(encoding="utf-8"))
    if date_str:
        entries = [e for e in entries if e.get("date") == date_str]
    elif not rebuild_all:
        entries = [e for e in entries
                   if e.get("structured", {}).get("ko", {}).get("issues")][:1]

    # issue_titles를 data.json에 저장 → _build_caption() Threads 캡션에 활용
    all_news = json.loads((PUBLISH / "news" / "data.json").read_text(encoding="utf-8"))
    extra_data: dict[str, dict] = {}
    for e in all_news:
        d  = e.get("date", "")
        ko = e.get("structured", {}).get("ko", {})
        titles = [i.get("title", "") for i in ko.get("issues", [])[:3] if i.get("title")]
        if d and titles:
            extra_data[d] = {"issue_titles": titles}

    built = 0
    for e in entries:
        d = e.get("date", "")
        html = build_news_html(d, e)
        if not html:
            print(f"  skip {d}: structured 데이터 없음")
            continue
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        ko = e.get("structured", {}).get("ko", {})
        n  = 1 + len(ko.get("issues", [])[:3]) + (1 if ko.get("trends") else 0)
        print(f"  + cardnews/news/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "news", extra_data=extra_data)


def build_ai_issue(date_str: str | None = None, rebuild_all: bool = False) -> None:
    import glob as _glob
    out_dir = CARDNEWS / "ai-issue"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(_glob.glob(str(PUBLISH / "ai-issue" / "[0-9][0-9][0-9][0-9]-??-??.json")),
                   reverse=True)
    if date_str:
        files = [f for f in files if Path(f).stem == date_str]
    elif not rebuild_all:
        files = files[:1]

    # issue_titles를 data.json에 저장 → _build_caption() Threads 캡션에 활용
    extra_data: dict[str, dict] = {}
    for fp in _glob.glob(str(PUBLISH / "ai-issue" / "[0-9][0-9][0-9][0-9]-??-??.json")):
        d = Path(fp).stem
        try:
            data_all = json.loads(Path(fp).read_text(encoding="utf-8"))
            titles = [t.get("title", "") for t in data_all.get("top10", [])[:3] if t.get("title")]
            if titles:
                extra_data[d] = {"issue_titles": titles}
        except Exception:
            pass

    built = 0
    for fp in files:
        d    = Path(fp).stem
        data = json.loads(Path(fp).read_text(encoding="utf-8"))
        html = build_ai_issue_html(d, data)
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        n = 1 + min(3, len(data.get("top10", []))) + (1 if data.get("paper_picks") or data.get("weekly_tips") else 0)
        print(f"  + cardnews/ai-issue/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "ai-issue", extra_data=extra_data)


def build_stock(date_str: str | None = None, rebuild_all: bool = False) -> None:
    out_dir = CARDNEWS / "stock"
    out_dir.mkdir(parents=True, exist_ok=True)

    stock_path = PUBLISH / "stock" / "data.json"
    if not stock_path.exists():
        print("  stock data.json 없음")
        return

    all_entries = json.loads(stock_path.read_text(encoding="utf-8"))
    all_entries.sort(key=lambda x: x.get("date", ""), reverse=True)

    # 전체 엔트리의 summary/keywords/temperature를 cardnews data.json에 저장
    # (Threads 텍스트 캡션에 활용)
    extra_data: dict[str, dict] = {}
    for e in all_entries:
        d = e.get("date", "")
        if not d:
            continue
        kws = [{"title": k.get("title", ""), "body": k.get("body", "")}
               for k in e.get("keywords", []) if isinstance(k, dict)]
        extra_data[d] = {
            "summary":     e.get("summary", ""),
            "keywords":    kws[:5],
            "temperature": e.get("temperature", {}),
        }

    if date_str:
        entries = [e for e in all_entries if e.get("date") == date_str]
    elif not rebuild_all:
        entries = all_entries[:1]
    else:
        entries = all_entries

    built = 0
    for e in entries:
        d         = e.get("date", "")
        is_weekly = e.get("type") == "weekly"
        html      = build_weekly_stock_html(d, e) if is_weekly else build_stock_html(d, e)
        n         = 4 if is_weekly else 2 + (1 if e.get("keywords") else 0) + (1 if e.get("sectors") else 0)
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        print(f"  + cardnews/stock/{d}.html  ({n} cards){' [주간]' if is_weekly else ''}")
        built += 1

    if built:
        _update_index(out_dir, "stock", extra_data=extra_data)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="카드뉴스 HTML 빌드")
    parser.add_argument("--type",  choices=["news","ai-issue","stock","all"],
                        default="news", help="채널 (기본: news)")
    parser.add_argument("--date",  help="YYYY-MM-DD (미입력 시 최신)")
    parser.add_argument("--all",   action="store_true", help="전체 날짜 재빌드")
    args = parser.parse_args()

    channels = ["news","ai-issue","stock"] if args.type == "all" else [args.type]
    print(f"[build-cardnews] type={args.type}  date={args.date or '최신'}  all={args.all}")

    for ch in channels:
        if ch == "news":
            build_news(args.date, args.all)
        elif ch == "ai-issue":
            build_ai_issue(args.date, args.all)
        elif ch == "stock":
            build_stock(args.date, args.all)


if __name__ == "__main__":
    main()
