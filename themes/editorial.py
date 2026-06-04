# themes/editorial.py
"""Editorial 테마 — 신문 마스트헤드, Noto Serif KR, 드롭캡.

[커스텀 레이아웃 테마] base.py 미사용. render_*() 함수가 Python f-string으로 HTML 직접 생성.
레이아웃·색상 모두 이 파일에서 수정. templates/web_*.html 은 이 테마에서 사용 안 함.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.theme_config import FOOTER_CONFIG, SITE_LOGO_HTML

TOKENS = {
    "meta": {
        "name":     "editorial",
        "label":    "Editorial",
        "desc":     "전통 영문 신문 스타일, 고풍 명조",
        "swatch_colors": ["#2b231a", "#8b2a1f"],
        "font_cdn": "https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;800;900&family=IBM+Plex+Mono:wght@400;500;700&display=swap",
        "font_family": "'Noto Serif KR', 'Source Serif Pro', Georgia, serif",
    },
    "colors": {
        "bg":         "#f4ede0",
        "card":       "#ece2cf",
        "text":       "#1a1612",
        "muted":      "#8a7e6f",
        "accent":     "#8b2a1f",
        "rule":       "#2b231a",
        # base.py 표준 렌더러(stock) 호환 alias
        "navy":       "#2b231a",
        "blue":       "#8b2a1f",
        "blue_light": "#c4735a",
        "blue_50":    "#fdf4ee",
        "blue_200":   "#e8c9b8",
        "border":     "#c8bda7",
        "code_bg":    "#ece2cf",
        "green":      "#4a6741",
        "orange":     "#8b5a2a",
    },
    "typography": {
        "font_sans": "'Noto Serif KR', Georgia, serif",
        "leading":   1.8,
    },
}

_FONTS = """
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;800;900&family=IBM+Plex+Mono:wght@400;500;700&display=swap" rel="stylesheet">
"""

_CSS = """
  :root {
    --ink:#1a1612; --ink-soft:#4a4036; --ink-mute:#8a7e6f;
    --paper:#f4ede0; --paper-2:#ece2cf;
    --rule:#2b231a; --rule-soft:#c8bda7; --accent:#8b2a1f;
  }
  *,*::before,*::after { box-sizing:border-box; }
  body { margin:0; background:var(--paper); color:var(--ink); line-height:1.65;
    font-family:'Noto Serif KR','Source Serif Pro',Georgia,serif; }

  .wrap { max-width:980px; margin:0 auto; padding:32px 32px 56px; }

  .masthead { border-top:6px solid var(--rule); border-bottom:1px solid var(--rule);
    padding:14px 0 12px; margin-bottom:22px; }
  .mh-top { display:flex; justify-content:space-between; align-items:baseline;
    font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em;
    color:var(--ink-soft); text-transform:uppercase;
    border-bottom:1px solid var(--rule-soft); padding-bottom:8px; margin-bottom:14px; }
  .mh-title { font-weight:900; font-size:72px; letter-spacing:-.04em;
    line-height:.92; text-align:center; margin:6px 0 2px; font-style:italic; }
  .mh-title em { color:var(--accent); }
  .mh-tag { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.3em;
    text-align:center; color:var(--ink-soft); text-transform:uppercase;
    padding-top:6px; border-top:1px solid var(--rule-soft); margin-top:10px; }
  .mh-nav { display:flex; justify-content:center; gap:32px; margin-top:14px;
    font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.08em;
    text-transform:uppercase; }
  .mh-nav a { color:var(--ink-soft); text-decoration:none; }
  .mh-nav a.on { color:var(--accent); font-weight:700;
    border-bottom:2px solid var(--accent); padding-bottom:2px; }

  .brief { display:grid; grid-template-columns:200px 1fr 160px; gap:24px;
    border-bottom:1px solid var(--rule); padding:18px 0 22px; margin-bottom:28px; }
  .brief-stats { font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--ink-soft); }
  .brief-stats .lbl { color:var(--ink); font-weight:700; display:block;
    margin-bottom:8px; letter-spacing:.08em; }
  .brief-stat { display:flex; gap:14px; align-items:baseline; margin-top:10px; }
  .brief-stat .num { font-family:'Noto Serif KR',serif; font-size:24px;
    font-weight:700; font-style:italic; }
  .brief-stat .lab { font-size:10px; letter-spacing:.15em;
    color:var(--ink-mute); text-transform:uppercase; }
  .kicker { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.2em;
    text-transform:uppercase; color:var(--accent); margin-bottom:8px;
    border-left:3px solid var(--accent); padding-left:12px; }
  .lede { font-size:20px; line-height:1.4; font-weight:500; text-wrap:balance; }
  .byline { font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--ink-mute);
    text-align:right; line-height:1.7; border-left:1px solid var(--rule-soft); padding-left:14px; }

  .prose { font-size:16px; line-height:1.8; }
  .prose h1 { display:none; }
  .prose h2 { font-family:'Noto Serif KR',serif; font-size:22px; font-weight:800;
    letter-spacing:-.015em; margin:36px 0 14px; padding-bottom:6px;
    border-bottom:2px solid var(--rule); }
  .prose h3 { font-size:17px; font-weight:700; margin:24px 0 8px; }
  .prose p { margin:0 0 14px; }
  .prose a { color:var(--accent); text-decoration:none;
    border-bottom:1px solid var(--rule-soft); }
  .prose a:hover { border-bottom-color:var(--accent); }
  .prose strong { color:var(--ink); font-weight:700; }
  .prose ul { padding-left:0; list-style:none; columns:2; column-gap:32px;
    column-rule:1px solid var(--rule-soft); margin:0 0 18px; }
  .prose ul li { break-inside:avoid; padding:8px 0 8px 20px; position:relative;
    border-bottom:1px dotted var(--rule-soft); font-size:14px; line-height:1.55; }
  .prose ul li::before { content:'§'; position:absolute; left:0; top:8px;
    color:var(--accent); font-weight:700; font-family:serif; }
  .prose ol { padding-left:1.4em; margin:0 0 18px; }
  .prose ol li { margin-bottom:6px; }
  .prose blockquote { font-family:'IBM Plex Mono',monospace; font-size:12px;
    border-left:3px solid var(--accent); padding:8px 16px; margin:14px 0;
    background:rgba(139,42,31,.04); color:var(--ink-soft); }
  .prose blockquote p { margin:0; }
  .prose hr { border:none; border-top:3px double var(--rule); margin:32px 0; }
  .prose code { font-family:'IBM Plex Mono',monospace; background:var(--paper-2);
    padding:2px 6px; border-radius:3px; font-size:.85em; }

  /* 뉴스 목록 접기/펼치기 */
  .news-list-section { margin-top:32px; border-top:3px double var(--rule); padding-top:20px; }
  .news-list-section h2 { font-family:'IBM Plex Mono',monospace; font-size:13px;
    letter-spacing:.15em; text-transform:uppercase; color:var(--ink-soft);
    margin:0 0 12px; }
  .news-list-section details { border:1px solid var(--rule-soft); margin-bottom:10px; }
  .news-list-section summary { padding:10px 14px; cursor:pointer; font-weight:600;
    font-size:.9rem; color:var(--ink); background:var(--paper-2);
    list-style:none; display:flex; justify-content:space-between; }
  .news-list-section summary::-webkit-details-marker { display:none; }
  .news-list-section summary::after { content:"▼"; font-size:.7rem; color:var(--ink-mute); }
  .news-list-section details[open] summary::after { content:"▲"; }
  .news-items { list-style:none; padding:6px 0; margin:0; }
  .news-items li { padding:6px 14px; border-bottom:1px solid var(--rule-soft);
    font-size:.84rem; line-height:1.5; margin:0; }
  .news-items li:last-child { border-bottom:none; }
  .news-label { display:inline-block; font-family:'IBM Plex Mono',monospace;
    font-size:.7rem; background:var(--paper-2); color:var(--ink-mute);
    padding:1px 6px; border-radius:3px; margin-right:6px; }

  /* 아카이브 */
  .arch h1 { font-size:32px; font-weight:900; margin:18px 0 6px; }
  .arch p.count { font-family:'IBM Plex Mono',monospace; font-size:12px;
    color:var(--ink-mute); letter-spacing:.1em; text-transform:uppercase; margin:0 0 24px; }
  .arch ul { list-style:none; padding:0; margin:0;
    columns:2; column-gap:32px; column-rule:1px solid var(--rule-soft); }
  .arch li { break-inside:avoid; padding:14px 0; border-bottom:1px solid var(--rule-soft); }
  .arch a { color:var(--ink); text-decoration:none; font-weight:600; font-size:16px; }
  .arch a:hover { color:var(--accent); }
  .arch .d { font-family:'IBM Plex Mono',monospace; font-size:11px;
    color:var(--ink-mute); margin-top:3px; letter-spacing:.04em; }

  .foot { border-top:6px solid var(--rule); margin-top:32px; padding-top:14px;
    display:flex; justify-content:space-between; align-items:baseline;
    font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--ink-mute);
    letter-spacing:.12em; text-transform:uppercase; flex-wrap:wrap; gap:8px; }

  @media (max-width:720px) {
    .mh-title { font-size:48px; }
    .brief { grid-template-columns:1fr; gap:18px; }
    .brief-stats, .byline { border-left:none; padding-left:0; }
    .prose ul, .arch ul { columns:1; }
  }
"""


def _masthead_title(site_title: str) -> str:
    parts = site_title.rsplit(" ", 1)
    if len(parts) == 2:
        return f'{parts[0]} <em>{parts[1]}</em>'
    return site_title


def _layout(title: str, body: str, active: str, site_title: str, now: str, site_url: str = "", nav_prefix: str = "") -> str:
    nav_items = [
        ("news",     "index.html",   "📰 뉴스 브리핑"),
        ("ai-issue", "ai-issue/",    "🤖 AI이슈"),
        ("stock",    "stock/",       "📊 주식 시황"),
        ("archive",  "archive.html", "📚 아카이브"),
    ]
    nav_html = "  ".join(
        f'<a href="{nav_prefix}{url}" class="{"on" if active == key else ""}">{label}</a>'
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
  <div class="wrap">
    <div class="masthead">
      <div class="mh-top">
        <span>AI NEWS</span>
        <span>{title}</span>
        <span>KST 08:00</span>
      </div>
      <a href="{nav_prefix}index.html" style="text-decoration:none;color:inherit">
        <h1 class="mh-title">{_masthead_title(site_title)}</h1>
      </a>
      <div class="mh-tag">RSS · AI 분석 · 매일 아침 한 부</div>
      <div class="mh-nav">{nav_html}</div>
    </div>

    {body}

    <div class="foot">
      <span>{site_title}</span>
      <span>Generated by {footer['generator']}</span>
      <span>{footer['repo']}</span>
      <span>생성 {now} KST</span>
    </div>
  </div>
</body>
</html>"""


def _category_bar_html(cat_stats: dict) -> str:
    """카테고리 분포 바 (JSON structured 데이터 활용)."""
    if not cat_stats:
        return ""
    total = sum(cat_stats.values()) or 1
    label_map = {
        "ai_ml": "AI·ML", "technology": "기술", "economy": "경제",
        "global_news": "글로벌", "korean_news": "국내", "korean_economy": "국내경제",
        "korean_tech": "국내기술", "security": "보안", "startup": "스타트업",
    }
    bars = ""
    for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        pct = round(count / total * 100)
        bars += (
            f'<div style="margin-bottom:6px">'
            f'<span style="font-family:IBM Plex Mono,monospace;font-size:10px;'
            f'color:var(--ink-mute);text-transform:uppercase;letter-spacing:.08em;'
            f'display:inline-block;width:80px">{label_map.get(cat, cat)}</span>'
            f'<span style="display:inline-block;background:var(--accent);height:8px;'
            f'width:{pct}%;max-width:120px;vertical-align:middle;border-radius:1px"></span>'
            f'<span style="font-size:10px;color:var(--ink-mute);margin-left:6px">{count}건</span>'
            f'</div>'
        )
    return f'<div style="margin-top:12px"><div style="font-size:10px;font-weight:700;color:var(--ink);letter-spacing:.12em;text-transform:uppercase;margin-bottom:8px">카테고리 분포</div>{bars}</div>'


def _top_stories_html(issues: list) -> str:
    """Top Stories 카드 섹션 (JSON issues 데이터 활용)."""
    if not issues:
        return ""
    importance_badge = {"high": "■ 주요", "medium": "□ 일반", "low": "○ 참고"}
    cards = ""
    for issue in issues[:3]:
        badge = importance_badge.get(issue.get("importance", "medium"), "□")
        sources_html = ""
        for src in issue.get("sources", [])[:2]:
            sources_html += f'<a href="{src["url"]}" style="color:var(--accent);font-size:10px;font-family:IBM Plex Mono,monospace;text-decoration:none;display:block;margin-top:4px">↗ {src["title"][:50]}{"…" if len(src["title"])>50 else ""}</a>'
        cards += f"""
        <div style="border-top:1px solid var(--rule-soft);padding:14px 0">
          <div style="font-family:IBM Plex Mono,monospace;font-size:10px;color:var(--accent);letter-spacing:.15em;text-transform:uppercase;margin-bottom:6px">{badge} 이슈 {issue['rank']}</div>
          <h3 style="font-size:16px;font-weight:800;margin:0 0 8px;line-height:1.35">{issue['title']}</h3>
          <p style="font-size:13px;line-height:1.7;margin:0;color:var(--ink-soft)">{issue['summary']}</p>
          {sources_html}
        </div>"""
    return cards


def render_report(ctx: dict) -> str:
    s = ctx["data"]["stats"]
    structured = ctx.get("structured", {})

    from themes.base import _split_at_news_list, _build_news_list_section
    analysis_html = _split_at_news_list(ctx["md_html"])
    news_section  = _build_news_list_section(
        ctx["data"].get("news_en", []),
        ctx["data"].get("news_ko", []),
    )

    # JSON 구조 데이터가 있으면 rich UI 활용
    en_data  = structured.get("en", {})
    ko_data  = structured.get("ko", {})
    has_json = bool(en_data or ko_data)

    cat_stats_merged: dict = {}
    for d in (en_data, ko_data):
        for k, v in d.get("category_stats", {}).items():
            cat_stats_merged[k] = cat_stats_merged.get(k, 0) + v

    cat_bar  = _category_bar_html(cat_stats_merged)
    en_stories = _top_stories_html(en_data.get("issues", [])) if en_data else ""
    ko_stories = _top_stories_html(ko_data.get("issues", [])) if ko_data else ""

    if has_json:
        analysis_body = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-top:24px">
          <div>
            <div class="kicker">🌐 글로벌 핵심이슈</div>
            {en_stories or analysis_html}
          </div>
          <div>
            <div class="kicker">🇰🇷 국내 핵심이슈</div>
            {ko_stories}
          </div>
        </div>"""
    else:
        analysis_body = f'<div class="prose">{analysis_html}</div>'

    body = f"""
    <div class="brief">
      <div class="brief-stats">
        <span class="lbl">오늘의 통계</span>
        <div class="brief-stat"><span class="num">{s['total']}</span><span class="lab">건 수집</span></div>
        <div class="brief-stat"><span class="num">{s['sent_to_ai']}</span><span class="lab">AI 분석</span></div>
        <div class="brief-stat"><span class="num">{s['ko']}</span><span class="lab">국내</span></div>
        {cat_bar}
      </div>
      <div>
        <div class="kicker">에디터 노트 · TODAY'S LEDE</div>
        <p class="lede">AI가 매일 아침 수십 개 언론사의 헤드라인을 한 면에 정리합니다.
        오늘 분석된 {s['sent_to_ai']}건의 기사 핵심을 아래에서 읽어보세요.</p>
      </div>
      <div class="byline">
        AI Editor<br>{FOOTER_CONFIG['generator']}<br>─<br>{ctx['date_str']}
      </div>
    </div>
    {analysis_body}
    {news_section}"""
    return _layout(ctx["display_date"], body, "news", ctx["site_title"], ctx["now"], ctx.get("site_url", ""), nav_prefix="../")


def render_archive(ctx: dict) -> str:
    """통합 아카이브: 마스트헤드 + 3탭(뉴스/주식/AI이슈) + 검색."""
    news_list  = ctx.get("items", [])
    stock_list = ctx.get("stock_items", [])
    ai_list    = ctx.get("ai_items", [])
    total      = len(news_list) + len(stock_list) + len(ai_list)

    def _li(it: dict, href: str, icon: str) -> str:
        return (
            f'<li data-label="{it["display"]}">'
            f'<a href="{href}">{icon} {it["display"]}</a>'
            f'<span class="d">{it["date"]}</span>'
            f'</li>'
        )

    news_html  = "".join(_li(it, f'news/{it["date"]}.html',     "📰") for it in news_list)  or "<li style='color:var(--muted);padding:12px 0'>뉴스 리포트 없음</li>"
    stock_html = "".join(_li(it, f'stock/{it["date"]}.html',    "📊") for it in stock_list) or "<li style='color:var(--muted);padding:12px 0'>주식 리포트 없음</li>"
    ai_html    = "".join(_li(it, f'ai-issue/{it["date"]}.html', "🤖") for it in ai_list)    or "<li style='color:var(--muted);padding:12px 0'>AI이슈 보고서 없음</li>"

    tab_style  = "font-family:inherit;font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;padding:4px 0;border:none;border-bottom:2px solid transparent;background:none;cursor:pointer;color:var(--muted);margin-right:20px"
    tab_active = tab_style.replace("border-bottom:2px solid transparent", "border-bottom:2px solid var(--rule)").replace("color:var(--muted)", "color:var(--text);font-weight:700")

    body = f"""
    <div class="arch">
      <h1>전체 리포트 색인</h1>
      <p class="count">LEDGER · 총 {total}호 발행</p>

      <div style="margin-bottom:8px;border-bottom:1px solid var(--rule);padding-bottom:4px">
        <button onclick="showTab('news')"  id="tabNews"  style="{tab_active}">📰 뉴스 {len(news_list)}</button>
        <button onclick="showTab('stock')" id="tabStock" style="{tab_style}">📊 주식 {len(stock_list)}</button>
        <button onclick="showTab('ai')"    id="tabAi"    style="{tab_style}">🤖 AI이슈 {len(ai_list)}</button>
      </div>

      <div style="position:relative;margin-bottom:16px">
        <input id="searchBox" type="text"
          placeholder="날짜 또는 요일로 검색…"
          oninput="filterList()"
          style="width:100%;padding:8px 12px 8px 32px;border:1px solid var(--rule-soft);
                 border-radius:6px;background:var(--paper-2);color:var(--ink);
                 font-family:inherit;font-size:.88rem;outline:none;" />
        <span style="position:absolute;left:10px;top:50%;transform:translateY(-50%);pointer-events:none;font-size:.82rem">🔍</span>
      </div>
      <p id="searchCount" style="font-size:.78rem;color:var(--muted);margin-bottom:10px;font-family:'IBM Plex Mono',monospace;letter-spacing:.05em"></p>

      <div id="tabPanelNews"  ><ul>{news_html}</ul></div>
      <div id="tabPanelStock" style="display:none"><ul>{stock_html}</ul></div>
      <div id="tabPanelAi"    style="display:none"><ul>{ai_html}</ul></div>
    </div>

    <script>
    var _active = 'news';
    var _tabA = "{tab_active}", _tabN = "{tab_style}";
    function showTab(t) {{
      ['news','stock','ai'].forEach(function(k) {{
        var cap = k.charAt(0).toUpperCase()+k.slice(1);
        document.getElementById('tabPanel'+cap).style.display = k===t ? '' : 'none';
        document.getElementById('tab'+cap).setAttribute('style', k===t ? _tabA : _tabN);
      }});
      _active = t;
      document.getElementById('searchBox').value = '';
      document.getElementById('searchCount').textContent = '';
    }}
    function filterList() {{
      var q = document.getElementById('searchBox').value.trim().toLowerCase();
      var cap = _active.charAt(0).toUpperCase()+_active.slice(1);
      var lis = document.getElementById('tabPanel'+cap).querySelectorAll('li[data-label]');
      var shown = 0;
      lis.forEach(function(li) {{
        var match = !q || li.getAttribute('data-label').toLowerCase().indexOf(q) >= 0;
        li.style.display = match ? '' : 'none';
        if (match) shown++;
      }});
      document.getElementById('searchCount').textContent = q ? shown + '건 검색됨' : '';
    }}
    </script>"""

    return _layout("아카이브", body, "archive", ctx["site_title"], ctx["now"], ctx.get("site_url", ""))


def render_stock_report(ctx: dict) -> str:
    from themes.base import render_stock_report as _base
    return _base(ctx, "editorial")


def render_stock_archive(ctx: dict) -> str:
    from themes.base import render_stock_archive as _base
    return _base(ctx, "editorial")
