# scripts/themes/minimal.py
# B시안 — Substack/Bear 풍 미니멀. Pretendard, 넓은 여백, 단일 컬럼.
# 평탄한 MD 입력과 가장 잘 맞는 테마.

_FONTS = """
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" as="style" crossorigin
        href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
"""

_CSS = """
  :root {
    --bg:#fafaf7; --surface:#fff; --ink:#16181a; --ink-soft:#3d4248;
    --ink-mute:#8a8f95; --rule:#e6e2da; --accent:#ff5a1f; --chip:#f1efe8;
  }
  *,*::before,*::after { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink); line-height:1.6;
    font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
    font-feature-settings:'ss01','ss02'; }

  .topbar { max-width:720px; margin:0 auto; padding:28px 24px 24px;
    display:flex; justify-content:space-between; align-items:center;
    border-bottom:1px solid var(--rule); }
  .brand { display:flex; align-items:center; gap:10px; font-weight:700;
    letter-spacing:-.02em; font-size:15px; }
  .brand-dot { width:22px; height:22px; border-radius:7px; background:var(--ink);
    display:grid; place-items:center; color:var(--bg); font-size:11px; font-weight:800; }
  .nav { display:flex; gap:22px; }
  .nav a { color:var(--ink-soft); text-decoration:none; font-size:13px; font-weight:500; }
  .nav a.on { color:var(--ink); font-weight:700; }

  .wrap { max-width:720px; margin:0 auto; padding:56px 24px 80px; }

  .eyebrow { font-size:12px; letter-spacing:.18em; text-transform:uppercase;
    color:var(--accent); font-weight:700; margin-bottom:18px;
    display:flex; align-items:center; gap:10px; }
  .eyebrow::before { content:''; width:24px; height:1px; background:var(--accent); }

  .hero h1 { font-size:46px; line-height:1.1; letter-spacing:-.03em;
    font-weight:800; margin:0 0 22px; text-wrap:balance; }
  .hero-meta { display:flex; gap:14px; align-items:center; color:var(--ink-mute);
    font-size:13px; padding-top:18px; border-top:1px solid var(--rule); margin-bottom:48px; }
  .hero-meta strong { color:var(--ink); font-weight:600; }
  .hero-meta .dot { width:3px; height:3px; background:var(--ink-mute); border-radius:50%; }

  .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:0;
    margin-bottom:48px; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule);
    padding:22px 0; }
  .stat { padding:0 4px; border-left:1px solid var(--rule); padding-left:18px; }
  .stat:first-child { border-left:none; padding-left:0; }
  .stat .n { font-size:30px; font-weight:800; letter-spacing:-.04em;
    line-height:1; margin-bottom:6px; font-feature-settings:'tnum'; }
  .stat .l { font-size:12px; color:var(--ink-mute); letter-spacing:.04em; }

  /* MD 본문 */
  .prose { font-size:16px; line-height:1.75; color:var(--ink-soft); }
  .prose h1 { font-size:32px; letter-spacing:-.025em; color:var(--ink);
    font-weight:800; margin:0 0 18px; line-height:1.15; }
  .prose h2 { font-size:24px; letter-spacing:-.02em; color:var(--ink);
    font-weight:800; margin:48px 0 16px; padding-bottom:10px;
    border-bottom:1px solid var(--rule); }
  .prose h3 { font-size:17px; letter-spacing:-.01em; color:var(--ink);
    font-weight:700; margin:32px 0 10px; }
  .prose p { margin:0 0 14px; }
  .prose a { color:var(--ink); text-decoration:underline; text-decoration-color:var(--rule);
    text-underline-offset:3px; transition:text-decoration-color .15s; }
  .prose a:hover { text-decoration-color:var(--accent); }
  .prose strong { color:var(--ink); font-weight:700; }
  .prose ul, .prose ol { padding-left:0; list-style:none; margin:0 0 18px; }
  .prose ul li, .prose ol li { position:relative; padding-left:22px; margin-bottom:10px; }
  .prose ul li::before { content:''; position:absolute; left:0; top:11px;
    width:6px; height:6px; border-radius:50%; background:var(--accent); }
  .prose ol { counter-reset:o; }
  .prose ol li { counter-increment:o; }
  .prose ol li::before { content:counter(o,decimal-leading-zero); position:absolute;
    left:0; top:1px; font-size:12px; color:var(--ink-mute); font-weight:700;
    font-feature-settings:'tnum'; }
  .prose blockquote { border:none; background:var(--chip); border-radius:10px;
    padding:14px 20px; color:var(--ink-soft); margin:18px 0;
    font-size:14px; }
  .prose blockquote p { margin:0; }
  .prose hr { border:none; border-top:1px solid var(--rule); margin:40px 0; }
  .prose code { background:var(--chip); padding:2px 6px; border-radius:4px;
    font-size:.88em; font-family:'JetBrains Mono',ui-monospace,monospace; }

  .sub { background:var(--surface); border:1px solid var(--rule); border-radius:14px;
    padding:32px; text-align:center; margin:56px 0 32px; }
  .sub h3 { font-size:20px; letter-spacing:-.02em; font-weight:800; margin:0 0 6px; color:var(--ink); }
  .sub p { font-size:14px; color:var(--ink-mute); margin:0 0 18px; }
  .sub form { display:flex; gap:8px; max-width:400px; margin:0 auto; }
  .sub input { flex:1; padding:11px 14px; border:1px solid var(--rule);
    border-radius:8px; font-size:14px; background:var(--bg); font-family:inherit;
    color:var(--ink); outline:none; }
  .sub button { background:var(--ink); color:var(--bg); border:none;
    padding:11px 18px; border-radius:8px; font-size:14px; font-weight:600;
    cursor:pointer; font-family:inherit; }

  .archive-list { list-style:none; padding:0; margin:0; }
  .archive-list li { display:grid; grid-template-columns:1fr auto auto;
    gap:18px; align-items:center; padding:16px 0; border-bottom:1px solid var(--rule); }
  .archive-list a { color:var(--ink); text-decoration:none; font-weight:600;
    font-size:15px; letter-spacing:-.01em; }
  .archive-list a:hover { color:var(--accent); }
  .archive-list .date { color:var(--ink-mute); font-size:12px;
    font-feature-settings:'tnum'; letter-spacing:.04em; }
  .archive-list .arrow { color:var(--ink-mute); font-size:16px; }

  .foot { max-width:720px; margin:0 auto; padding:22px 24px 40px;
    border-top:1px solid var(--rule); color:var(--ink-mute); font-size:12px;
    display:flex; justify-content:space-between; }

  @media (max-width:640px) {
    .hero h1 { font-size:34px; }
    .stats { grid-template-columns:repeat(2,1fr); gap:18px 0; }
    .stat:nth-child(3) { border-left:none; padding-left:0; }
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
  <div class="topbar">
    <div class="brand">
      <div class="brand-dot">N</div>
      <span>{site_title}</span>
    </div>
    <div class="nav">
      <a href="index.html" class="{'on' if active=='index' else ''}">오늘</a>
      <a href="archive.html" class="{'on' if active=='archive' else ''}">아카이브</a>
    </div>
  </div>

  <div class="wrap">{body}</div>

  <div class="foot">
    <span>© Daily News · {site_title}</span>
    <span>chamgil71/dailynews · 생성 {now} KST</span>
  </div>
</body>
</html>"""


def render_report(ctx):
    s = ctx['data']['stats']
    body = f"""
    <div class="hero">
      <div class="eyebrow">{ctx['display_date']} · 오늘의 브리핑</div>
      <h1>매일 아침 AI가 정리한 한국 뉴스 브리핑.</h1>
      <div class="hero-meta">
        <span><strong>AI 분석</strong></span>
        <span class="dot"></span><span>{s['sent_to_ai']}건 요약</span>
        <span class="dot"></span><span>총 {s['total']}건 수집</span>
        <span class="dot"></span><span>읽는 시간 약 6분</span>
      </div>
    </div>

    <div class="stats">
      <div class="stat"><div class="n">{s['total']}</div><div class="l">수집 기사</div></div>
      <div class="stat"><div class="n">{s['sent_to_ai']}</div><div class="l">AI 분석</div></div>
      <div class="stat"><div class="n">{s['ko']}</div><div class="l">한국어</div></div>
      <div class="stat"><div class="n">{s['en']}</div><div class="l">영어</div></div>
    </div>

    <div class="prose">
      {ctx['md_html']}
    </div>

    <div class="sub">
      <h3>매일 아침 8시, 받은편지함으로.</h3>
      <p>AI가 정리한 뉴스 브리핑. 광고 없음. 언제든 해지.</p>
      <form onsubmit="event.preventDefault(); window.open('https://forms.gle/REPLACE_WITH_GOOGLE_FORM_ID', '_blank');">
        <input placeholder="you@example.com" />
        <button type="submit">구독</button>
      </form>
    </div>"""
    return _layout(ctx['display_date'], body, 'index', ctx['site_title'], ctx['now'])


def render_archive(ctx):
    items = "".join(f"""
        <li>
          <a href="{it['date']}.html">{it['display']}</a>
          <span class="date">{it['date']}</span>
          <span class="arrow">→</span>
        </li>""" for it in ctx['items'])
    body = f"""
    <div class="hero">
      <div class="eyebrow">아카이브 · {len(ctx['items'])}개 리포트</div>
      <h1>지나간 매일의 브리핑.</h1>
    </div>
    <ul class="archive-list">{items}</ul>"""
    return _layout("아카이브", body, 'archive', ctx['site_title'], ctx['now'])
