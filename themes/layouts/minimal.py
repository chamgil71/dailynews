# themes/layouts/minimal.py
"""Minimal 테마 — Pretendard, 넓은 여백, 오렌지 accent.

[커스텀 레이아웃 테마] base.py 미사용. render_*() 함수가 Python f-string으로 HTML 직접 생성.
레이아웃·색상 모두 이 파일에서 수정.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

TOKENS = {
    "meta": {
        "name":     "minimal",
        "label":    "Minimal",
        "desc":     "넓은 여백, 깔끔한 오렌지 포인트",
        "swatch_colors": ["#ffffff", "#ff5a1f"],
        "font_cdn": "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css",
        "font_family": "'Pretendard Variable', 'Pretendard', -apple-system, sans-serif",
    },
    "colors": {
        "blue":         "#ff5a1f",
        "blue_light":   "#ff8c00",
        "blue_50":      "#f1efe8",
        "blue_200":     "#e6e2da",
        "navy":         "#16181a",
        "bg":           "#fafaf7",
        "card":         "#ffffff",
        "border":       "#e6e2da",
        "text":         "#16181a",
        "muted":        "#8a8f95",
        "code_bg":      "#f1efe8",
        "green":        "#16a34a",
        "green_50":     "#f0fdf4",
        "green_200":    "#bbf7d0",
        "orange":       "#ea580c",
        "orange_50":    "#fff7ed",
        "orange_200":   "#fed7aa",
    },
    "typography": {
        "font_sans": "'Pretendard Variable', 'Pretendard', -apple-system, sans-serif",
        "leading":   1.75,
    },
}

from themes.base import (
    layout_html, get_tokens,
    subscribe_card_html, hub_sections_html,
    render_archive as _base_archive,
    render_stock_report as _stock_report,
    render_stock_archive as _stock_archive,
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

  /* ── 아카이브 검색 결과 ── */
  .arc-result { padding:10px 0; border-bottom:1px solid var(--color-border); font-size:.9rem; line-height:1.55; }
  .arc-result:last-child { border-bottom:none; }
  .arc-type { display:inline-block; font-size:.7rem; font-weight:700;
               padding:2px 6px; border-radius:4px; margin-right:6px; vertical-align:middle; text-transform:uppercase; }
  .arc-type-news  { background:var(--color-blue-50); color:var(--color-blue); }
  .arc-type-ai    { background:#ede9fe; color:#6d28d9; }
  .arc-type-stock { background:#dcfce7; color:#15803d; }
  .arc-date { font-family:var(--font-sans); font-size:.8rem; color:var(--color-muted); margin-right:6px; }
  .arc-date a { color:var(--color-muted); text-decoration:none; }
  .arc-label { display:inline-block; font-size:.7rem; background:var(--color-bg); color:var(--color-muted);
                border:1px solid var(--color-border); border-radius:4px; padding:2px 6px; margin-left:6px; }
  .arc-result a { color:var(--color-text); text-decoration:none; font-weight:600; }
  .arc-result a:hover { color:var(--color-blue); }
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
    
    news_items_html = "".join(f"""
    <li style="display:flex;justify-content:space-between;align-items:center;
               padding:16px 0;border-bottom:1px solid var(--color-border)">
      <a href="news/{it['date']}.html"
         style="font-weight:600;text-decoration:none;color:var(--color-text)">
        {it['display']}
      </a>
      <span style="color:var(--color-muted);font-size:.85rem">{it['date']} →</span>
    </li>""" for it in ctx.get('items', []))
    
    stock_items_html = "".join(f"""
    <li style="display:flex;justify-content:space-between;align-items:center;
               padding:16px 0;border-bottom:1px solid var(--color-border)">
      <a href="stock/{it['date']}.html"
         style="font-weight:600;text-decoration:none;color:var(--color-text)">
        {it['display']}
      </a>
      <span style="color:var(--color-muted);font-size:.85rem">{it['date']} →</span>
    </li>""" for it in ctx.get('stock_items', [])) or "<li style='color:var(--color-muted);padding:16px 0'>주식 리포트 없음</li>"
    
    ai_items_html = "".join(f"""
    <li style="display:flex;justify-content:space-between;align-items:center;
               padding:16px 0;border-bottom:1px solid var(--color-border)">
      <a href="ai-issue/{it['date']}.html"
         style="font-weight:600;text-decoration:none;color:var(--color-text)">
        {it['display']}
      </a>
      <span style="color:var(--color-muted);font-size:.85rem">{it['date']} →</span>
    </li>""" for it in ctx.get('ai_items', [])) or "<li style='color:var(--color-muted);padding:16px 0'>AI이슈 보고서 없음</li>"

    total = len(ctx.get('items', [])) + len(ctx.get('stock_items', [])) + len(ctx.get('ai_items', []))

    body = f"""
  <div class="card">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:20px;flex-wrap:wrap;margin-bottom:32px">
      <div>
        <div class="eyebrow">아카이브 · 총 {total}개 리포트</div>
        <h1 style="margin:0">지나간 매일의 브리핑.</h1>
      </div>
      <!-- 통합 검색 -->
      <div class="arch-search" style="flex:0 0 280px;min-width:200px">
        <div style="position:relative;margin-bottom:8px">
          <input id="arcSearchInput" type="text" placeholder="기사·이슈·시황 키워드…"
            style="width:100%;padding:10px 14px 10px 36px;border:1px solid var(--color-border);
                   border-radius:8px;background:var(--color-card);color:var(--color-text);
                   font-family:inherit;font-size:.9rem;outline:none;transition:border-color .15s;" 
            onfocus="this.style.borderColor='var(--color-blue)'"
            onblur="this.style.borderColor='var(--color-border)'" />
          <span style="position:absolute;left:11px;top:50%;transform:translateY(-50%);font-size:.95rem;pointer-events:none">🔍</span>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;font-size:.8rem;color:var(--color-muted)">
          <label style="display:flex;align-items:center;gap:4px;cursor:pointer">
            <input type="checkbox" id="arcSfNews" checked style="accent-color:var(--color-blue)"> 뉴스</label>
          <label style="display:flex;align-items:center;gap:4px;cursor:pointer">
            <input type="checkbox" id="arcSfAi" checked style="accent-color:var(--color-blue)"> AI이슈</label>
          <label style="display:flex;align-items:center;gap:4px;cursor:pointer">
            <input type="checkbox" id="arcSfStock" checked style="accent-color:var(--color-blue)"> 주식</label>
        </div>
        <div id="arcSearchResults"></div>
      </div>
    </div>

    <!-- 탭 스위치 -->
    <div style="margin-bottom:24px;border-bottom:1px solid var(--color-border);padding-bottom:8px;display:flex;gap:20px;">
      <button onclick="showTab('news')" id="tabNews" style="font-family:inherit;font-size:.95rem;padding:6px 0;border:none;border-bottom:2px solid var(--color-blue);background:none;cursor:pointer;color:var(--color-text);font-weight:700">뉴스 {len(ctx.get('items', []))}</button>
      <button onclick="showTab('stock')" id="tabStock" style="font-family:inherit;font-size:.95rem;padding:6px 0;border:none;border-bottom:2px solid transparent;background:none;cursor:pointer;color:var(--color-muted)">주식 {len(ctx.get('stock_items', []))}</button>
      <button onclick="showTab('ai')" id="tabAi" style="font-family:inherit;font-size:.95rem;padding:6px 0;border:none;border-bottom:2px solid transparent;background:none;cursor:pointer;color:var(--color-muted)">AI이슈 {len(ctx.get('ai_items', []))}</button>
    </div>

    <!-- 리스트 패널 -->
    <div id="tabPanelNews"><ul style="list-style:none;padding:0">{news_items_html}</ul></div>
    <div id="tabPanelStock" style="display:none"><ul style="list-style:none;padding:0">{stock_items_html}</ul></div>
    <div id="tabPanelAi" style="display:none"><ul style="list-style:none;padding:0">{ai_items_html}</ul></div>
  </div>

  <script>
  var _active = 'news';
  function showTab(t) {{
    ['news','stock','ai'].forEach(function(k) {{
      var cap = k.charAt(0).toUpperCase()+k.slice(1);
      var panel = document.getElementById('tabPanel'+cap);
      var tabBtn = document.getElementById('tab'+cap);
      if (panel) panel.style.display = k===t ? '' : 'none';
      if (tabBtn) {{
        tabBtn.style.borderBottom = k===t ? '2px solid var(--color-blue)' : '2px solid transparent';
        tabBtn.style.color = k===t ? 'var(--color-text)' : 'var(--color-muted)';
        tabBtn.style.fontWeight = k===t ? '700' : '400';
      }}
    }});
    _active = t;
  }}

  // 통합 검색
  var _searchIndex = null, _searchLoading = false;
  function _loadSearchIndex(cb) {{
    if (_searchIndex) {{ cb(_searchIndex); return; }}
    if (_searchLoading) {{ setTimeout(function() {{ _loadSearchIndex(cb); }}, 100); return; }}
    _searchLoading = true;
    fetch('search-index.json')
      .then(function(r) {{ return r.json(); }})
      .then(function(d) {{ _searchIndex = d; _searchLoading = false; cb(d); }})
      .catch(function() {{ _searchLoading = false; _searchIndex = []; cb([]); }});
  }}
  function _runSearch() {{
    var q   = document.getElementById('arcSearchInput').value.trim();
    var res = document.getElementById('arcSearchResults');
    var useNews  = document.getElementById('arcSfNews').checked;
    var useAi    = document.getElementById('arcSfAi').checked;
    var useStock = document.getElementById('arcSfStock').checked;
    if (q.length < 2) {{ res.innerHTML = ''; return; }}
    var ql = q.toLowerCase();
    _loadSearchIndex(function(index) {{
      var hits = [];
      index.forEach(function(report) {{
        var t = report.type || 'news';
        if (t === 'news'     && !useNews)  return;
        if (t === 'ai-issue' && !useAi)    return;
        if (t === 'stock'    && !useStock) return;
        report.articles.forEach(function(art) {{
          if (art.title.toLowerCase().indexOf(ql) >= 0) {{
            hits.push({{ type: t, date: report.date, display: report.display,
                         report_url: report.report_url, art: art }});
          }}
        }});
      }});
      if (!hits.length) {{
        res.innerHTML = '<p style="color:var(--color-muted);font-size:.85rem;padding:8px 0">검색 결과 없음</p>';
        return;
      }}
      var typeLabel = {{ news:'뉴스', 'ai-issue':'AI', stock:'주식' }};
      var typeCls   = {{ news:'arc-type-news', 'ai-issue':'arc-type-ai', stock:'arc-type-stock' }};
      var re = new RegExp('(' + q.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&') + ')', 'gi');
      var html = '<p style="font-size:.75rem;color:var(--color-muted);margin-bottom:8px;font-family:monospace">'
               + hits.length + '건 검색됨 (최대 100건)</p>';
      hits.slice(0, 100).forEach(function(h) {{
        var badge = '<span class="arc-type ' + typeCls[h.type] + '">' + typeLabel[h.type] + '</span>';
        var dateA = '<span class="arc-date"><a href="' + h.report_url + '">' + h.date + '</a></span>';
        var hiTitle = h.art.title.replace(re, '<mark style="background:#fef08a;border-radius:2px">$1</mark>');
        var titleA = h.art.link
          ? '<a href="' + h.art.link + '" target="_blank" rel="noopener">' + hiTitle + '</a>'
          : '<a href="' + h.report_url + '" target="_blank">' + hiTitle + '</a>';
        var label = h.art.label ? '<span class="arc-label">' + h.art.label + '</span>' : '';
        html += '<div class="arc-result">' + badge + dateA + titleA + label + '</div>';
      }});
      res.innerHTML = html;
    }});
  }}
  var _arcTimer;
  document.getElementById('arcSearchInput').addEventListener('input', function() {{
    clearTimeout(_arcTimer);
    _arcTimer = setTimeout(_runSearch, 280);
  }});
  ['arcSfNews','arcSfAi','arcSfStock'].forEach(function(id) {{
    document.getElementById(id).addEventListener('change', _runSearch);
  }});
  </script>
"""
    return layout_html("아카이브", body, "archive",
                       ctx['site_title'], ctx['now'], tokens, _EXTRA_CSS)


def render_stock_report(ctx: dict) -> str:
    return _stock_report(ctx, _NAME)

def render_stock_archive(ctx: dict) -> str:
    return _stock_archive(ctx, _NAME)
