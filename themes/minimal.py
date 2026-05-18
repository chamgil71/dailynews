# themes/minimal.py
"""
Minimal 테마 — Pretendard, 넓은 여백, 깔끔한 prose.
base 레이아웃 사용 + CSS 오버라이드로 시각 차별화.
"""
from themes.base import (
    layout_html, get_tokens,
    subscribe_card_html, hub_sections_html,
    render_archive as _base_archive,
    render_email as _base_email,
    render_stock_report as _stock_report,
    render_stock_archive as _stock_archive,
    render_stock_email as _stock_email,
)

_NAME = "minimal"

# base common_css 이후에 적용되는 오버라이드
_EXTRA_CSS = """
  /* ── Minimal 오버라이드 ── */
  body { letter-spacing: -.01em; }
  .container { max-width: 720px; }

  /* 카드 — 더 넓은 여백 */
  .card { padding: 40px 48px; border-radius: 14px; }

  /* 타이포 오버라이드 */
  h1 { font-size: 2rem; letter-spacing: -.03em; font-weight: 800; }
  h2 { font-size: 1.25rem; font-weight: 700; letter-spacing: -.015em;
       padding-bottom: 12px; }
  h3 { font-size: 1.05rem; font-weight: 700; }

  /* 리스트 — accent 색 dot */
  ul { list-style: none; padding-left: 0; }
  ul li { position: relative; padding-left: 18px; margin-bottom: .5em; }
  ul li::before {
    content: '';
    position: absolute; left: 0; top: .58em;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--color-blue);
  }

  /* Blockquote — 배경 라운드, 왼쪽 바 없음 */
  blockquote {
    border-left: none;
    background: var(--color-blue-50);
    border-radius: 10px;
    padding: 16px 20px;
  }

  /* 구독 카드 */
  .subscribe-card { border-radius: 14px; }

  /* 통계 행 (Minimal 전용 컴포넌트) */
  .stats-row {
    display: flex;
    gap: 24px;
    padding: 18px 0;
    border-top: 1px solid var(--color-border);
    border-bottom: 1px solid var(--color-border);
    margin-bottom: 36px;
    font-size: .9rem;
  }
  .stats-row .stat-item { text-align: left; }
  .stats-row .stat-n {
    display: block;
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -.03em;
    color: var(--color-navy);
    line-height: 1;
    margin-bottom: 2px;
  }
  .stats-row .stat-l { color: var(--color-muted); font-size: .78rem; }

  /* Eyebrow 레이블 */
  .eyebrow {
    font-size: .75rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--color-blue);
    font-weight: 700;
    margin-bottom: 14px;
  }

  @media (max-width: 600px) {
    .card { padding: 24px 20px; }
    .stats-row { flex-wrap: wrap; gap: 16px; }
  }
"""


def render_report(ctx: dict) -> str:
    tokens = get_tokens(_NAME)
    s = ctx["data"]["stats"]
    hub = hub_sections_html()

    stats_row = f"""
    <div class="stats-row">
      <div class="stat-item">
        <span class="stat-n">{s['total']}</span>
        <span class="stat-l">수집 기사</span>
      </div>
      <div class="stat-item">
        <span class="stat-n">{s['sent_to_ai']}</span>
        <span class="stat-l">AI 분석</span>
      </div>
      <div class="stat-item">
        <span class="stat-n">{s['ko']}</span>
        <span class="stat-l">한국어</span>
      </div>
      <div class="stat-item">
        <span class="stat-n">{s['en']}</span>
        <span class="stat-l">영어</span>
      </div>
    </div>"""

    body = f"""
  {hub}
  <div class="card">
    <div class="eyebrow">{ctx['display_date']} · 오늘의 브리핑</div>
    <h1 style="margin-bottom:20px">Daily News Brief</h1>
    {stats_row}
    {ctx['md_html']}
  </div>
  {subscribe_card_html(ctx.get('subscribe_url', '#'))}"""

    return layout_html(ctx['display_date'], body, "news",
                       ctx['site_title'], ctx['now'], tokens, _EXTRA_CSS)


def render_archive(ctx: dict) -> str:
    tokens = get_tokens(_NAME)
    items = "".join(f"""
    <li style="display:flex;justify-content:space-between;align-items:center;
               padding:16px 0;border-bottom:1px solid var(--color-border)">
      <a href="{it['date']}.html"
         style="font-weight:600;text-decoration:none;color:var(--color-text)">
        {it['display']}
      </a>
      <span style="color:var(--color-muted);font-size:.85rem">{it['date']} →</span>
    </li>""" for it in ctx['items'])
    body = f"""
  <div class="card">
    <div class="eyebrow">아카이브 · {len(ctx['items'])}개 리포트</div>
    <h1 style="margin-bottom:32px">지나간 매일의 브리핑.</h1>
    <ul style="list-style:none;padding:0">{items}</ul>
  </div>"""
    return layout_html("아카이브", body, "archive",
                       ctx['site_title'], ctx['now'], tokens, _EXTRA_CSS)


def render_email(ctx: dict) -> str:
    return _base_email(ctx, _NAME)

def render_stock_report(ctx: dict) -> str:
    return _stock_report(ctx, _NAME)

def render_stock_archive(ctx: dict) -> str:
    return _stock_archive(ctx, _NAME)

def render_stock_email(ctx: dict) -> str:
    return _stock_email(ctx, _NAME)
