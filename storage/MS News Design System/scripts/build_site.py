# scripts/build_site.py
"""
GitHub Pages 정적 사이트 빌더 (테마 시스템)
reports/*.md → publish/*.html + index.html + archive.html + reports-data.json

테마 선택:
    SITE_THEME=classic    (기본, 기존 디자인)
    SITE_THEME=minimal    (B시안, Substack 스타일)
    SITE_THEME=editorial  (A시안, 신문 스타일)
    SITE_THEME=terminal   (C시안, Bloomberg 터미널 스타일)

실행:
    python scripts/build_site.py
    SITE_THEME=minimal python scripts/build_site.py

의존: markdown2 (pip install markdown2)
"""

import glob
import importlib
import json
import os
import re
from datetime import datetime

import markdown2

# ── 설정 ─────────────────────────────────────────────────────────────────────
REPORTS_DIR = "reports"
DOCS_DIR    = "publish"
SITE_TITLE  = "AI News Daily"
THEME_NAME  = os.getenv("SITE_THEME", "classic").lower()

os.makedirs(DOCS_DIR, exist_ok=True)


# ── 테마 로더 ────────────────────────────────────────────────────────────────
def load_theme(name: str):
    """themes/<name>.py 를 동적 로드. 없으면 classic으로 폴백."""
    try:
        return importlib.import_module(f"scripts.themes.{name}")
    except ModuleNotFoundError:
        try:
            # scripts/ 안에서 직접 실행하는 경우
            return importlib.import_module(f"themes.{name}")
        except ModuleNotFoundError:
            print(f"⚠  테마 '{name}' 을 찾을 수 없습니다. classic으로 폴백합니다.")
            return importlib.import_module(f"scripts.themes.classic")


THEME = load_theme(THEME_NAME)


# ── MD 파싱 (app.html 용 JSON 데이터 추출) ────────────────────────────────────
def parse_md_for_json(md_path: str, date_str: str) -> dict:
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

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
                (news_en if is_en else news_ko).append(item)

    en_match = re.search(r'## 🌐 Global News Analysis\n([\s\S]*?)(?=---\n\n## 🇰🇷|## 📋|$)', raw)
    ko_match = re.search(r'## 🇰🇷 국내 뉴스 분석\n([\s\S]*?)(?=## 📋|$)', raw)

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


# ── 페이지 빌드 (테마에 위임) ─────────────────────────────────────────────────
def build_report_page(md_path: str, date_str: str) -> str:
    with open(md_path, encoding="utf-8") as f:
        raw = f.read()

    md_html = markdown2.markdown(
        raw, extras=["tables", "fenced-code-blocks", "strike", "cuddled-lists"]
    )

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = dt.strftime("%Y년 %m월 %d일")
    except Exception:
        display_date = date_str

    data = parse_md_for_json(md_path, date_str)

    ctx = {
        "site_title":   SITE_TITLE,
        "date_str":     date_str,
        "display_date": display_date,
        "md_html":      md_html,
        "data":         data,
        "now":          datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return THEME.render_report(ctx)


def build_archive_page(pages: list) -> str:
    items = []
    for date_str, _ in pages:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            display = dt.strftime("%Y년 %m월 %d일 (%a)")
        except Exception:
            display = date_str
        items.append({"date": date_str, "display": display})

    ctx = {
        "site_title": SITE_TITLE,
        "items":      items,
        "now":        datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    return THEME.render_archive(ctx)


# ── 메인 빌드 ─────────────────────────────────────────────────────────────────
def build():
    md_files = sorted(
        glob.glob(f"{REPORTS_DIR}/news_*.md"), reverse=True
    )
    if not md_files:
        print("⚠  reports/ 에 MD 파일이 없습니다.")
        return

    print(f"🎨 THEME = {THEME_NAME}")

    pages = []
    reports_data = []

    for md_path in md_files:
        date_str = (
            os.path.basename(md_path)
            .replace("news_", "")
            .replace(".md", "")
        )
        html = build_report_page(md_path, date_str)
        out_path = os.path.join(DOCS_DIR, f"{date_str}.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        pages.append((date_str, out_path))

        report_data = parse_md_for_json(md_path, date_str)
        reports_data.append(report_data)

        print(f"  ✓ {date_str}.html")

    # index = 최신
    latest_html = build_report_page(md_files[0], pages[0][0])
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(latest_html)

    # archive
    archive_html = build_archive_page(pages)
    with open(os.path.join(DOCS_DIR, "archive.html"), "w", encoding="utf-8") as f:
        f.write(archive_html)

    # 메타 JSON (Vercel app.html 연동용)
    meta = [{"date": d, "url": f"{d}.html"} for d, _ in pages]
    with open(os.path.join(DOCS_DIR, "reports.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    with open(os.path.join(DOCS_DIR, "reports-data.json"), "w", encoding="utf-8") as f:
        json.dump(reports_data, f, ensure_ascii=False)
    print(f"  ✓ reports-data.json ({len(reports_data)}개 리포트)")

    print(f"\n✅ {len(pages)}개 리포트 빌드 완료 → {DOCS_DIR}/  ({THEME_NAME})")
    print(f"   최신: {pages[0][0]}")


if __name__ == "__main__":
    build()
