# scripts/build_site.py
"""
GitHub Pages 정적 사이트 빌더
reports/*.md → docs/*.html + docs/index.html + docs/archive.html + docs/reports-data.json

실행: python scripts/build_site.py
의존: markdown (pip install markdown)
"""

import glob
import json
import os
import re
from datetime import datetime

import markdown

REPORTS_DIR = "reports"
DOCS_DIR    = "docs"
SITE_TITLE  = "AI News Daily"
os.makedirs(DOCS_DIR, exist_ok=True)

# ── 공통 HTML 레이아웃 ────────────────────────────────────────────────────────
def layout(title: str, body: str, active: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI가 매일 자동으로 수집·분석하는 글로벌 뉴스 브리핑">
  <title>{title} — {SITE_TITLE}</title>
  <style>
    :root {{
      --blue:   #2563eb;
      --navy:   #1e3a5f;
      --bg:     #f8fafc;
      --card:   #ffffff;
      --border: #e2e8f0;
      --text:   #1e293b;
      --muted:  #64748b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, "Segoe UI", sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.7;
    }}

    /* ── 헤더 ── */
    header {{
      background: var(--navy);
      color: #fff;
      padding: 0 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 58px;
      position: sticky; top: 0; z-index: 100;
      box-shadow: 0 2px 8px rgba(0,0,0,.25);
    }}
    header .logo {{ font-size: 1.15rem; font-weight: 700; letter-spacing: -.3px; }}
    header .logo span {{ color: #60a5fa; }}
    header nav a {{
      color: rgba(255,255,255,.8);
      text-decoration: none;
      margin-left: 20px;
      font-size: .9rem;
      transition: color .15s;
    }}
    header nav a:hover,
    header nav a.active {{ color: #fff; font-weight: 600; }}

    /* ── 본문 ── */
    .container {{ max-width: 860px; margin: 0 auto; padding: 36px 20px 80px; }}

    /* ── 카드 ── */
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 32px 36px;
      margin-bottom: 24px;
      box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }}

    /* ── 타이포 ── */
    h1 {{ font-size: 1.6rem; color: var(--navy); margin-bottom: 6px; }}
    h2 {{
      font-size: 1.2rem; color: var(--blue);
      margin: 2em 0 .6em;
      padding-bottom: 6px;
      border-bottom: 2px solid var(--border);
    }}
    h3 {{ font-size: 1rem; color: var(--navy); margin: 1.4em 0 .4em; }}
    p  {{ margin-bottom: .9em; }}
    a  {{ color: var(--blue); }}
    ul, ol {{ padding-left: 1.4em; margin-bottom: .9em; }}
    li {{ margin-bottom: .3em; }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 2em 0; }}
    code {{
      background: #f1f5f9; padding: 2px 6px;
      border-radius: 4px; font-size: .88em;
    }}
    blockquote {{
      border-left: 4px solid var(--blue);
      padding: 8px 16px;
      background: #eff6ff;
      border-radius: 0 8px 8px 0;
      margin: 1em 0;
      color: var(--muted);
    }}

    /* ── 메타 배지 ── */
    .meta {{
      display: flex; flex-wrap: wrap; gap: 8px;
      margin-bottom: 24px;
    }}
    .badge {{
      background: #eff6ff; color: var(--blue);
      border: 1px solid #bfdbfe;
      padding: 3px 10px; border-radius: 20px;
      font-size: .78rem; font-weight: 500;
    }}

    /* ── 아카이브 목록 ── */
    .archive-list {{ list-style: none; padding: 0; }}
    .archive-list li {{
      border-bottom: 1px solid var(--border);
      padding: 14px 0;
    }}
    .archive-list li:last-child {{ border-bottom: none; }}
    .archive-list a {{
      font-weight: 500; font-size: 1rem; text-decoration: none;
    }}
    .archive-list a:hover {{ text-decoration: underline; }}
    .archive-list .date {{ color: var(--muted); font-size: .85rem; margin-top: 2px; }}

    /* ── 푸터 ── */
    footer {{
      text-align: center;
      color: var(--muted);
      font-size: .8rem;
      padding: 24px;
      border-top: 1px solid var(--border);
    }}

    @media (max-width: 600px) {{
      .card {{ padding: 20px; }}
      header .logo {{ font-size: 1rem; }}
    }}
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

  <div class="container">
    {body}
  </div>

  <footer>
    Powered by GitHub Actions · OpenAI GPT · RSS Feeds<br>
    매일 자동 업데이트 · 생성: {datetime.now().strftime("%Y-%m-%d %H:%M")} KST
  </footer>
</body>
</html>"""


# ── MD 파싱 (app.html 용 JSON 데이터 추출) ────────────────────────────────────
def parse_md_for_json(md_path: str, date_str: str) -> dict:
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    # 통계 파싱
    stats_line = ""
    for line in raw.splitlines():
        if line.startswith("> 📊"):
            stats_line = line.lstrip("> ").strip()
            break

    stats = {
        "total":      int(m.group(1)) if (m := re.search(r'총 (\d+)건', stats_line)) else 0,
        "en":         int(m.group(1)) if (m := re.search(r'EN:\s*(\d+)', stats_line)) else 0,
        "ko":         int(m.group(1)) if (m := re.search(r'KO:\s*(\d+)', stats_line)) else 0,
        "sent_to_ai": int(m.group(1)) if (m := re.search(r'AI 분석:\s*(\d+)건', stats_line)) else 0,
    }

    # 뉴스 항목 파싱
    news_en, news_ko = [], []
    sections = raw.split("### ")
    for sec in sections:
        is_en = sec.startswith("🌐 영어")
        is_ko = sec.startswith("🇰🇷 한국어")
        if not is_en and not is_ko:
            continue
        for line in sec.split("\n"):
            m = re.match(r'^- \*\*\[(.+?)\]\*\* \[(.+?)\]\((.+?)\)', line)
            if m:
                item = {"label": m.group(1), "title": m.group(2), "link": m.group(3)}
                if is_en:
                    news_en.append(item)
                else:
                    news_ko.append(item)

    # 분석 섹션 파싱
    en_match = re.search(r'## 🌐 Global News Analysis\n([\s\S]*?)(?=---\n\n## 🇰🇷|## 📋|$)', raw)
    ko_match = re.search(r'## 🇰🇷 국내 뉴스 분석\n([\s\S]*?)(?=## 📋|$)', raw)

    # combined: 분석 파트만 (뉴스 목록 제외)
    analysis_parts = re.findall(r'(?:## 🌐|## 🇰🇷)([\s\S]*?)(?=## 📋|$)', raw)
    combined = "\n\n---\n\n".join(analysis_parts).strip()
    if not combined:
        combined = raw.split("## 📋")[0].strip() if "## 📋" in raw else raw.strip()

    return {
        "date": date_str,
        "analysis_en": (en_match.group(1).strip() if en_match else ""),
        "analysis_ko": (ko_match.group(1).strip() if ko_match else ""),
        "combined": combined,
        "news_en": news_en,
        "news_ko": news_ko,
        "stats": stats,
    }


# ── 리포트 페이지 생성 ────────────────────────────────────────────────────────
def build_report_page(md_path: str, date_str: str) -> str:
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    html_body = markdown.markdown(
        raw,
        extras=["tables", "fenced-code-blocks", "strike", "cuddled-lists"]
    )

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = dt.strftime("%Y년 %m월 %d일")
    except Exception:
        display_date = date_str

    badges = f"""
    <div class="meta">
      <span class="badge">📅 {display_date}</span>
      <span class="badge">🤖 AI 자동 분석</span>
      <span class="badge">🌐 EN + KO</span>
    </div>"""

    body = f"""
    <div class="card">
      <h1>📰 Daily News Brief</h1>
      {badges}
      {html_body}
    </div>"""

    return layout(display_date, body, active="index")


# ── 아카이브 페이지 ───────────────────────────────────────────────────────────
def build_archive_page(pages: list) -> str:
    items = ""
    for date_str, _ in pages:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            display = dt.strftime("%Y년 %m월 %d일 (%a)")
        except Exception:
            display = date_str
        items += f"""
        <li>
          <a href="{date_str}.html">📄 {display} 리포트</a>
          <div class="date">{date_str}</div>
        </li>"""

    body = f"""
    <div class="card">
      <h1>📚 전체 리포트 목록</h1>
      <p style="color:var(--muted);margin:.5em 0 1.5em">총 {len(pages)}개 리포트</p>
      <ul class="archive-list">{items}</ul>
    </div>"""

    return layout("전체 목록", body, active="archive")


# ── 메인 빌드 ─────────────────────────────────────────────────────────────────
def build():
    md_files = sorted(
        glob.glob(f"{REPORTS_DIR}/news_*.md"), reverse=True
    )

    if not md_files:
        print("⚠  reports/ 에 MD 파일이 없습니다.")
        return

    pages = []
    reports_data = []  # app.html용 JSON 데이터

    for md_path in md_files:
        date_str = (
            os.path.basename(md_path)
            .replace("news_", "")
            .replace(".md", "")
        )
        html     = build_report_page(md_path, date_str)
        out_path = os.path.join(DOCS_DIR, f"{date_str}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        pages.append((date_str, out_path))

        # JSON 데이터 추출
        report_data = parse_md_for_json(md_path, date_str)
        reports_data.append(report_data)

        print(f"  ✓ {date_str}.html")

    # index.html = 최신 리포트
    latest_html = build_report_page(md_files[0], pages[0][0])
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(latest_html)

    # archive.html
    archive_html = build_archive_page(pages)
    with open(os.path.join(DOCS_DIR, "archive.html"), "w", encoding="utf-8") as f:
        f.write(archive_html)

    # 메타 JSON (Vercel 동적 연동용)
    meta = [{"date": d, "url": f"{d}.html"} for d, _ in pages]
    with open(os.path.join(DOCS_DIR, "reports.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # ★ app.html용 전체 리포트 데이터 JSON
    with open(os.path.join(DOCS_DIR, "reports-data.json"), "w", encoding="utf-8") as f:
        json.dump(reports_data, f, ensure_ascii=False)
    print(f"  ✓ reports-data.json ({len(reports_data)}개 리포트)")

    print(f"\n✅ {len(pages)}개 리포트 빌드 완료 → {DOCS_DIR}/")
    print(f"   최신: {pages[0][0]}")


if __name__ == "__main__":
    build()
