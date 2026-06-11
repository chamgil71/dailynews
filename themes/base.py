# themes/base.py
"""
토큰 기반 렌더링 엔진.

역할 분담:
  templates/*.html  → HTML 구조 (Jinja2 템플릿)
  themes/{name}.py  → 색상·폰트 토큰 (TOKENS dict)
  themes/base.py    → 토큰 로드 + Jinja2 렌더링 (이 파일)

표준 렌더러 (classic/ink/forest 등 토큰 교체형 테마):
  render_report(), render_archive(), render_stock_report(), render_stock_archive()

커스텀 레이아웃 테마 (editorial/terminal/minimal):
  자체 render_*() 구현을 가지며, 웹 레이아웃을 Python에서 직접 정의.
  layout_html()을 헬퍼로 사용할 수 있음.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib

from config.theme_config import NAV_SECTIONS, HUB_SECTIONS, FOOTER_CONFIG, SITE_LOGO_HTML

_TEMPLATES = Path(__file__).parent.parent / "templates"


# ── 토큰 조회 ─────────────────────────────────────────────────────────────────

def get_tokens(theme_name: str) -> dict:
    try:
        mod = importlib.import_module(f"themes.{theme_name}")
        return mod.TOKENS
    except (ModuleNotFoundError, AttributeError):
        from themes.classic import TOKENS
        return TOKENS


# ── CSS :root 변수 블록 (테마 토큰 → CSS 변수) ────────────────────────────────

def css_root_vars(tokens: dict) -> str:
    c = tokens["colors"]
    t = tokens["typography"]
    return f"""
  :root {{
    --color-blue:        {c['blue']};
    --color-blue-light:  {c['blue_light']};
    --color-blue-50:     {c['blue_50']};
    --color-blue-200:    {c['blue_200']};
    --color-navy:        {c['navy']};
    --color-bg:          {c['bg']};
    --color-card:        {c['card']};
    --color-border:      {c['border']};
    --color-text:        {c['text']};
    --color-muted:       {c['muted']};
    --color-code-bg:     {c['code_bg']};
    --color-green:       {c['green']};
    --color-green-50:    {c.get('green_50', '#f0fdf4')};
    --color-green-200:   {c.get('green_200', '#bbf7d0')};
    --color-orange:      {c['orange']};
    --color-orange-50:   {c.get('orange_50', '#fff7ed')};
    --color-orange-200:  {c.get('orange_200', '#fed7aa')};
    --color-up:          {c['green']};
    --color-up-50:       {c.get('green_50', '#f0fdf4')};
    --color-up-200:      {c.get('green_200', '#bbf7d0')};
    --color-down:        #dc2626;
    --color-down-50:     #fef2f2;
    --color-down-200:    #fecaca;
    --font-sans:         {t['font_sans']};
    --leading-base:      {t['leading']};
  }}"""


# ── 내비게이션 HTML ──────────────────────────────────────────────────────────

def nav_html(active_key: str, nav_prefix: str = "") -> str:
    enabled = [s for s in NAV_SECTIONS if s["enabled"]]
    parts = []
    for s in enabled:
        cls = ' class="active"' if active_key == s["key"] else ""
        parts.append(f'<a href="{nav_prefix}{s["url"]}"{cls}>{s["label"]}</a>')
    return "\n      ".join(parts)


# ── 커스텀 테마용 헬퍼 (editorial/terminal/minimal에서 사용) ──────────────────

def hub_sections_html(nav_prefix: str = "") -> str:
    active = [s for s in HUB_SECTIONS if s["enabled"]]
    if not active:
        return ""
    abbr_map = {"news": "NW", "stock": "ST", "ai-issue": "AI", "archive": "AR"}
    cards = "".join(f"""
    <a href="{nav_prefix}{s['url']}" class="hub-section-card">
      <span class="section-abbr">{abbr_map.get(s.get('key', ''), s['label'][:2].upper())}</span>
      <h3>{s['label']}</h3>
      <p>{s['desc']}</p>
    </a>""" for s in active)
    return f'<div class="hub-sections">{cards}\n  </div>'


def subscribe_card_html(subscribe_url: str) -> str:
    return f"""
  <div class="card subscribe-card">
    <h3>뉴스레터 구독</h3>
    <p style="color:var(--color-muted);margin:.5em 0 0">
      매일 오전 AI가 정리한 글로벌 뉴스 브리핑을 이메일로 받아보세요.
    </p>
    <a href="{subscribe_url}" target="_blank" rel="noopener" class="btn">
      구독 신청하기
    </a>
    <p style="font-size:.8rem;color:var(--color-muted);margin:.8em 0 0">
      구독 취소는 수신된 메일 하단 링크를 클릭하세요.
    </p>
  </div>"""


def layout_html(
    title: str,
    body: str,
    active: str,
    site_title: str,
    now: str,
    tokens: dict,
    extra_css: str = "",
    nav_prefix: str = "",
) -> str:
    """커스텀 테마(minimal 등)용 레이아웃 빌더. 표준 렌더러는 Jinja2 템플릿 사용."""
    font_cdn = tokens.get("meta", {}).get("font_cdn", "")
    font_link = (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        f'  <link rel="stylesheet" href="{font_cdn}" crossorigin>'
        if font_cdn else ""
    )
    css_root = css_root_vars(tokens)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI가 매일 자동으로 수집·분석하는 글로벌 뉴스 브리핑">
  <title>{title} — {site_title}</title>
  {font_link}
  <style>
  {css_root}
  {_COMMON_CSS}
  {extra_css}
  </style>
</head>
<body>
  <header>
    <div class="logo">AI <span class="accent">News</span> Brief</div>
    <nav>
      {nav_html(active, nav_prefix)}
    </nav>
  </header>

  <div class="container">
    {body}
  </div>

  <footer>
    {FOOTER_CONFIG['powered_by']} · {FOOTER_CONFIG['update_text']}<br>
    Generated by {FOOTER_CONFIG['generator']} ·
    <a href="https://github.com/{FOOTER_CONFIG['repo']}" style="color:inherit">{FOOTER_CONFIG['repo']}</a>
    · 생성: {now} KST
  </footer>
</body>
</html>"""


_COMMON_CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: var(--font-sans);
    background: var(--color-bg);
    color: var(--color-text);
    line-height: var(--leading-base);
    -webkit-font-smoothing: antialiased;
  }

  /* ── 헤더 ── */
  header {
    background: var(--color-navy);
    color: #fff;
    padding: 0 20px;
    display: flex;
    align-items: center;
    height: 58px;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,.22);
  }
  header .logo {
    font-size: 1.05rem; font-weight: 700; letter-spacing: -.3px;
    margin-right: 24px; white-space: nowrap; cursor: pointer;
  }
  header .logo .accent { color: var(--color-blue-light); }
  .header-nav {
    display: flex; align-items: center; height: 100%; flex: 1; gap: 2px;
  }
  .hnav-tab {
    display: flex; align-items: center; height: 100%;
    padding: 0 14px;
    color: rgba(255,255,255,.6);
    text-decoration: none; font-size: .875rem; font-weight: 500;
    border-bottom: 3px solid transparent;
    border-top: none; border-left: none; border-right: none;
    cursor: pointer; background: none;
    transition: color .15s, border-color .15s; white-space: nowrap;
  }
  .hnav-tab:hover { color: rgba(255,255,255,.9); }
  .hnav-tab.active {
    color: #fff; font-weight: 600;
    border-bottom-color: var(--color-blue-light);
  }
  .tab-label { pointer-events: none; }
  .header-actions {
    display: flex; align-items: center; gap: 8px; margin-left: auto;
  }
  .btn-icon {
    background: none; border: none; color: rgba(255,255,255,.65);
    cursor: pointer; padding: 6px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    transition: color .15s, background .15s; text-decoration: none;
  }
  .btn-icon:hover { color: #fff; background: rgba(255,255,255,.1); }

  /* legacy nav fallback (nav.js 교체 전 id="site-nav" 깜빡임 방지) */
  header nav a {
    color: rgba(255,255,255,.6); text-decoration: none;
    padding: 0 14px; font-size: .875rem;
    display: flex; align-items: center; height: 100%;
  }
  header nav a.active { color: #fff; font-weight: 600; }

  /* 탭별 활성 border 색상 (뉴스=파랑, AI이슈=보라, 주식=초록) */
  .hnav-tab[data-section="news"].active     { border-bottom-color: var(--color-blue-light); }
  .hnav-tab[data-section="ai-issue"].active { border-bottom-color: #a78bfa; }
  .hnav-tab[data-section="stock"].active    { border-bottom-color: var(--color-up); }
  .hnav-tab[data-section="archive"].active  { border-bottom-color: var(--color-blue-light); }

  /* ── 허브 섹션 카드 ── */
  .hub-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
  }
  .hub-section-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 10px;
    padding: 20px 22px;
    text-decoration: none;
    color: var(--color-text);
    transition: border-color .15s, box-shadow .15s;
    display: block;
  }
  .hub-section-card:hover {
    border-color: var(--color-blue);
    box-shadow: 0 2px 8px rgba(0,0,0,.08);
  }
  .section-abbr {
    display: inline-block;
    font-family: ui-monospace, monospace;
    font-size: .68rem; font-weight: 700; letter-spacing: .1em;
    color: var(--color-blue);
    border: 1px solid var(--color-blue-200);
    background: var(--color-blue-50);
    padding: 2px 6px; border-radius: 3px;
    margin-bottom: 10px;
  }
  .hub-section-card h3 { color: var(--color-navy); margin: 0 0 4px;
    font-size: .95rem; font-weight: 700; }
  .hub-section-card p { color: var(--color-muted); font-size: .85rem; margin: 0; }

  /* ── 컨테이너 ── */
  .container { max-width: 860px; margin: 0 auto; padding: 36px 20px 80px; }

  /* ── 카드 ── */
  .card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }

  /* ── 타이포그래피 ── */
  h1 {
    font-size: 1.5rem; color: var(--color-navy);
    font-weight: 800; line-height: 1.25; margin-bottom: 8px;
  }
  .section-kicker {
    font-size: 10px; font-weight: 700; letter-spacing: .18em;
    text-transform: uppercase; color: var(--color-blue);
    display: block; margin-bottom: 2px; font-family: ui-monospace, monospace;
  }
  h2 {
    font-size: 1.15rem; color: var(--color-navy); margin: 2em 0 .6em;
    padding-bottom: 6px; border-bottom: 2px solid var(--color-navy);
    font-weight: 700; line-height: 1.3;
  }
  h3 {
    font-size: .97rem; color: var(--color-navy);
    margin: 1.3em 0 .4em; font-weight: 600;
  }
  p  { margin-bottom: .85em; }
  a  { color: var(--color-blue); text-underline-offset: 2px; }
  ul, ol { padding-left: 1.4em; margin-bottom: .85em; }
  li { margin-bottom: .3em; }
  hr { border: none; border-top: 1px solid var(--color-border); margin: 1.8em 0; }
  code {
    background: var(--color-code-bg); padding: 2px 6px;
    border-radius: 4px; font-size: .87em;
    font-family: ui-monospace, monospace;
  }
  blockquote {
    border-left: 3px solid var(--color-blue);
    padding: 8px 16px;
    background: var(--color-blue-50);
    border-radius: 0 6px 6px 0;
    margin: 1em 0;
    color: var(--color-muted);
  }
  mark { background: #fef08a; border-radius: 2px; padding: 0 2px; }
  table { border-collapse: collapse; width: 100%; margin: 1em 0; }
  th, td { border: 1px solid var(--color-border); padding: 8px 12px;
           text-align: left; font-size: .88rem; }
  th { background: var(--color-blue-50); color: var(--color-navy); font-weight: 600; }

  /* ── 태그 (배지 대체 — 이모지 없이, 모노스페이스) ── */
  .tag-row { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 20px; }
  .tag {
    font-size: 11px; font-weight: 600; letter-spacing: .05em;
    border: 1px solid var(--color-border);
    padding: 3px 9px; border-radius: 4px;
    color: var(--color-muted);
    font-family: ui-monospace, monospace;
    white-space: nowrap;
    background: var(--color-bg);
  }
  .tag-up   { background: var(--color-up-50);   color: var(--color-up);
              border-color: var(--color-up-200); }
  .tag-down { background: var(--color-down-50); color: var(--color-down);
              border-color: var(--color-down-200); }

  /* 구버전 .badge 호환 */
  .meta { display: flex; flex-wrap: wrap; gap: 7px; margin-bottom: 20px; }
  .badge { font-size: 11px; font-weight: 600; border: 1px solid var(--color-border);
    padding: 3px 9px; border-radius: 4px; color: var(--color-muted);
    font-family: ui-monospace, monospace; background: var(--color-bg); }
  .badge-green { background: var(--color-up-50);   color: var(--color-up);
                 border-color: var(--color-up-200); }
  .badge-orange { background: var(--color-down-50); color: var(--color-down);
                  border-color: var(--color-down-200); }

  /* ── 온도 인디케이터 (주식 전용) ── */
  .temp-indicator {
    display: inline-block;
    font-size: 11px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; padding: 4px 12px;
    border: 1.5px solid var(--color-border); border-radius: 4px;
    font-family: ui-monospace, monospace; margin-bottom: 16px;
  }
  .temp-neutral  { color: var(--color-muted); }
  .temp-risk-on  { background: var(--color-up-50);   color: var(--color-up);
                   border-color: var(--color-up-200); }
  .temp-risk-off { background: var(--color-down-50); color: var(--color-down);
                   border-color: var(--color-down-200); }

  /* 주식 수치 색상 */
  .change-pos { color: var(--color-up);   font-weight: 600; }
  .change-neg { color: var(--color-down); font-weight: 600; }

  /* ── 뉴스 목록 ── */
  .news-label {
    display: inline-block; font-size: .72rem; font-weight: 600;
    background: var(--color-bg); color: var(--color-muted);
    border: 1px solid var(--color-border);
    padding: 1px 6px; border-radius: 3px; margin-right: 6px;
    font-family: ui-monospace, monospace; white-space: nowrap;
  }

  /* ── 아카이브 목록 ── */
  .archive-list { list-style: none; padding: 0; }
  .archive-list li { border-bottom: 1px solid var(--color-border); padding: 12px 0; }
  .archive-list li:last-child { border-bottom: none; }
  .archive-list a { font-weight: 500; font-size: .95rem; text-decoration: none;
                    color: var(--color-text); }
  .archive-list a:hover { color: var(--color-blue); }
  .archive-list .date { color: var(--color-muted); font-size: .82rem;
    margin-top: 2px; font-family: ui-monospace, monospace; }

  /* 아카이브 검색 타입 배지 */
  .arc-result { padding: 8px 0; border-bottom: 1px solid var(--color-border);
    font-size: .88rem; line-height: 1.55; }
  .arc-result:last-child { border-bottom: none; }
  .arc-type { display: inline-block; font-size: .68rem; font-weight: 700;
    padding: 1px 5px; border-radius: 3px; margin-right: 4px;
    vertical-align: middle; font-family: ui-monospace, monospace;
    letter-spacing: .05em; }
  .arc-type-news  { background: var(--color-blue-50);  color: var(--color-blue);
                    border: 1px solid var(--color-blue-200); }
  .arc-type-ai    { background: #f5f3ff; color: #5b21b6;
                    border: 1px solid #ddd6fe; }
  .arc-type-stock { background: var(--color-up-50);    color: var(--color-up);
                    border: 1px solid var(--color-up-200); }
  .arc-date { font-family: ui-monospace, monospace; font-size: .76rem;
    color: var(--color-muted); margin-right: 4px; }
  .arc-date a { color: var(--color-muted); text-decoration: none; }
  .arc-label { display: inline-block; font-size: .68rem; background: var(--color-bg);
    color: var(--color-muted); border: 1px solid var(--color-border);
    border-radius: 3px; padding: 1px 5px; margin-left: 5px; }
  .arc-result a { color: var(--color-text); text-decoration: none; }
  .arc-result a:hover { text-decoration: underline; }

  /* ── 푸터 ── */
  footer {
    text-align: center;
    color: var(--color-muted);
    font-size: .8rem;
    padding: 24px;
    border-top: 1px solid var(--color-border);
    line-height: 1.7;
  }

  @media (max-width: 600px) {
    .card { padding: 18px 16px; }
    header .logo { font-size: .95rem; }
    .hub-sections { grid-template-columns: 1fr 1fr; }
  }
"""


# ── Jinja2 환경 ───────────────────────────────────────────────────────────────

def _jinja_env():
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(str(_TEMPLATES)), autoescape=False)


def _font_link(tokens: dict) -> str:
    cdn = tokens.get("meta", {}).get("font_cdn", "")
    if not cdn:
        return ""
    return (f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'  <link rel="stylesheet" href="{cdn}" crossorigin>')


# ── 뉴스 파싱 헬퍼 ────────────────────────────────────────────────────────────

def _split_at_news_list(md_html: str) -> str:
    m = re.search(r'<h2[^>]*>.*?📋.*?수집 기사', md_html)
    if m:
        return md_html[:m.start()]
    return md_html


def _split_analysis_sections(md_html: str) -> tuple[str, str, str]:
    """md_html을 해외/국내/키워드 세 섹션으로 분리.
    Returns: (analysis_en_html, analysis_ko_html, keyword_html)
    """
    analysis = _split_at_news_list(md_html)

    en_m  = re.search(r'(<h2[^>]*>.*?🌐.*?</h2>)', analysis)
    ko_m  = re.search(r'(<h2[^>]*>.*?🇰🇷.*?</h2>)', analysis)
    kw_m  = re.search(r'(<h2[^>]*>.*?🔍.*?</h2>)', analysis)

    def _slice(start_m, end_m) -> str:
        if not start_m:
            return ""
        s = start_m.start()
        e = end_m.start() if end_m else len(analysis)
        return analysis[s:e]

    en_html  = _slice(en_m,  ko_m  or kw_m)
    ko_html  = _slice(ko_m,  kw_m)
    kw_html  = _slice(kw_m,  None)
    return en_html, ko_html, kw_html


def _build_news_list_section(news_en: list[dict], news_ko: list[dict]) -> str:
    """커스텀 테마(editorial/terminal)에서 직접 뉴스 목록 HTML이 필요할 때 사용."""
    if not news_en and not news_ko:
        return ""

    def _items(items: list[dict]) -> str:
        return "\n".join(
            f'<li><span class="news-label">{n["label"]}</span>'
            f'<a href="{n["link"]}" target="_blank" rel="noopener">{n["title"]}</a></li>'
            for n in items
        )

    en_block = (
        f'<details>\n'
        f'  <summary>🌐 영어 뉴스 ({len(news_en)}건)</summary>\n'
        f'  <ul class="news-items">{_items(news_en)}</ul>\n'
        f'</details>'
    ) if news_en else ""

    ko_block = (
        f'<details>\n'
        f'  <summary>🇰🇷 한국어 뉴스 ({len(news_ko)}건)</summary>\n'
        f'  <ul class="news-items">{_items(news_ko)}</ul>\n'
        f'</details>'
    ) if news_ko else ""

    return f"""
  <div class="card news-list-section">
    <h2>📋 수집 기사 전체 목록</h2>
    {en_block}
    {ko_block}
  </div>"""


# ── 표준 렌더러 (classic/ink/forest 등 Jinja2 템플릿 사용) ────────────────────

def render_report(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    data   = ctx["data"]
    tmpl   = _jinja_env().get_template("web_news.html")
    en_html, ko_html, kw_html = _split_analysis_sections(ctx["md_html"])
    return tmpl.render(
        css_root=css_root_vars(tokens),
        css_common=_COMMON_CSS,
        font_link=_font_link(tokens),
        display_date=ctx["display_date"],
        date_str=ctx["date_str"],
        site_title=ctx["site_title"],
        site_logo_html=SITE_LOGO_HTML,
        now=ctx["now"],
        nav=nav_html("news"),
        active_tab="news",
        nav_prefix="../",
        stats=data["stats"],
        analysis_html=_split_at_news_list(ctx["md_html"]),
        analysis_en_html=en_html,
        analysis_ko_html=ko_html,
        keyword_section_html=kw_html,
        news_en=data.get("news_en", []),
        news_ko=data.get("news_ko", []),
        footer=FOOTER_CONFIG,
        site_url=ctx.get("site_url", ""),
    )


def render_archive(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    tmpl   = _jinja_env().get_template("web_archive.html")
    return tmpl.render(
        css_root=css_root_vars(tokens),
        css_common=_COMMON_CSS,
        font_link=_font_link(tokens),
        display_date="전체 목록",
        site_title=ctx["site_title"],
        site_logo_html=SITE_LOGO_HTML,
        now=ctx["now"],
        nav=nav_html("archive"),
        items=ctx["items"],
        stock_items=ctx.get("stock_items", []),
        ai_items=ctx.get("ai_items", []),
        footer=FOOTER_CONFIG,
        site_url=ctx.get("site_url", ""),
    )


def render_stock_report(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    data   = ctx.get("data", {})
    temp   = data.get("temperature", {})
    level  = temp.get("level", "neutral")
    temp_class = {
        "risk_off": "temp-risk-off",
        "neutral":  "temp-neutral",
        "risk_on":  "temp-risk-on",
    }.get(level, "temp-neutral")
    temp_label = {
        "risk_off": "▼ Risk-Off",
        "neutral":  "● Neutral",
        "risk_on":  "▲ Risk-On",
    }.get(level, "● Neutral")
    tmpl = _jinja_env().get_template("web_stock.html")
    return tmpl.render(
        css_root=css_root_vars(tokens),
        css_common=_COMMON_CSS,
        font_link=_font_link(tokens),
        display_date=ctx["display_date"],
        date_str=ctx["date_str"],
        site_title=ctx["site_title"],
        site_logo_html=SITE_LOGO_HTML,
        now=ctx["now"],
        nav=nav_html("stock", "../"),
        active_tab="stock",
        nav_prefix="../",
        md_html=ctx["md_html"],
        temp_label=temp_label,
        temp_class=temp_class,
        footer=FOOTER_CONFIG,
    )


def render_stock_archive(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    tmpl   = _jinja_env().get_template("web_stock_archive.html")
    return tmpl.render(
        css_root=css_root_vars(tokens),
        css_common=_COMMON_CSS,
        font_link=_font_link(tokens),
        display_date="주식 시황 전체 목록",
        site_title=ctx["site_title"],
        site_logo_html=SITE_LOGO_HTML,
        now=ctx["now"],
        nav=nav_html("stock", "../"),
        items=ctx["items"],
        footer=FOOTER_CONFIG,
    )
