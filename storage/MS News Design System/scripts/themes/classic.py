# scripts/themes/classic.py
# 기존 디자인을 그대로 모듈화 (남색 헤더 + 파란 배지 + 흰 카드).

def _layout(title, body, active, site_title, now):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI가 매일 자동으로 수집·분석하는 글로벌 뉴스 브리핑">
  <title>{title} — {site_title}</title>
  <style>
    :root {{ --blue:#2563eb; --navy:#1e3a5f; --bg:#f8fafc; --card:#fff;
             --border:#e2e8f0; --text:#1e293b; --muted:#64748b; }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:-apple-system,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }}
    header {{ background:var(--navy); color:#fff; padding:0 24px;
              display:flex; align-items:center; justify-content:space-between;
              height:58px; position:sticky; top:0; z-index:100; box-shadow:0 2px 8px rgba(0,0,0,.25); }}
    header .logo {{ font-size:1.15rem; font-weight:700; letter-spacing:-.3px; }}
    header .logo span {{ color:#60a5fa; }}
    header nav a {{ color:rgba(255,255,255,.8); text-decoration:none; margin-left:20px;
                    font-size:.9rem; transition:color .15s; }}
    header nav a:hover, header nav a.active {{ color:#fff; font-weight:600; }}
    .container {{ max-width:860px; margin:0 auto; padding:36px 20px 80px; }}
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px;
             padding:32px 36px; margin-bottom:24px; box-shadow:0 1px 4px rgba(0,0,0,.06); }}
    h1 {{ font-size:1.6rem; color:var(--navy); margin-bottom:6px; }}
    h2 {{ font-size:1.2rem; color:var(--blue); margin:2em 0 .6em;
          padding-bottom:6px; border-bottom:2px solid var(--border); }}
    h3 {{ font-size:1rem; color:var(--navy); margin:1.4em 0 .4em; }}
    p {{ margin-bottom:.9em; }}
    a {{ color:var(--blue); }}
    ul, ol {{ padding-left:1.4em; margin-bottom:.9em; }}
    li {{ margin-bottom:.3em; }}
    hr {{ border:none; border-top:1px solid var(--border); margin:2em 0; }}
    code {{ background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:.88em; }}
    blockquote {{ border-left:4px solid var(--blue); padding:8px 16px; background:#eff6ff;
                  border-radius:0 8px 8px 0; margin:1em 0; color:var(--muted); }}
    .meta {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:24px; }}
    .badge {{ background:#eff6ff; color:var(--blue); border:1px solid #bfdbfe;
              padding:3px 10px; border-radius:20px; font-size:.78rem; font-weight:500; }}
    .archive-list {{ list-style:none; padding:0; }}
    .archive-list li {{ border-bottom:1px solid var(--border); padding:14px 0; }}
    .archive-list li:last-child {{ border-bottom:none; }}
    .archive-list a {{ font-weight:500; font-size:1rem; text-decoration:none; }}
    .archive-list a:hover {{ text-decoration:underline; }}
    .archive-list .date {{ color:var(--muted); font-size:.85rem; margin-top:2px; }}
    footer {{ text-align:center; color:var(--muted); font-size:.8rem; padding:24px; border-top:1px solid var(--border); }}
    @media (max-width:600px) {{ .card {{ padding:20px; }} header .logo {{ font-size:1rem; }} }}
  </style>
</head>
<body>
  <header>
    <div class="logo">📰 AI <span>News</span> Daily</div>
    <nav>
      <a href="index.html" {"class='active'" if active=='index' else ''}>최신 리포트</a>
      <a href="archive.html" {"class='active'" if active=='archive' else ''}>전체 목록</a>
    </nav>
  </header>
  <div class="container">{body}</div>
  <footer>Powered by GitHub Actions · OpenAI GPT · RSS Feeds<br>
    매일 자동 업데이트 · 생성: {now} KST</footer>
</body>
</html>"""


def render_report(ctx):
    body = f"""
    <div class="card">
      <h1>📰 Daily News Brief</h1>
      <div class="meta">
        <span class="badge">📅 {ctx['display_date']}</span>
        <span class="badge">🤖 AI 자동 분석</span>
        <span class="badge">🌐 EN + KO</span>
      </div>
      {ctx['md_html']}
    </div>"""
    return _layout(ctx['display_date'], body, 'index', ctx['site_title'], ctx['now'])


def render_archive(ctx):
    items = "".join(f"""
        <li>
          <a href="{it['date']}.html">📄 {it['display']} 리포트</a>
          <div class="date">{it['date']}</div>
        </li>""" for it in ctx['items'])
    body = f"""
    <div class="card">
      <h1>📚 전체 리포트 목록</h1>
      <p style="color:var(--muted);margin:.5em 0 1.5em">총 {len(ctx['items'])}개 리포트</p>
      <ul class="archive-list">{items}</ul>
    </div>"""
    return _layout("전체 목록", body, 'archive', ctx['site_title'], ctx['now'])
