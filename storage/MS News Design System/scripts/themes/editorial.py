# scripts/themes/editorial.py
# A시안 — 신문 마스트헤드, Noto Serif KR, 2단 컬럼, 드롭캡.

_FONTS = """
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700;800;900&family=IBM+Plex+Mono:wght@400;500;700&family=Pretendard:wght@400;500;700&display=swap" rel="stylesheet">
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

  /* Masthead */
  .masthead { border-top:6px solid var(--rule); border-bottom:1px solid var(--rule);
    padding:14px 0 12px; margin-bottom:22px; }
  .mh-top { display:flex; justify-content:space-between; align-items:baseline;
    font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.12em;
    color:var(--ink-soft); text-transform:uppercase;
    border-bottom:1px solid var(--rule-soft); padding-bottom:8px; margin-bottom:14px; }
  .mh-title { font-weight:900; font-size:84px; letter-spacing:-.04em;
    line-height:.92; text-align:center; margin:6px 0 2px; font-style:italic; }
  .mh-title em { color:var(--accent); font-style:italic; }
  .mh-tag { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.3em;
    text-align:center; color:var(--ink-soft); text-transform:uppercase;
    padding-top:6px; border-top:1px solid var(--rule-soft); margin-top:10px; }
  .mh-nav { display:flex; justify-content:center; gap:32px; margin-top:14px;
    font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.08em;
    text-transform:uppercase; }
  .mh-nav a { color:var(--ink-soft); text-decoration:none; }
  .mh-nav a.on { color:var(--accent); font-weight:700; border-bottom:2px solid var(--accent); padding-bottom:2px; }

  /* Briefing */
  .brief { display:grid; grid-template-columns:200px 1fr 160px; gap:24px;
    border-bottom:1px solid var(--rule); padding:18px 0 22px; margin-bottom:28px; }
  .brief-stats { font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--ink-soft); }
  .brief-stats .lbl { color:var(--ink); font-weight:700; display:block;
    margin-bottom:8px; letter-spacing:.08em; }
  .brief-stat { display:flex; gap:14px; align-items:baseline; margin-top:10px; }
  .brief-stat .num { font-family:'Noto Serif KR',serif; font-size:24px;
    font-weight:700; font-style:italic; }
  .brief-stat .lab { font-size:10px; letter-spacing:.15em; color:var(--ink-mute); text-transform:uppercase; }
  .kicker { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.2em;
    text-transform:uppercase; color:var(--accent); margin-bottom:8px;
    border-left:3px solid var(--accent); padding-left:12px; }
  .lede { font-size:22px; line-height:1.4; font-weight:500; text-wrap:balance; }
  .byline { font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--ink-mute);
    text-align:right; line-height:1.7; border-left:1px solid var(--rule-soft); padding-left:14px; }

  /* MD body */
  .prose { font-size:16px; line-height:1.8; }
  .prose h1 { font-size:32px; font-weight:900; letter-spacing:-.02em;
    margin:0 0 14px; text-align:center; }
  .prose h2 { font-family:'Noto Serif KR',serif; font-size:22px;
    font-weight:800; letter-spacing:-.015em; margin:36px 0 14px;
    padding-bottom:6px; border-bottom:2px solid var(--rule); }
  .prose h3 { font-size:17px; font-weight:700; margin:24px 0 8px; }
  .prose p { margin:0 0 14px; }
  .prose p:first-of-type::first-letter { font-size:54px; font-weight:800;
    float:left; line-height:.9; padding:4px 8px 0 0; color:var(--accent); }
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

  /* Archive list */
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
    letter-spacing:.12em; text-transform:uppercase; }

  @media (max-width:720px) {
    .mh-title { font-size:54px; }
    .brief { grid-template-columns:1fr; gap:18px; }
    .brief-stats, .byline { border-left:none; padding-left:0; }
    .prose ul, .arch ul { columns:1; }
  }
"""


def _layout(title, body, active, site_title, now):
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
        <span>VOL. III</span>
        <span>{title}</span>
        <span>AI · KST 08:00</span>
      </div>
      <h1 class="mh-title">The Daily <em>Brief</em></h1>
      <div class="mh-tag">RSS · AI 분석 · 매일 아침 한 부</div>
      <div class="mh-nav">
        <a href="index.html" class="{'on' if active=='index' else ''}">최신 리포트</a>
        <a href="archive.html" class="{'on' if active=='archive' else ''}">아카이브</a>
      </div>
    </div>

    {body}

    <div class="foot">
      <span>The Daily Brief</span>
      <span>chamgil71/dailynews</span>
      <span>생성 {now} KST</span>
    </div>
  </div>
</body>
</html>"""


def render_report(ctx):
    s = ctx['data']['stats']
    body = f"""
    <div class="brief">
      <div class="brief-stats">
        <span class="lbl">오늘의 통계</span>
        <div class="brief-stat"><span class="num">{s['total']}</span><span class="lab">건 수집</span></div>
        <div class="brief-stat"><span class="num">{s['sent_to_ai']}</span><span class="lab">AI 분석</span></div>
        <div class="brief-stat"><span class="num">{s['ko']}</span><span class="lab">국내</span></div>
      </div>
      <div>
        <div class="kicker">에디터 노트 · TODAY'S LEDE</div>
        <p class="lede">AI가 매일 아침 수십 개 언론사의 헤드라인을 한 면에 정리합니다.
        오늘 분석된 {s['sent_to_ai']}건의 기사 핵심을 아래에서 읽어보세요.</p>
      </div>
      <div class="byline">
        AI Editor<br>Gemini 2.0 Flash<br>─<br>{ctx['date_str']}
      </div>
    </div>

    <div class="prose">
      {ctx['md_html']}
    </div>"""
    return _layout(ctx['display_date'], body, 'index', ctx['site_title'], ctx['now'])


def render_archive(ctx):
    items = "".join(f"""
        <li>
          <a href="{it['date']}.html">{it['display']}</a>
          <div class="d">{it['date']}</div>
        </li>""" for it in ctx['items'])
    body = f"""
    <div class="arch">
      <h1>전체 리포트 색인</h1>
      <p class="count">LEDGER · 총 {len(ctx['items'])}호 발행</p>
      <ul>{items}</ul>
    </div>"""
    return _layout("아카이브", body, 'archive', ctx['site_title'], ctx['now'])
