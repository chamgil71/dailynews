# scripts/build_ai_issue_site.py
"""
주간 AI 이슈 HTML 빌더 스크립트.
reports/ai-issue/ai_issue_*.md -> publish/ai-issue/*.html 및 publish/ai-issue/ai-issue-data.json 인덱스를 생성합니다.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import markdown2
from dotenv import load_dotenv

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

load_dotenv()

from config.settings import SITE_BASE_URL
from config.theme_config import SECTION_THEMES, SITE_TITLE, FOOTER_CONFIG, SUBSCRIBE_URL

REPORTS_DIR = "reports/ai-issue"
PUBLISH_DIR = "publish/ai-issue"

os.makedirs(PUBLISH_DIR, exist_ok=True)


def parse_weekly_json_for_summary(json_path: Path) -> dict:
    """주간 JSON 사이드카를 파싱하여 app.html용 컴팩트한 요약 메타 데이터를 추출합니다."""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        top10 = data.get("top10", [])
        category_stats = data.get("category_stats", {})

        # TOP 3 이슈 제목 추출
        top3_titles = [item.get("title", "") for item in top10[:3]]

        ko_keys = {"korean_news", "korean_economy", "korean_tech"}
        ko_count = sum(category_stats.get(k, 0) for k in ko_keys)
        total = sum(category_stats.values()) or len(top10)

        return {
            "date": data.get("issue_date", json_path.stem.replace("ai_issue_", "")),
            "period": data.get("period", ""),
            "top3": top3_titles,
            "category_counts": category_stats,
            "stats": {
                "total": total,
                "en": total - ko_count,
                "ko": ko_count,
                "sent_to_ai": len(top10),
            },
        }
    except Exception as e:
        print(f"  ⚠ JSON 파싱 오류 {json_path.name}: {e}")
        return {
            "date": json_path.stem.replace("ai_issue_", ""),
            "period": "주간 데이터 분석 중",
            "top3": [],
            "category_counts": {},
            "stats": {"total": 0, "en": 0, "ko": 0, "sent_to_ai": 0},
        }


def build_weekly_report_ctx(md_path: Path, date_str: str, summary_data: dict) -> dict:
    """Jinja2 테마 렌더링에 적합한 컨텍스트 객체를 채취 조립합니다."""
    raw_md = md_path.read_text(encoding="utf-8")
    
    # Markdown 파싱 및 cuddled-lists 포함 extras
    md_html = markdown2.markdown(
        raw_md,
        extras=["tables", "fenced-code-blocks", "strike", "cuddled-lists", "header-ids"],
    )
    
    try:
        display_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y년 %m월 %d일")
    except ValueError:
        display_date = date_str
        
    # JSON 사이드카 데이터 직접 매핑
    structured = {}
    json_sidecar = md_path.with_suffix(".json")
    if json_sidecar.exists():
        try:
            structured = json.loads(json_sidecar.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    return {
        "display_date": f"AI Weekly — {display_date}",
        "date_str": date_str,
        "md_html": md_html,
        "email_html": "",
        "site_title": SITE_TITLE,
        "now": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M"),
        "data": summary_data,
        "items": [],
        "site_url": SITE_BASE_URL or "https://chamgil71.github.io/dailynews/",
        "subscribe_url": SUBSCRIBE_URL,
        "unsubscribe_url": "",
        "structured": structured,
    }


def main():
    print("[ai-issue-build] AI 주간 이슈 HTML 컴파일 시작")
    
    md_files = sorted(glob.glob(f"{REPORTS_DIR}/ai_issue_*.md"), reverse=True)
    if not md_files:
        print("  ⚠ reports/ai-issue/ 디렉토리에 MD 파일이 존재하지 않습니다. 빌드를 조기 중단합니다.")
        return
        
    # 테마 동적 바인딩 (AI이슈는 기획서 기조에 맞추어 품격 있는 'editorial' 테마를 기본으로 사용)
    from themes import load_theme
    active_theme = SECTION_THEMES.get("ai-issue", "editorial")
    theme = load_theme(active_theme)
    print(f"  → 적용 디자인 테마: {active_theme}")
    
    pages = []
    weekly_indexes = []
    
    for md_file_path in md_files:
        p = Path(md_file_path)
        date_str = p.stem.replace("ai_issue_", "")
        
        # 1. JSON 요약 정보 획득
        json_path = p.with_suffix(".json")
        summary = parse_weekly_json_for_summary(json_path) if json_path.exists() else {
            "date": date_str, "period": "주간 데이터 분석", "top3": [], "category_counts": {},
            "stats": {"total": 0, "en": 0, "ko": 0, "sent_to_ai": 0},
        }
        weekly_indexes.append(summary)
        
        # 2. 개별 날짜별 HTML 빌드
        ctx = build_weekly_report_ctx(p, date_str, summary)
        html_content = theme.render_report(ctx)
        
        out_html_path = os.path.join(PUBLISH_DIR, f"{date_str}.html")
        Path(out_html_path).write_text(html_content, encoding="utf-8")
        
        # 개별 JSON 도 아카이브 publish 폴더로 복사 이동 (SPA lazy-load 목적)
        out_json_path = os.path.join(PUBLISH_DIR, f"{date_str}.json")
        if json_path.exists():
            import shutil
            shutil.copy2(str(json_path), out_json_path)
            
        pages.append((date_str, out_html_path))
        print(f"  + publish/ai-issue/{date_str}.html & {date_str}.json 빌드 완료")
        
    # 3. 요약 인덱스 파일 publish/ai-issue/ai-issue-data.json 저장 (git 추적 대상)
    index_payload = {
        "updated": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        "issues": weekly_indexes
    }
    
    index_json_path = os.path.join(PUBLISH_DIR, "data.json")
    Path(index_json_path).write_text(
        json.dumps(index_payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"  + publish/ai-issue/data.json 업데이트 완료 ({len(weekly_indexes)}개 아카이브 인덱스)")
    
    # 4. 아카이브 웹 목록 (publish/ai-issue/archive.html) 빌드
    # 테마 규격의 아카이브 렌더링에 적합한 컨텍스트 데이터 매핑
    archive_items = []
    for idx_item in weekly_indexes:
        archive_items.append({
            "date": idx_item["date"],
            "display": f"{idx_item['date']} 브리핑 ({idx_item['period']})"
        })
        
    archive_ctx = {
        "display_date": "AI 주간 이슈 아카이브",
        "date_str": "",
        "md_html": "",
        "email_html": "",
        "site_title": SITE_TITLE,
        "now": datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M"),
        "data": {"stats": {}},
        "items": archive_items,
        "site_url": SITE_BASE_URL or "",
        "subscribe_url": SUBSCRIBE_URL,
        "unsubscribe_url": "",
    }
    archive_html = theme.render_archive(archive_ctx)
    Path(PUBLISH_DIR, "archive.html").write_text(archive_html, encoding="utf-8")
    print("  + publish/ai-issue/archive.html 빌드 완료")
    
    # 5. 최신 아카이브 리다이렉트 index.html 빌드
    if pages:
        latest_date = pages[0][0]
        redirect_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Redirecting...</title>
  <meta http-equiv="refresh" content="0; url={latest_date}.html">
</head>
<body>
  <p>최신 주간 보고서로 이동 중입니다... <a href="{latest_date}.html">여기</a>를 클릭하세요.</p>
</body>
</html>"""
        Path(PUBLISH_DIR, "index.html").write_text(redirect_html, encoding="utf-8")
        print(f"  + publish/ai-issue/index.html 리다이렉터 빌드 완료 (최신: {latest_date})")
        
    print("AI 주간 이슈 HTML 컴파일 전과정 성공 완료\n")


if __name__ == "__main__":
    main()
