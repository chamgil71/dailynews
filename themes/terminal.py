# themes/terminal.py
"""Terminal Dark 테마 — Bloomberg 터미널 스타일, 다크 모노스페이스.

[커스텀 레이아웃 테마] base.py 미사용. render_*() 함수가 Python f-string으로 HTML 직접 생성.
레이아웃·색상 모두 이 파일에서 수정.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.theme_config import FOOTER_CONFIG

TOKENS = {
    "meta": {
        "name":     "terminal",
        "label":    "Terminal Dark",
        "font_cdn": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap",
        "font_family": "'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace",
    },
    "colors": {
        "bg":     "#0a0d12",
        "card":   "#11161e",
        "text":   "#e8eef5",
        "muted":  "#a8b3c2",
        "accent": "#f5a524",
        "green":  "#2cb67d",
        "red":    "#e5484d",
    },
    "typography": {
        "font_sans": "'JetBrains Mono', 'IBM Plex Mono', monospace",
        "leading":   1.55,
    },
}

_FONTS = """
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
"""

_CSS = """
  :root {
    --bg:#0a0d12; --panel:#11161e; --panel-2:#161c25;
    --line:#1f2733; --line-soft:#182030;
    --ink:#e8eef5; --ink-soft:#a8b3c2; --ink-mute:#5a6675;
    --amber:#f5a524; --green:#2cb67d; --red:#e5484d;
  }
  *,*::before,*::after { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
    font-family:'JetBrains Mono','IBM Plex Mono',ui-monospace,monospace;
    font-size:13px; line-height:1.55; }

  .topbar { display:flex; align-items:center; background:var(--panel-2);
    border-bottom:1px solid var(--line); padding:0 16px; font-size:11px;
    letter-spacing:.04em; color:var(--ink-soft); height:34px; }
  .topbar .lhs, .topbar .rhs { display:flex; align-items:center; gap:14px; }
  .topbar .rhs { margin-left:auto; }
  .logo { display:flex; align-items:center; gap:8px; color:var(--amber);
    font-weight:700; letter-spacing:.12em; }
  .logo-box { width:16px; height:16px; border:1px solid var(--amber);
    color:var(--amber); display:grid; place-items:center; font-size:9px; font-weight:700; }
  .nav-tab { padding:0 10px; color:var(--ink-mute); height:34px;
    display:flex; align-items:center; text-decoration:none;
    margin-top:-0px; border-bottom:2px solid transparent; }
  .nav-tab.on { color:var(--amber); border-bottom-color:var(--amber);
    background:linear-gradient(180deg,transparent 60%,rgba(245,165,36,.06)); }
  .live { display:inline-flex; gap:6px; align-items:center;
    color:var(--green); font-weight:600; }
  .live::before { content:''; width:6px; height:6px; background:var(--green);
    border-radius:50%; box-shadow:0 0 0 3px rgba(44,182,125,.18);
    animation:pulse 2s ease-in-out infinite; }
  @keyframes pulse { 50% { opacity:.4 } }

  .wrap { padding:18px 22px; max-width:1200px; margin:0 auto; }

  .main-head { display:flex; justify-content:space-between; align-items:flex-end;
    border-bottom:1px solid var(--line); padding-bottom:14px; margin-bottom:18px; }
  .main-head h1 { font-size:18px; font-weight:700; margin:0; color:var(--ink); }
  .main-head h1 .gt { color:var(--amber); }
  .main-head .meta { font-size:11px; color:var(--ink-mute); text-align:right; line-height:1.7; }
  .main-head .ok { color:var(--green); }

  .statgrid { display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
    background:var(--line); border:1px solid var(--line); margin-bottom:18px; }
  .statgrid > div { background:var(--panel); padding:12px 14px; }
  .statgrid .l { font-size:10px; color:var(--ink-mute); letter-spacing:.12em;
    text-transform:uppercase; margin-bottom:4px; }
  .statgrid .n { font-size:22px; color:var(--ink); font-weight:700;
    font-feature-settings:'tnum'; letter-spacing:-.02em; }
  .statgrid .n.amber { color:var(--amber); }
  .statgrid .n.green { color:var(--green); }

  .prose { background:var(--panel); border:1px solid var(--line); padding:18px 22px; }
  .prose h1 { display:none; }
  .prose h2 { font-size:13px; color:var(--amber); font-weight:700;
    margin:24px 0 12px; padding:7px 12px; background:var(--panel-2);
    border-left:2px solid var(--amber); letter-spacing:.1em; }
  .prose h3 { font-size:12px; color:var(--ink); font-weight:600;
    margin:18px 0 8px; letter-spacing:.06em; }
  .prose h3::before { content:'## '; color:var(--ink-mute); }
  .prose p { color:var(--ink-soft); margin:0 0 10px; font-size:12.5px; line-height:1.65; }
  .prose a { color:var(--amber); text-decoration:none; }
  .prose a:hover { text-decoration:underline; }
  .prose strong { color:var(--ink); }
  .prose ul, .prose ol { padding-left:0; list-style:none; margin:0 0 14px; }
  .prose li { padding:5px 0 5px 18px; position:relative;
    border-bottom:1px solid var(--line-soft); color:var(--ink-soft); font-size:12px; }
  .prose li::before { content:'>'; position:absolute; left:0; top:5px;
    color:var(--amber); font-weight:700; }
  .prose li:last-child { border-bottom:none; }
  .prose blockquote { background:var(--panel-2); border-left:2px solid var(--amber);
    padding:8px 14px; margin:12px 0; color:var(--ink-mute); font-size:11px; }
  .prose blockquote p { margin:0; color:var(--ink-mute); }
  .prose hr { border:none; border-top:1px dashed var(--line); margin:20px 0; }
  .prose code { background:var(--bg); color:var(--amber); padding:2px 6px;
    border:1px solid var(--line); font-size:.88em; }

  /* 뉴스 목록 접기/펼치기 */
  .news-list-section { margin-top:18px; }
  .news-list-section h2 { font-size:11px; color:var(--amber); letter-spacing:.15em;
    text-transform:uppercase; margin:0 0 8px; }
  .news-list-section details { border:1px solid var(--line); margin-bottom:8px;
    background:var(--panel); }
  .news-list-section summary { padding:8px 14px; cursor:pointer;
    font-size:.82rem; color:var(--ink-soft); background:var(--panel-2);
    list-style:none; display:flex; justify-content:space-between; letter-spacing:.04em; }
  .news-list-section summary::-webkit-details-marker { display:none; }
  .news-list-section summary::after { content:"▼"; font-size:.7rem; }
  .news-list-section details[open] summary::after { content:"▲"; }
  .news-items { list-style:none; padding:4px 0; margin:0; }
  .news-items li { padding:5px 14px; border-bottom:1px solid var(--line-soft);
    font-size:11.5px; color:var(--ink-soft); margin:0; }
  .news-items li:last-child { border-bottom:none; }
  .news-items a { color:var(--amber); text-decoration:none; }
  .news-items a:hover { text-decoration:underline; }
  .news-label { display:inline-block; font-size:.7rem; background:var(--panel-2);
    color:var(--ink-mute); padding:1px 5px; border:1px solid var(--line);
    margin-right:6px; }

  /* 아카이브 */
  .arch h1 { color:var(--amber); font-size:16px; letter-spacing:.06em; margin:0 0 4px; }
  .arch h1::before { content:'▸ '; }
  .arch .count { color:var(--ink-mute); font-size:11px;
    letter-spacing:.1em; text-transform:uppercase; margin:0 0 18px; }
  .arch table { width:100%; border-collapse:collapse; font-size:12px; }
  .arch th { text-align:left; color:var(--ink-mute); font-weight:500;
    letter-spacing:.08em; padding:8px 10px; font-size:10px; text-transform:uppercase;
    border-bottom:1px solid var(--line); background:var(--panel-2); }
  .arch td { padding:8px 10px; border-bottom:1px solid var(--line-soft); color:var(--ink); }
  .arch tr:hover td { background:rgba(245,165,36,.05); }
  .arch a { color:var(--ink); text-decoration:none; }
  .arch a:hover { color:var(--amber); }
  .arch .date { color:var(--ink-mute); width:120px; }

  .status-bar { border-top:1px solid var(--line); background:var(--panel-2);
    padding:0 16px; font-size:10px; color:var(--ink-mute);
    display:flex; gap:16px; height:28px; align-items:center; letter-spacing:.06em; }
  .status-bar .ok { color:var(--green); }
  .status-bar .spacer { margin-left:auto; }
"""


def _layout(title: str, body: str, active: str, site_title: str, now: str, date_str: str = "") -> str:
    nav_items = [
        ("news",    "index.html",   "BRIEF"),
        ("stock",   "../stock/",    "STOCK"),
        ("archive", "archive.html", "ARCHIVE"),
    ]
    nav_html = "".join(
        f'<a class="nav-tab {"on" if active == key else ""}" href="{url}">{label}</a>'
        for key, url, label in nav_items
    )
    footer = FOOTER_CONFIG
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI가 매일 자동으로 수집·분석하는 글로벌 뉴스 브리핑">
  <title>{title} — {site_title}</title>
  {_FONTS}
  <style>{_CSS}</style>
</head>
<body>
  <div class="topbar">
    <div class="lhs">
      <div class="logo"><span class="logo-box">N</span><span>DAILY/NEWS</span></div>
      {nav_html}
    </div>
    <div class="rhs">
      <span class="live">LIVE</span>
      <span>{date_str or title}</span>
      <span>KST</span>
    </div>
  </div>

  <div class="wrap">{body}</div>

  <div class="status-bar">
    <span class="ok">● OK</span>
    <span>{footer['generator']}</span>
    <span class="spacer">{footer['repo']} · gh-actions</span>
    <span>{now} KST</span>
  </div>
</body>
</html>"""


def _cat_bar(cat_stats: dict) -> str:
    if not cat_stats:
        return ""
    total = sum(cat_stats.values()) or 1
    label_map = {
        "ai_ml": "AI/ML", "technology": "TECH", "economy": "ECON",
        "global_news": "GLOBAL", "korean_news": "KR-NEWS", "korean_economy": "KR-ECON",
        "korean_tech": "KR-TECH", "security": "SEC", "startup": "STARTUP",
    }
    rows = ""
    for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        pct = round(count / total * 100)
        filled = "█" * (pct // 5)
        empty  = "░" * (20 - pct // 5)
        rows += (
            f'<div style="display:flex;gap:8px;align-items:center;margin-bottom:3px">'
            f'<span style="width:72px;color:var(--ink-mute);font-size:10px;letter-spacing:.04em">'
            f'{label_map.get(cat, cat)}</span>'
            f'<span style="color:var(--amber);font-size:10px">{filled}{empty}</span>'
            f'<span style="color:var(--ink-mute);font-size:10px;margin-left:4px">{count}</span>'
            f'</div>'
        )
    return rows


def _issue_card(issue: dict, accent: str) -> str:
    imp_label = {"high": "HIGH", "medium": "MED ", "low": "LOW "}
    imp = imp_label.get(issue.get("importance", "medium"), "MED ")
    sources_html = ""
    for src in issue.get("sources", [])[:1]:
        title_trunc = src["title"][:60] + ("…" if len(src["title"]) > 60 else "")
        sources_html = (
            f'<div style="margin-top:8px;font-size:10px;color:var(--ink-mute)">'
            f'↗ <a href="{src["url"]}" style="color:{accent};text-decoration:none">'
            f'{title_trunc}</a></div>'
        )
    return (
        f'<div style="background:var(--panel-2);border:1px solid var(--line);'
        f'padding:12px 14px;margin-bottom:8px">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:6px">'
        f'<span style="font-size:10px;color:{accent};letter-spacing:.12em">[{imp}] #{issue["rank"]}</span>'
        f'<span style="font-size:10px;color:var(--ink-mute)">{issue.get("category","")}</span></div>'
        f'<div style="font-size:13px;font-weight:600;color:var(--ink);margin-bottom:6px;line-height:1.4">'
        f'{issue["title"]}</div>'
        f'<div style="font-size:11px;color:var(--ink-soft);line-height:1.6">{issue["summary"]}</div>'
        f'{sources_html}</div>'
    )


def _trend_row(t: dict, accent: str) -> str:
    return (
        f'<div style="padding:5px 0;border-bottom:1px solid var(--line-soft);font-size:11px">'
        f'<span style="color:{accent};font-weight:600">[{t["keyword"]}]</span> '
        f'<span style="color:var(--ink-soft)">{t.get("description","")}</span></div>'
    )


def _json_body(en_data: dict, ko_data: dict) -> str:
    en_cards = "".join(_issue_card(i, "var(--amber)") for i in en_data.get("issues", [])[:3])
    ko_cards = "".join(_issue_card(i, "var(--green)") for i in ko_data.get("issues", [])[:3])

    en_trends = "".join(_trend_row(t, "var(--amber)") for t in en_data.get("trends", [])[:3])
    ko_trends = "".join(_trend_row(t, "var(--green)") for t in ko_data.get("trends", [])[:3])

    cat_stats: dict = {}
    for d in (en_data, ko_data):
        for k, v in d.get("category_stats", {}).items():
            cat_stats[k] = cat_stats.get(k, 0) + v
    cat_html = _cat_bar(cat_stats)

    no_data = '<div style="color:var(--ink-mute);font-size:11px;padding:12px">데이터 없음</div>'
    hdr_en = '<div style="font-size:11px;color:var(--amber);letter-spacing:.15em;text-transform:uppercase;margin-bottom:8px;padding:6px 10px;background:var(--panel-2);border-left:2px solid var(--amber)">▸ GLOBAL TOP STORIES</div>'
    hdr_ko = '<div style="font-size:11px;color:var(--green);letter-spacing:.15em;text-transform:uppercase;margin-bottom:8px;padding:6px 10px;background:var(--panel-2);border-left:2px solid var(--green)">▸ KR TOP STORIES</div>'

    return f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
      <div>{hdr_en}{en_cards or no_data}</div>
      <div>{hdr_ko}{ko_cards or no_data}</div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 220px;gap:12px">
      <div>
        <div style="font-size:11px;color:var(--amber);letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">GLOBAL TRENDS</div>
        {en_trends or '<div style="color:var(--ink-mute);font-size:11px">—</div>'}
      </div>
      <div>
        <div style="font-size:11px;color:var(--green);letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">KR TRENDS</div>
        {ko_trends or '<div style="color:var(--ink-mute);font-size:11px">—</div>'}
      </div>
      <div>
        <div style="font-size:11px;color:var(--ink-mute);letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px">CATEGORY DIST</div>
        {cat_html or '<div style="color:var(--ink-mute);font-size:11px">—</div>'}
      </div>
    </div>"""


def render_report(ctx: dict) -> str:
    s = ctx["data"]["stats"]
    structured = ctx.get("structured", {})

    from themes.base import _split_at_news_list, _build_news_list_section
    analysis_html = _split_at_news_list(ctx["md_html"])
    news_section  = _build_news_list_section(
        ctx["data"].get("news_en", []),
        ctx["data"].get("news_ko", []),
    )

    en_data  = structured.get("en", {})
    ko_data  = structured.get("ko", {})
    has_json = bool(en_data or ko_data)

    analysis_body = (
        _json_body(en_data, ko_data) if has_json
        else f'<div class="prose">{analysis_html}</div>'
    )

    body = f"""
    <div class="main-head">
      <h1><span class="gt">&gt;</span> daily_brief.md // {ctx['date_str']}</h1>
      <div class="meta">
        {ctx['display_date']}<br>
        Generated {ctx['now']} KST<br>
        <span class="ok">● status=success</span>
      </div>
    </div>
    <div class="statgrid">
      <div><div class="l">TOTAL</div><div class="n">{s['total']}</div></div>
      <div><div class="l">AI ANALYZED</div><div class="n green">{s['sent_to_ai']}</div></div>
      <div><div class="l">KOREAN</div><div class="n">{s['ko']}</div></div>
      <div><div class="l">ENGLISH</div><div class="n amber">{s['en']}</div></div>
    </div>
    {analysis_body}
    {news_section}"""
    return _layout(ctx["display_date"], body, "news", ctx["site_title"], ctx["now"], ctx["date_str"])


def render_archive(ctx: dict) -> str:
    rows = "".join(f"""
        <tr>
          <td class="date">{it['date']}</td>
          <td><a href="{it['date']}.html">{it['display']}</a></td>
          <td style="color:var(--ink-mute);text-align:right">→</td>
        </tr>""" for it in ctx["items"])
    body = f"""
    <div class="arch">
      <h1>ARCHIVE INDEX</h1>
      <div class="count">{len(ctx['items'])} REPORTS · SORT: DATE ↓</div>
      <table>
        <thead><tr><th>DATE</th><th>TITLE</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""
    return _layout("ARCHIVE", body, "archive", ctx["site_title"], ctx["now"])


def render_stock_report(ctx: dict) -> str:
    from themes.base import render_stock_report as _base
    return _base(ctx, "classic")


def render_stock_archive(ctx: dict) -> str:
    from themes.base import render_stock_archive as _base
    return _base(ctx, "classic")
