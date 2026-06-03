"""
기존 MD 파일을 재분석하는 스크립트.
메일/텔레그램 발송 없이 AI 분석 → JSON 사이드카 저장 → HTML 재빌드만 수행.

사용법:
  python scripts/reanalyze.py                    # 오늘 날짜
  python scripts/reanalyze.py --date 2026-05-25  # 특정 날짜
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("reanalyze")


def main(date_str: str) -> None:
    md_path = Path(f"reports/news_{date_str}.md")
    if not md_path.exists():
        logger.error(f"MD 파일 없음: {md_path}")
        sys.exit(1)

    logger.info(f"재분석 대상: {md_path}")

    # 1. MD에서 뉴스 목록 파싱
    from scripts.build_site import parse_md_for_json
    data = parse_md_for_json(str(md_path), date_str)
    news_en = data.get("news_en", [])
    news_ko = data.get("news_ko", [])
    logger.info(f"  뉴스 파싱: EN {len(news_en)}건, KO {len(news_ko)}건")

    if not news_en and not news_ko:
        logger.error("파싱된 뉴스가 없습니다. MD 형식을 확인하세요.")
        sys.exit(1)

    # label → category 역매핑 (parse_md_for_json 은 label만 반환하므로 보완)
    try:
        from config.rss_sources import RSS_FEEDS
        label_to_cat = {meta["label"]: cat for cat, meta in RSS_FEEDS.items()}
    except Exception:
        label_to_cat = {}
    for item in news_en:
        if "category" not in item:
            item["category"] = label_to_cat.get(item.get("label", ""), "technology")
    for item in news_ko:
        if "category" not in item:
            item["category"] = label_to_cat.get(item.get("label", ""), "korean_news")
    logger.info(f"  카테고리 보완 완료 (label_to_cat 매핑 {len(label_to_cat)}개)")

    # 2. AI 분석 실행
    from core.news.analyzer import get_analyzer
    logger.info("  AI 분석 중...")
    analyzer = get_analyzer()
    analysis = analyzer.analyze_by_lang(news_en, news_ko)
    structured = analysis.get("structured", {})
    logger.info(f"  분석 완료: EN issues {len(structured.get('en',{}).get('issues',[]))}개, "
                f"KO issues {len(structured.get('ko',{}).get('issues',[]))}개")

    # 3. JSON 사이드카 저장
    json_path = md_path.with_suffix(".json")
    if structured:
        json_path.write_text(json.dumps(structured, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  JSON 사이드카 저장: {json_path}")
    else:
        logger.warning("  structured 데이터 없음 → JSON 사이드카 미저장")

    # 4. MD 분석 섹션 업데이트
    original_md = md_path.read_text(encoding="utf-8")
    combined = analysis.get("combined", "")
    if combined and combined != "분석 결과 없음":
        # 기존 분석 섹션 교체 (## 📋 이전까지)
        if "## 📋" in original_md:
            before = original_md.split("## 📋")[0].rstrip()
            after  = "## 📋" + original_md.split("## 📋")[1]
            # 헤더+통계만 남기고 분석 삽입
            header_lines = []
            for line in before.splitlines():
                header_lines.append(line)
                if line.startswith("> 📊"):
                    break
            new_md = "\n".join(header_lines) + "\n\n" + combined + "\n\n" + after
        else:
            # 분석 섹션 없으면 끝에 추가
            new_md = original_md.rstrip() + "\n\n" + combined + "\n"
        md_path.write_text(new_md, encoding="utf-8")
        logger.info(f"  MD 분석 섹션 업데이트 완료")

    # 5. HTML 재빌드 (오늘 날짜만)
    logger.info(f"  HTML 재빌드 중...")
    from scripts.build_site import build
    build(from_date=date_str)
    logger.info(f"  완료: publish/{date_str}.html 재생성")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="기존 MD 파일 재분석 (메일 발송 없음)")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                    help="재분석 날짜 (기본: 오늘, 형식: YYYY-MM-DD)")
    args = ap.parse_args()
    main(args.date)
