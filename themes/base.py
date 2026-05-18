# themes/base.py
"""
토큰 기반 공통 레이아웃 & 렌더링 빌더.

모든 테마는 이 모듈의 함수를 사용하거나 오버라이드한다.
CSS 변수(웹)와 인라인 스타일(이메일) 모두 THEME_TOKENS에서 값을 읽어
하드코딩을 제거한다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.theme_config import NAV_SECTIONS, HUB_SECTIONS, THEME_TOKENS


# ── 토큰 조회 ──────────────────────────────────────────────────────────────────

def get_tokens(theme_name: str) -> dict:
    return THEME_TOKENS.get(theme_name, THEME_TOKENS["classic"])


# ── CSS 생성 ───────────────────────────────────────────────────────────────────

def css_root_vars(tokens: dict) -> str:
    """CSS :root 변수 블록. 이름은 MS Design System 토큰과 동일."""
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
    --font-sans:         {t['font_sans']};
    --leading-base:      {t['leading']};
  }}"""


def common_css() -> str:
    """테마 중립 구조 CSS. 색상은 CSS 변수를 통해 테마가 결정."""
    return """
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
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 58px;
    position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
  }
  header .logo { font-size: 1.15rem; font-weight: 700; letter-spacing: -.3px; }
  header .logo .accent { color: var(--color-blue-light); }
  header nav a {
    color: rgba(255,255,255,.8);
    text-decoration: none;
    margin-left: 20px;
    font-size: .9rem;
    transition: color .15s;
  }
  header nav a:hover,
  header nav a.active { color: #fff; font-weight: 600; }

  /* ── 컨테이너 ── */
  .container { max-width: 860px; margin: 0 auto; padding: 36px 20px 80px; }

  /* ── 카드 ── */
  .card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 32px 36px;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
  }

  /* ── 타이포그래피 ── */
  h1 { font-size: 1.6rem; color: var(--color-navy); margin-bottom: 6px;
       font-weight: 700; line-height: 1.3; }
  h2 { font-size: 1.2rem; color: var(--color-blue); margin: 2em 0 .6em;
       padding-bottom: 6px; border-bottom: 2px solid var(--color-border);
       font-weight: 600; }
  h3 { font-size: 1rem; color: var(--color-navy); margin: 1.4em 0 .4em;
       font-weight: 600; }
  p  { margin-bottom: .9em; }
  a  { color: var(--color-blue); text-underline-offset: 2px; }
  ul, ol { padding-left: 1.4em; margin-bottom: .9em; }
  li { margin-bottom: .3em; }
  hr { border: none; border-top: 1px solid var(--color-border); margin: 2em 0; }
  code { background: var(--color-code-bg); padding: 2px 6px;
         border-radius: 4px; font-size: .88em; }
  blockquote {
    border-left: 4px solid var(--color-blue);
    padding: 8px 16px;
    background: var(--color-blue-50);
    border-radius: 0 8px 8px 0;
    margin: 1em 0;
    color: var(--color-muted);
  }
  mark { background: #fef08a; border-radius: 2px; padding: 0 2px; }

  /* ── 배지 ── */
  .meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 24px; }
  .badge {
    background: var(--color-blue-50);
    color: var(--color-blue);
    border: 1px solid var(--color-blue-200);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: .78rem;
    font-weight: 500;
  }
  .badge-green {
    background: var(--color-green-50);
    color: var(--color-green);
    border: 1px solid var(--color-green-200);
  }
  .badge-orange {
    background: var(--color-orange-50);
    color: var(--color-orange);
    border: 1px solid var(--color-orange-200);
  }

  /* ── 아카이브 목록 ── */
  .archive-list { list-style: none; padding: 0; }
  .archive-list li { border-bottom: 1px solid var(--color-border); padding: 14px 0; }
  .archive-list li:last-child { border-bottom: none; }
  .archive-list a { font-weight: 500; font-size: 1rem; text-decoration: none; }
  .archive-list a:hover { text-decoration: underline; }
  .archive-list .date { color: var(--color-muted); font-size: .85rem; margin-top: 2px; }

  /* ── 허브 섹션 카드 (Phase 2/3 활성화) ── */
  .hub-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }
  .hub-section-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 24px;
    text-decoration: none;
    color: var(--color-text);
    transition: border-color .15s, box-shadow .15s;
    display: block;
  }
  .hub-section-card:hover {
    border-color: var(--color-blue);
    box-shadow: 0 2px 8px rgba(0,0,0,.1);
  }
  .hub-section-card .section-icon { font-size: 2rem; margin-bottom: 10px; display: block; }
  .hub-section-card h3 { color: var(--color-navy); margin: 0 0 6px; }
  .hub-section-card p { color: var(--color-muted); font-size: .9rem; margin: 0; }

  /* ── 푸터 ── */
  footer {
    text-align: center;
    color: var(--color-muted);
    font-size: .8rem;
    padding: 24px;
    border-top: 1px solid var(--color-border);
  }

  /* ── 반응형 ── */
  @media (max-width: 600px) {
    .card { padding: 20px; }
    header .logo { font-size: 1rem; }
    .hub-sections { grid-template-columns: 1fr; }
  }
"""


# ── HTML 컴포넌트 ──────────────────────────────────────────────────────────────

def nav_html(active_key: str, nav_prefix: str = "") -> str:
    """활성 섹션에 .active 클래스, disabled 항목은 렌더링 제외.
    nav_prefix: 하위 폴더 페이지에서 루트 기준 경로 보정 (예: "../")
    """
    enabled = [s for s in NAV_SECTIONS if s["enabled"]]
    parts = []
    for s in enabled:
        cls = ' class="active"' if active_key == s["key"] else ""
        parts.append(f'<a href="{nav_prefix}{s["url"]}"{cls}>{s["label"]}</a>')
    return "\n      ".join(parts)


def hub_sections_html(nav_prefix: str = "") -> str:
    """허브 페이지용 섹션 카드 그리드. Phase 2/3 활성화 시 표시."""
    active = [s for s in HUB_SECTIONS if s["enabled"]]
    if not active:
        return ""
    cards = "".join(f"""
    <a href="{nav_prefix}{s['url']}" class="hub-section-card">
      <span class="section-icon">{s['icon']}</span>
      <h3>{s['label']}</h3>
      <p>{s['desc']}</p>
    </a>""" for s in active)
    return f'<div class="hub-sections">{cards}\n  </div>'


def subscribe_card_html(subscribe_url: str) -> str:
    return f"""
  <div class="card subscribe-card">
    <h3>📬 뉴스레터 구독</h3>
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


# ── 페이지 레이아웃 ────────────────────────────────────────────────────────────

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
    """
    완전한 HTML 페이지 생성.
    extra_css  : 테마별 CSS 오버라이드.
    nav_prefix : 하위 폴더 페이지의 경로 보정 (예: stock/ 에서 "../").
    """
    font_cdn = tokens.get("meta", {}).get("font_cdn", "")
    font_link = (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        f'  <link rel="stylesheet" href="{font_cdn}" crossorigin>'
        if font_cdn else ""
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI가 매일 자동으로 수집·분석하는 글로벌 뉴스 브리핑">
  <title>{title} — {site_title}</title>
  {font_link}
  <style>
  {css_root_vars(tokens)}
  {common_css()}
  {extra_css}
  </style>
</head>
<body>
  <header>
    <div class="logo">📰 AI <span class="accent">News</span> Daily</div>
    <nav>
      {nav_html(active, nav_prefix)}
    </nav>
  </header>

  <div class="container">
    {body}
  </div>

  <footer>
    Powered by GitHub Actions · RSS Feeds<br>
    매일 자동 업데이트 · 생성: {now} KST
  </footer>
</body>
</html>"""


# ── 뉴스 렌더 헬퍼 ───────────────────────────────────────────────────────────

_NEWS_EXTRA_CSS = """
  /* ── 수집 기사 전체 목록 접기/펼치기 ── */
  .news-list-section h2 { margin-top: 0; }
  .news-list-section details {
    border: 1px solid var(--color-border);
    border-radius: 8px;
    margin-bottom: 12px;
    overflow: hidden;
  }
  .news-list-section summary {
    padding: 13px 18px;
    cursor: pointer;
    font-weight: 600;
    font-size: .92rem;
    color: var(--color-navy);
    background: var(--color-bg);
    list-style: none;
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
  }
  .news-list-section summary::-webkit-details-marker { display: none; }
  .news-list-section summary::after {
    content: "▼";
    font-size: .72rem;
    color: var(--color-muted);
    transition: transform .2s;
  }
  .news-list-section details[open] summary::after { transform: rotate(180deg); }
  .news-list-section details[open] summary {
    border-bottom: 1px solid var(--color-border);
  }
  .news-list-section .news-items {
    list-style: none;
    padding: 6px 0;
    margin: 0;
  }
  .news-list-section .news-items li {
    padding: 6px 18px;
    border-bottom: 1px solid var(--color-border);
    font-size: .86rem;
    line-height: 1.55;
    margin: 0;
  }
  .news-list-section .news-items li:last-child { border-bottom: none; }
  .news-label {
    display: inline-block;
    font-size: .73rem;
    background: var(--color-blue-50);
    color: var(--color-blue);
    padding: 1px 6px;
    border-radius: 4px;
    margin-right: 6px;
    font-weight: 500;
    white-space: nowrap;
  }
"""


def _split_at_news_list(md_html: str) -> str:
    """md_html 에서 '## 📋 수집 기사 전체 목록' 이후 부분을 제거하고 반환."""
    # markdown2 가 생성하는 h2 태그 패턴 (id 여부 무관)
    m = re.search(r'<h2[^>]*>.*?📋.*?수집 기사', md_html)
    if m:
        return md_html[:m.start()]
    return md_html


def _build_news_list_section(news_en: list[dict], news_ko: list[dict]) -> str:
    """수집 기사 전체 목록 카드 — EN 기본 표시, KO 기본 접힘."""
    if not news_en and not news_ko:
        return ""

    def _items(items: list[dict]) -> str:
        return "\n".join(
            f'<li><span class="news-label">{n["label"]}</span>'
            f'<a href="{n["link"]}" target="_blank" rel="noopener">{n["title"]}</a></li>'
            for n in items
        )

    en_block = (
        f'<details open>\n'
        f'  <summary>🌐 영어 뉴스 ({len(news_en)}건)</summary>\n'
        f'  <ul class="news-items">{_items(news_en)}</ul>\n'
        f'</details>'
    ) if news_en else ""

    ko_block = (
        f'<details>\n'
        f'  <summary>🇰🇷 한국어 뉴스 ({len(news_ko)}건) — 클릭하여 펼치기</summary>\n'
        f'  <ul class="news-items">{_items(news_ko)}</ul>\n'
        f'</details>'
    ) if news_ko else ""

    return f"""
  <div class="card news-list-section">
    <h2>📋 수집 기사 전체 목록</h2>
    {en_block}
    {ko_block}
  </div>"""


# ── 표준 렌더러 (classic / ink / forest 등 토큰 교체형 테마에서 공유) ─────────

def render_report(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    s = ctx["data"]["stats"]
    hub = hub_sections_html()
    badges = f"""
    <div class="meta">
      <span class="badge">📅 {ctx['display_date']}</span>
      <span class="badge badge-orange">🤖 AI분석 {s['sent_to_ai']}건</span>
      <span class="badge badge-green">🇰🇷 KO {s['ko']}</span>
      <span class="badge">🌐 EN {s['en']}</span>
    </div>"""

    # 분석 섹션만 (## 📋 수집 기사 전체 목록 이후 제거)
    analysis_html = _split_at_news_list(ctx['md_html'])
    news_section  = _build_news_list_section(
        ctx['data'].get('news_en', []),
        ctx['data'].get('news_ko', []),
    )

    body = f"""
  {hub}
  <div class="card">
    <h1>📰 Daily News Brief</h1>
    {badges}
    {analysis_html}
  </div>
  {news_section}"""
    return layout_html(ctx['display_date'], body, "news",
                       ctx['site_title'], ctx['now'], tokens,
                       extra_css=_NEWS_EXTRA_CSS)


def render_archive(ctx: dict, theme_name: str) -> str:
    tokens = get_tokens(theme_name)
    items = "".join(f"""
    <li>
      <a href="{it['date']}.html">📄 {it['display']} 리포트</a>
      <div class="date">{it['date']}</div>
    </li>""" for it in ctx['items'])
    body = f"""
  <div class="card">
    <h1>📚 전체 리포트 목록</h1>
    <p style="color:var(--color-muted);margin:.5em 0 1.5em">
      총 {len(ctx['items'])}개 리포트
    </p>
    <ul class="archive-list">{items}</ul>
  </div>"""
    return layout_html("전체 목록", body, "archive",
                       ctx['site_title'], ctx['now'], tokens)


# ── 주식 시황 렌더러 ──────────────────────────────────────────────────────────

_TEMP_BADGE_COLORS = {
    "risk_off": ("orange", "badge-orange"),
    "neutral":  ("blue",   "badge"),
    "risk_on":  ("green",  "badge-green"),
}

_STOCK_EXTRA_CSS = """
  /* ── 주식 시황 전용 CSS ── */
  .change-pos { color: var(--color-green); font-weight: 600; }
  .change-neg { color: var(--color-orange); font-weight: 600; }
  .temp-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 16px; border-radius: 24px; font-weight: 700;
    font-size: 1rem; margin-bottom: 16px;
  }
  .temp-risk-off { background: var(--color-orange-50); color: var(--color-orange);
                   border: 1.5px solid var(--color-orange-200); }
  .temp-neutral  { background: var(--color-blue-50);   color: var(--color-blue);
                   border: 1.5px solid var(--color-blue-200); }
  .temp-risk-on  { background: var(--color-green-50);  color: var(--color-green);
                   border: 1.5px solid var(--color-green-200); }
"""


def render_stock_report(ctx: dict, theme_name: str) -> str:
    """주식 시황 리포트 전용 렌더러."""
    tokens = get_tokens(theme_name)
    data   = ctx.get("data", {})
    temp   = data.get("temperature", {})
    level  = temp.get("level", "neutral")
    temp_class = {"risk_off": "temp-risk-off", "neutral": "temp-neutral", "risk_on": "temp-risk-on"}.get(level, "temp-neutral")
    temp_display = temp.get("display", "🟡 중립")

    hub = hub_sections_html("../")
    badges = f"""
    <div class="meta">
      <span class="badge">📅 {ctx['display_date']}</span>
      <span class="temp-badge {temp_class}">{temp_display}</span>
    </div>"""
    body = f"""
  {hub}
  <div class="card">
    <h1>📊 주식 시황 브리핑</h1>
    {badges}
    {ctx['md_html']}
  </div>"""
    return layout_html(
        ctx['display_date'], body, "stock",
        ctx['site_title'], ctx['now'], tokens,
        extra_css=_STOCK_EXTRA_CSS,
        nav_prefix="../",
    )


def render_stock_archive(ctx: dict, theme_name: str) -> str:
    """주식 시황 아카이브 전용 렌더러."""
    tokens = get_tokens(theme_name)
    items  = "".join(f"""
    <li>
      <a href="{it['date']}.html">📊 {it['display']} 시황</a>
      <div class="date">{it['date']}</div>
    </li>""" for it in ctx['items'])
    body = f"""
  <div class="card">
    <h1>📚 주식 시황 전체 목록</h1>
    <p style="color:var(--color-muted);margin:.5em 0 1.5em">
      총 {len(ctx['items'])}개 리포트
    </p>
    <ul class="archive-list">{items}</ul>
  </div>"""
    return layout_html("주식 시황 목록", body, "stock",
                       ctx['site_title'], ctx['now'], tokens,
                       nav_prefix="../")


def render_stock_email(ctx: dict, theme_name: str) -> str:
    """주식 시황 이메일 전용 렌더러 (인라인 스타일)."""
    tokens = get_tokens(theme_name)
    c = tokens["colors"]
    t = tokens["typography"]
    body_html  = ctx.get("email_html", ctx.get("md_html", ""))
    date_str   = ctx.get("display_date", "")
    site_url   = ctx.get("site_url", "#")
    unsub_url  = ctx.get("unsubscribe_url", "")
    unsub_link = (
        f'&nbsp;|&nbsp;<a href="{unsub_url}" style="color:{c["muted"]}">구독 취소</a>'
        if unsub_url else ""
    )
    data  = ctx.get("data", {})
    temp  = data.get("temperature", {})
    level = temp.get("level", "neutral")
    temp_bg  = {"risk_off": c["orange_50"], "neutral": c["blue_50"],  "risk_on": c["green_50"]}.get(level, c["blue_50"])
    temp_fg  = {"risk_off": c["orange"],    "neutral": c["blue"],     "risk_on": c["green"]}.get(level, c["blue"])
    temp_bd  = {"risk_off": c["orange_200"],"neutral": c["blue_200"], "risk_on": c["green_200"]}.get(level, c["blue_200"])
    temp_txt = temp.get("display", "🟡 중립")

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <style>
    body {{ margin:0; padding:0; }}
    a  {{ color:{c['blue']}; }}
    h2 {{ color:{c['navy']}; }}
    h3 {{ color:{c['navy']}; }}
    ul {{ padding-left:1.4em; margin-bottom:.9em; }}
    li {{ margin-bottom:.3em; }}
    blockquote {{ border-left:4px solid {c['blue']};padding:8px 16px;
                  background:{c['blue_50']};border-radius:0 8px 8px 0;
                  margin:1em 0;color:{c['muted']}; }}
    table {{ border-collapse:collapse; width:100%; margin:1em 0; }}
    th, td {{ border:1px solid {c['border']}; padding:8px 12px;
               text-align:left; font-size:.9rem; }}
    th {{ background:{c['blue_50']}; color:{c['navy']}; font-weight:600; }}
  </style>
</head>
<body style="margin:0;padding:0;background:{c['bg']};
             font-family:{t['font_sans']};color:{c['text']};line-height:{t['leading']}">
  <div style="max-width:650px;margin:0 auto;padding:20px 16px">

    <!-- 헤더 -->
    <div style="background:{c['navy']};padding:14px 24px;border-radius:12px 12px 0 0">
      <span style="color:#fff;font-weight:700;font-size:1.05rem">
        📊 주식 시황 <span style="color:{c['blue_light']}">브리핑</span>
      </span>
    </div>

    <!-- 본문 카드 -->
    <div style="background:{c['card']};border:1px solid {c['border']};
                border-top:none;border-radius:0 0 12px 12px;padding:28px 32px">

      <!-- 날짜 + 온도계 배지 -->
      <div style="margin-bottom:20px">
        <span style="background:{c['blue_50']};color:{c['blue']};
                     border:1px solid {c['blue_200']};padding:3px 10px;
                     border-radius:20px;font-size:.78rem;font-weight:500">
          📅 {date_str}
        </span>
        <span style="background:{temp_bg};color:{temp_fg};
                     border:1.5px solid {temp_bd};padding:4px 12px;
                     border-radius:20px;font-size:.85rem;font-weight:700;margin-left:8px">
          {temp_txt}
        </span>
      </div>

      <!-- 분석 본문 -->
      <div style="font-size:15px;line-height:{t['leading']}">
        {body_html}
      </div>

      <!-- CTA -->
      <div style="text-align:center;margin-top:32px;padding-top:24px;
                  border-top:1px solid {c['border']}">
        <a href="{site_url}/stock/"
           style="display:inline-block;background:{c['blue']};color:#fff;
                  text-decoration:none;padding:11px 28px;border-radius:8px;
                  font-weight:600;font-size:.95rem">
          웹에서 전체 시황 보기 →
        </a>
      </div>
    </div>

    <!-- 푸터 -->
    <p style="text-align:center;color:{c['muted']};font-size:.75rem;margin:14px 0 0">
      주식 시황 브리핑 — {date_str}{unsub_link}
    </p>
    <p style="text-align:center;color:{c['muted']};font-size:.7rem;margin:4px 0 0">
      ※ 투자 권유 아님. AI 자동 분석 참고용.
    </p>
  </div>
</body>
</html>"""


# ── 이메일 렌더러 ──────────────────────────────────────────────────────────────

def render_email(ctx: dict, theme_name: str) -> str:
    """
    이메일 전용 HTML.
    Gmail/Outlook은 CSS 변수를 지원하지 않으므로 인라인 스타일로 생성.
    THEME_TOKENS의 동일 색상값을 사용해 웹과 동일한 브랜드 느낌 유지.
    """
    tokens = get_tokens(theme_name)
    c = tokens["colors"]
    t = tokens["typography"]
    body_html   = ctx.get("email_html", ctx.get("md_html", ""))
    date_str    = ctx.get("display_date", "")
    site_url    = ctx.get("site_url", "#")
    unsub_url   = ctx.get("unsubscribe_url", "")
    unsub_link  = (
        f'&nbsp;|&nbsp;<a href="{unsub_url}" style="color:{c["muted"]}">구독 취소</a>'
        if unsub_url else ""
    )

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <style>
    /* 최소 인라인 CSS — Gmail 클리핑 방지 */
    body {{ margin:0; padding:0; }}
    a {{ color:{c['blue']}; }}
    h2 {{ color:{c['navy']}; }}
    h3 {{ color:{c['navy']}; }}
    ul {{ padding-left:1.4em; margin-bottom:.9em; }}
    li {{ margin-bottom:.3em; }}
    blockquote {{ border-left:4px solid {c['blue']};padding:8px 16px;
                  background:{c['blue_50']};border-radius:0 8px 8px 0;
                  margin:1em 0;color:{c['muted']}; }}
  </style>
</head>
<body style="margin:0;padding:0;background:{c['bg']};
             font-family:{t['font_sans']};color:{c['text']};line-height:{t['leading']}">
  <div style="max-width:650px;margin:0 auto;padding:20px 16px">

    <!-- 헤더 바 -->
    <div style="background:{c['navy']};padding:14px 24px;
                border-radius:12px 12px 0 0">
      <span style="color:#fff;font-weight:700;font-size:1.05rem">
        📰 AI <span style="color:{c['blue_light']}">News</span> Daily
      </span>
    </div>

    <!-- 본문 카드 -->
    <div style="background:{c['card']};border:1px solid {c['border']};
                border-top:none;border-radius:0 0 12px 12px;padding:28px 32px">

      <!-- 날짜 배지 행 -->
      <div style="margin-bottom:20px">
        <span style="background:{c['blue_50']};color:{c['blue']};
                     border:1px solid {c['blue_200']};padding:3px 10px;
                     border-radius:20px;font-size:.78rem;font-weight:500">
          📅 {date_str}
        </span>
        <span style="background:{c['orange_50']};color:{c['orange']};
                     border:1px solid {c['orange_200']};padding:3px 10px;
                     border-radius:20px;font-size:.78rem;font-weight:500;margin-left:6px">
          🤖 AI 자동 분석
        </span>
      </div>

      <!-- 뉴스 분석 본문 (analysis 섹션만, 전체 목록 제외) -->
      <div style="font-size:15px;line-height:{t['leading']}">
        {body_html}
      </div>

      <!-- CTA 버튼 -->
      <div style="text-align:center;margin-top:32px;padding-top:24px;
                  border-top:1px solid {c['border']}">
        <a href="{site_url}"
           style="display:inline-block;background:{c['blue']};color:#fff;
                  text-decoration:none;padding:11px 28px;border-radius:8px;
                  font-weight:600;font-size:.95rem">
          웹에서 전체 기사 보기 →
        </a>
      </div>
    </div>

    <!-- 푸터 -->
    <p style="text-align:center;color:{c['muted']};font-size:.75rem;margin:14px 0 0">
      AI News Daily — {date_str}{unsub_link}
    </p>
  </div>
</body>
</html>"""
