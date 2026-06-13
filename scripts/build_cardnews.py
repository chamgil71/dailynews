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
    """CSS 커스텀 프로퍼티로 채널 색상을 주입. CSS 파일 자체는 순수 CSS."""
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
        lines += f"""
    <div class="cover-issue">
      <span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>
      <span class="cover-issue-text">{_trunc(iss.get('title',''), 34)}</span>
    </div>"""
    content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{ch['label']}</div>
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
        items += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[i]}</span>
        <span class="trend-keyword">#{t.get('keyword','')}</span>
      </div>
      <div class="trend-desc">{_trunc(t.get('description',''), 80)}</div>
    </div>"""
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

    lines = ""
    for i, item in enumerate(top3):
        lines += f"""
    <div class="cover-issue">
      <span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>
      <span class="cover-issue-text">{_trunc(item.get('title',''), 34)}</span>
    </div>"""
    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{ch['label']}</div>
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
        items_html = ""
        for j, ex in enumerate(extras[:3]):
            tip = ex if isinstance(ex, str) else ex.get("title", str(ex))
            items_html += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[j % 3]}</span>
        <span class="trend-keyword">{_trunc(tip, 30)}</span>
      </div>
    </div>"""
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
def _stock_sectors_card(sectors: list[dict], date_str: str, idx: int, total: int) -> str:
    items = ""
    for s in sectors[:9]:
        chg = s.get("change", "")
        if "▲" in chg or (chg.startswith("+") and "▼" not in chg):
            color = "#34d399"
        elif "▼" in chg or chg.startswith("-"):
            color = "#f87171"
        else:
            color = "#94a3b8"
        items += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:9px 0;border-bottom:1px solid #334155">'
            f'<span style="font-size:21px;color:#94a3b8;width:130px;flex-shrink:0">{s.get("sector","")}</span>'
            f'<span style="font-size:21px;color:#f1f5f9;font-weight:500;flex:1">{s.get("name","")}</span>'
            f'<span style="font-size:21px;color:{color};font-weight:700;white-space:nowrap">{chg}</span>'
            f'</div>'
        )
    content = (
        '<div class="trends-header">'
        '<span class="trends-icon">&#128202;</span>'
        '<span class="trends-title">섹터 동향</span>'
        '</div>'
        f'<div style="padding:0 4px">{items}</div>'
    )
    return _card(idx, total, content, _fmt_date(date_str))


def build_stock_html(date_str: str, data: dict) -> str:
    ch      = _load_channel_cfg("stock")
    accent  = ch["accent"]
    css     = _render_css(accent, ch["topbar"])
    temp    = data.get("temperature", {})
    temp_disp = temp.get("display", "")
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
            sum_html += f"""
    <div class="cover-issue">
      <div>
        <div style="font-size:28px;font-weight:700;color:#f1f5f9;margin-bottom:6px">{_trunc(bold,30)}</div>
        <div style="font-size:25px;color:#94a3b8;line-height:1.5">{_trunc(rest,60)}</div>
      </div>
    </div>"""
        else:
            sum_html += f"""
    <div class="cover-issue">
      <span class="cover-issue-text">{_trunc(line, 60)}</span>
    </div>"""

    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">&#128200;</div>
    <div>
      <div class="logo-main">{ch['label']}</div>
      <div class="logo-sub">{ch['sublabel']}</div>
    </div>
  </div>
  <div class="cover-date" style="font-size:36px">{temp_disp}&nbsp;&nbsp;{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 시황 요약</div>
  <div class="cover-issues">{sum_html}</div>
  <div class="cover-tags">{ch['hashtags']}</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    def _idx(key: str, label: str) -> str:
        info = market.get(key, {})
        if not info:
            return ""
        close = info.get("close_str", "")
        chg   = info.get("chg_str", "")
        return f"""
    <div class="trend-item" style="border-left-color:{accent}">
      <div class="trend-header" style="margin-bottom:8px">
        <span class="trend-keyword" style="font-size:28px">{label}</span>
        <span style="font-size:26px;color:#f8fafc;font-weight:700;margin-left:auto">{close}</span>
      </div>
      <div class="trend-desc" style="font-size:24px">{chg}</div>
    </div>"""

    mkt_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주요 시장 지표</span>
  </div>
  <div class="trends-list">
    {_idx('kospi',   '코스피')}
    {_idx('kosdaq',  '코스닥')}
    {_idx('usd_krw', 'USD/KRW')}
    {_idx('wti',     'WTI')}
  </div>"""
    cards += _card(1, total, mkt_content, _fmt_date(date_str), layout="trends")

    kw_idx = 2
    if keywords:
        kw_items = ""
        for j, kw in enumerate(keywords[:3]):
            title = kw.get("title", "") if isinstance(kw, dict) else str(kw)
            body  = kw.get("body",  "") if isinstance(kw, dict) else ""
            kw_items += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[j % 3]}</span>
        <span class="trend-keyword">{_trunc(title, 22)}</span>
      </div>
      <div class="trend-desc">{_trunc(body, 80)}</div>
    </div>"""
        kw_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128269;</span>
    <span class="trends-title">핵심 키워드</span>
  </div>
  <div class="trends-list">{kw_items}</div>"""
        cards += _card(kw_idx, total, kw_content, _fmt_date(date_str), layout="trends")
        kw_idx += 1

    if sectors:
        cards += _stock_sectors_card(sectors, date_str, kw_idx, total)

    return _html_wrapper(f"주식 카드뉴스 {date_str}", css, cards)


# ── 인덱스 업데이트 ───────────────────────────────────────────────────────────
def _update_index(type_dir: Path, channel: str) -> None:
    index = []
    for html in sorted(type_dir.glob("[0-9][0-9][0-9][0-9]-??-??.html"), reverse=True):
        date_str = html.stem
        index.append({
            "date":    date_str,
            "display": _fmt_date(date_str),
            "type":    channel,
            "html":    f"cardnews/{channel}/{date_str}.html",
        })
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
        _update_index(out_dir, "news")


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
        _update_index(out_dir, "ai-issue")


def build_stock(date_str: str | None = None, rebuild_all: bool = False) -> None:
    out_dir = CARDNEWS / "stock"
    out_dir.mkdir(parents=True, exist_ok=True)

    stock_path = PUBLISH / "stock" / "data.json"
    if not stock_path.exists():
        print("  stock data.json 없음")
        return

    entries = json.loads(stock_path.read_text(encoding="utf-8"))
    entries.sort(key=lambda x: x.get("date", ""), reverse=True)

    if date_str:
        entries = [e for e in entries if e.get("date") == date_str]
    elif not rebuild_all:
        entries = entries[:1]

    built = 0
    for e in entries:
        d    = e.get("date", "")
        html = build_stock_html(d, e)
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        n = 2 + (1 if e.get("keywords") else 0) + (1 if e.get("sectors") else 0)
        print(f"  + cardnews/stock/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "stock")


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
