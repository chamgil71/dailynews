# scripts/build_site.py
"""
GitHub Pages 정적 사이트 빌더
reports/news_*.md → publish/*.html + publish/index.html + publish/archive.html
                  + publish/reports-data.json

사용법:
  python scripts/build_site.py                         # 기본 빌드
  python scripts/build_site.py --theme terminal        # 전체 테마 강제 지정
  python scripts/build_site.py --from 2026-05-01       # 해당 날짜 이후만 빌드
  python scripts/build_site.py --all                   # 모든 날짜 강제 재빌드
  python scripts/build_site.py --color-only            # 색상 토큰만 교체 (레이아웃 유지)

테마 설정: config/theme_config.py > SECTION_THEMES["news"]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import markdown2
from dotenv import load_dotenv

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

load_dotenv()

from config.settings import SITE_BASE_URL
from config.theme_config import SECTION_THEMES, SITE_TITLE, FOOTER_CONFIG, SUBSCRIBE_URL

REPORTS_DIR  = "reports"
DOCS_DIR     = "publish"
NEWS_HTML_DIR = os.path.join(DOCS_DIR, "news")   # 날짜별 HTML 전용 디렉토리
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(NEWS_HTML_DIR, exist_ok=True)


# ── MD 파싱: 통계+뉴스목록 추출 (app.html SPA용 JSON) ────────────────────────
def parse_md_for_json(md_path: str, date_str: str) -> dict:
    raw = Path(md_path).read_text(encoding="utf-8")

    # 통계 파싱
    stats_line = next(
        (ln.lstrip("> ").strip() for ln in raw.splitlines() if ln.startswith("> 📊")),
        ""
    )
    stats = {
        "total":      int(m.group(1)) if (m := re.search(r'총 (\d+)건', stats_line)) else 0,
        "en":         int(m.group(1)) if (m := re.search(r'EN:\s*(\d+)', stats_line)) else 0,
        "ko":         int(m.group(1)) if (m := re.search(r'KO:\s*(\d+)', stats_line)) else 0,
        "sent_to_ai": int(m.group(1)) if (m := re.search(r'AI 분석:\s*(\d+)건', stats_line)) else 0,
    }

    # 뉴스 항목 파싱
    news_en, news_ko = [], []
    for sec in raw.split("### "):
        is_en = sec.startswith("🌐 영어")
        is_ko = sec.startswith("🇰🇷 한국어")
        if not is_en and not is_ko:
            continue
        
        # 기사 제목/링크와 그 다음 줄의 요약문(선택적)을 정규식으로 안전하게 매칭
        # 윈도우(\r\n)와 리눅스(\n) 줄바꿈을 모두 포용하도록 \r?\n 사용
        pattern = r'^- \*\*\[(.+?)\]\*\* \[(.+?)\]\((.+?)\)(?:\r?\n\s*>\s*(.+))?'
        matches = re.finditer(pattern, sec, re.MULTILINE)
        for m in matches:
            item = {
                "label": m.group(1).strip(),
                "title": m.group(2).strip(),
                "link": m.group(3).strip(),
                "summary": m.group(4).strip() if m.group(4) else ""
            }
            (news_en if is_en else news_ko).append(item)

    # 분석 섹션 (combined: 뉴스 목록 제외, 섹션 헤더 포함)
    en_match = re.search(r'## 🌐 Global News Analysis\n([\s\S]*?)(?=---\n\n## 🇰🇷|## 📋|$)', raw)
    ko_match = re.search(r'## 🇰🇷 국내 뉴스 분석\n([\s\S]*?)(?=## 📋|$)', raw)
    en_full  = re.search(r'(## 🌐 Global News Analysis\n[\s\S]*?)(?=---\n\n## 🇰🇷|## 📋|$)', raw)
    ko_full  = re.search(r'(## 🇰🇷 국내 뉴스 분석\n[\s\S]*?)(?=## 📋|$)', raw)
    combined_parts = [m.group(1).strip() for m in (en_full, ko_full) if m]
    combined = "\n\n---\n\n".join(combined_parts)
    if not combined:
        combined = raw.split("## 📋")[0].strip() if "## 📋" in raw else raw.strip()

    # structured 사이드카 JSON 로드
    structured = {}
    json_sidecar = Path(md_path).with_suffix(".json")
    if json_sidecar.exists():
        try:
            structured = json.loads(json_sidecar.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "date":        date_str,
        "analysis_en": en_match.group(1).strip() if en_match else "",
        "analysis_ko": ko_match.group(1).strip() if ko_match else "",
        "combined":    combined,
        "news_en":     news_en,
        "news_ko":     news_ko,
        "stats":       stats,
        "structured":  structured,
    }


# ── ctx 빌더 (themes 계약) ─────────────────────────────────────────────────────
def build_report_ctx(md_path: str, date_str: str, data: dict) -> dict:
    raw = Path(md_path).read_text(encoding="utf-8")
    md_html = markdown2.markdown(
        raw,
        extras=["tables", "fenced-code-blocks", "strike", "cuddled-lists", "header-ids"],
    )
    # 이메일용 축약 (분석 섹션만)
    email_parts = re.findall(
        r'(?:## 🌐|## 🇰🇷)([\s\S]*?)(?=## 📋|$)', raw
    )
    email_md   = "\n\n".join(email_parts).strip() or raw
    email_html = markdown2.markdown(email_md, extras=["tables", "fenced-code-blocks"])

    # JSON sidecar 로드 (editorial/terminal 테마 rich UI용)
    structured: dict = {}
    json_sidecar = Path(md_path).with_suffix(".json")
    if json_sidecar.exists():
        try:
            structured = json.loads(json_sidecar.read_text(encoding="utf-8"))
        except Exception:
            pass

    try:
        display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    except ValueError:
        display_date = date_str

    return {
        "display_date":    display_date,
        "date_str":        date_str,
        "md_html":         md_html,
        "email_html":      email_html,
        "site_title":      SITE_TITLE,
        "now":             datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data":            data,
        "items":           [],
        "site_url":        SITE_BASE_URL or "https://chamgil71.github.io/dailynews/",
        "subscribe_url":   SUBSCRIBE_URL,
        "unsubscribe_url": "",
        "structured":      structured,
    }


# ── 아카이브 ctx 빌더 ──────────────────────────────────────────────────────────
def build_archive_ctx(pages: list[tuple[str, str]]) -> dict:
    items = []
    for date_str, _ in pages:
        try:
            display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일 (%a)")
        except ValueError:
            display = date_str
        items.append({"date": date_str, "display": display})
    return {
        "display_date": "전체 목록",
        "date_str":     "",
        "md_html":      "",
        "email_html":   "",
        "site_title":   SITE_TITLE,
        "now":          datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data":         {"stats": {}},
        "items":        items,
        "site_url":     SITE_BASE_URL or "",
        "subscribe_url": SUBSCRIBE_URL,
        "unsubscribe_url": "",
    }


# ── 메인 빌드 ─────────────────────────────────────────────────────────────────
def build(theme_name: str | None = None,
          from_date: str | None = None,
          rebuild_all: bool = False) -> None:
    from themes import load_theme
    active_theme = theme_name or SECTION_THEMES.get("news", "classic")
    theme = load_theme(active_theme)
    print(f"[news-build] theme={active_theme}"
          + (f"  from={from_date}" if from_date else "")
          + ("  ALL" if rebuild_all else ""))

    md_files = sorted(glob.glob(f"{REPORTS_DIR}/news_*.md"), reverse=True)
    if not md_files:
        print("  reports/ 에 MD 파일이 없습니다.")
        return

    # 날짜 필터링
    if from_date and not rebuild_all:
        md_files = [
            f for f in md_files
            if Path(f).name.replace("news_", "").replace(".md", "") >= from_date
        ]
        print(f"  {from_date} 이후 파일만 빌드: {len(md_files)}개")

    pages:       list[tuple[str, str]] = []
    reports_data: list[dict]           = []

    for md_path in md_files:
        date_str = Path(md_path).name.replace("news_", "").replace(".md", "")
        data = parse_md_for_json(md_path, date_str)
        ctx  = build_report_ctx(md_path, date_str, data)

        html     = theme.render_report(ctx)
        out_path = os.path.join(NEWS_HTML_DIR, f"{date_str}.html")
        Path(out_path).write_text(html, encoding="utf-8")
        pages.append((date_str, out_path))

        # 날짜별 뉴스 목록 JSON (app.html lazy-load용: news_en, news_ko 분리 저장)
        news_json_path = os.path.join(NEWS_HTML_DIR, f"{date_str}.json")
        news_payload   = {"date": date_str, "news_en": data["news_en"], "news_ko": data["news_ko"]}
        Path(news_json_path).write_text(
            json.dumps(news_payload, ensure_ascii=False), encoding="utf-8"
        )

        # reports-data.json 에는 news_en/news_ko 제외 (파일 크기 절감)
        reports_data.append({k: v for k, v in data.items() if k not in ("news_en", "news_ko")})
        print(f"  + news/{date_str}.html + {date_str}.json [{active_theme}]")

    # archive.html
    archive_ctx = build_archive_ctx(pages)
    archive_html = theme.render_archive(archive_ctx)
    Path(DOCS_DIR, "archive.html").write_text(archive_html, encoding="utf-8")
    print("  + archive.html")

    # reports-data.json (SPA용 — news_en/news_ko 제외, 경량 인덱스)
    # --from 빌드 시에는 기존 JSON 데이터와 병합
    json_path = Path(DOCS_DIR, "reports-data.json")
    if from_date and not rebuild_all and json_path.exists():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            existing_dates = {r["date"] for r in reports_data}
            # 기존 항목도 news_en/news_ko 제거 (레거시 대응)
            cleaned_existing = [
                {k: v for k, v in r.items() if k not in ("news_en", "news_ko")}
                for r in existing if r["date"] not in existing_dates
            ]
            merged = reports_data + cleaned_existing
            merged.sort(key=lambda r: r["date"], reverse=True)
            reports_data = merged
        except Exception:
            pass
    json_path.write_text(
        json.dumps(reports_data, ensure_ascii=False, indent=None),
        encoding="utf-8"
    )
    print(f"  + reports-data.json ({len(reports_data)}개 — news 목록 분리됨)")

    # reports.json (메타)
    meta = [{"date": d, "url": f"news/{d}.html"} for d, _ in
            sorted([(r["date"], "") for r in reports_data], key=lambda x: x[0], reverse=True)]
    Path(DOCS_DIR, "reports.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # index.html = app.html (동적 SPA)
    app_src = Path(DOCS_DIR, "app.html")
    app_dst = Path(DOCS_DIR, "index.html")
    if app_src.exists():
        app_html = app_src.read_text(encoding="utf-8")
        
        # ── 모든 테마 동적 컴파일 파이프라인 ──
        theme_fonts = []
        theme_css = []
        theme_chips = []
        
        themes_dir = Path(Path(__file__).parent.parent, "themes")
        import importlib
        
        # 일관된 순서 지정을 위한 정렬 기준
        theme_order = ["classic", "minimal", "ink", "forest", "editorial", "terminal"]
        found_themes = []
        
        for p in themes_dir.glob("*.py"):
            name = p.stem
            if name in ["base", "__init__"]:
                continue
            try:
                # 임포트 시 충돌 방지 및 정상 탑재
                mod = importlib.import_module(f"themes.{name}")
                if hasattr(mod, "TOKENS"):
                    found_themes.append((name, mod.TOKENS))
            except Exception as e:
                print(f"  ⚠ 테마 '{name}' 로드 에러: {e}")
                
        # 순서 정렬
        found_themes.sort(key=lambda x: theme_order.index(x[0]) if x[0] in theme_order else 999)
        
        for name, tokens in found_themes:
            meta = tokens.get("meta", {})
            colors = tokens.get("colors", {})
            font_family = meta.get("font_family", "")
            
            # 1. 폰트 CDN 취합
            font_cdn = meta.get("font_cdn", "")
            if font_cdn:
                font_tag = f'  <link href="{font_cdn}" rel="stylesheet">'
                if font_tag not in theme_fonts:
                    theme_fonts.append(font_tag)
                    
            # 2. CSS 변수 코드 빌드 (언더스코어를 대시로 변환)
            css_vars = []
            for k, v in colors.items():
                css_key = k.replace("_", "-")
                css_vars.append(f"      --{css_key}: {v};")
            if font_family:
                css_vars.append(f"      --font-family: {font_family};")
                
            css_block = f'    [data-theme="{name}"] {{\n' + "\n".join(css_vars) + "\n    }"
            theme_css.append(css_block)
            
            # 3. 테마 선택 칩 HTML 생성
            label = meta.get("label", name.capitalize())
            desc = meta.get("desc", "")
            swatch = meta.get("swatch_colors", ["#ccc", "#999"])
            grad_val = ",".join(swatch)
            if len(swatch) == 1:
                grad_val = f"{swatch[0]},{swatch[0]}"
                
            is_active = " active" if name == active_theme else ""
            chip_html = f"""    <div class="theme-chip{is_active}" onclick="applyTheme('{name}')" id="chip-{name}">
      <div class="chip-swatch" style="background:linear-gradient(90deg,{grad_val})"></div>
      <div class="chip-name">{label}</div>
      <div class="chip-desc">{desc}</div>
    </div>"""
            theme_chips.append(chip_html)
            
        # 플레이스홀더들 동적 교체
        if theme_fonts:
            pre_connect = """  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>"""
            app_html = app_html.replace('<!-- DYNAMIC_THEME_FONTS -->', f"{pre_connect}\n" + "\n".join(theme_fonts))
            
        app_html = app_html.replace('/* DYNAMIC_THEME_CSS */', "\n\n".join(theme_css))
        app_html = app_html.replace('<!-- DYNAMIC_THEME_CHIPS -->', "\n".join(theme_chips))
        
        # 디폴트 body data-theme 및 localstorage 치환
        app_html = app_html.replace('<body data-theme="classic">', f'<body data-theme="{active_theme}">')
        app_html = app_html.replace('localStorage.getItem("site-theme") || "classic"', f'localStorage.getItem("site-theme") || "{active_theme}"')
        
        app_dst.write_text(app_html, encoding="utf-8")
        print(f"  + index.html (← app.html, dynamic compiled {len(found_themes)} themes, default_theme: {active_theme})")
    else:
        print("  ⚠ app.html 없음: index.html 미생성")

    print(f"\nDone: {len(pages)}개 빌드 완료 → {DOCS_DIR}/  [theme: {active_theme}]")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AI News Daily 사이트 빌더")
    ap.add_argument("--theme", default=None,
                    help="테마 이름 (classic|minimal|ink|forest|editorial|terminal). "
                         "미지정 시 config/theme_config.py SECTION_THEMES[news] 사용")
    ap.add_argument("--from", dest="from_date", default=None, nargs="?",
                    const="TODAY", metavar="YYYY-MM-DD",
                    help="이 날짜 이후 파일만 빌드. "
                         "날짜 생략 시(--from 만 입력) 오늘 파일만 빌드")
    ap.add_argument("--all", action="store_true",
                    help="모든 날짜 강제 재빌드 (일괄 변경)")
    args = ap.parse_args()

    # --from 단독 → 오늘 날짜
    from_date = args.from_date
    if from_date == "TODAY":
        from_date = datetime.now().strftime("%Y-%m-%d")

    build(
        theme_name  = args.theme,
        from_date   = from_date,
        rebuild_all = args.all,
    )
