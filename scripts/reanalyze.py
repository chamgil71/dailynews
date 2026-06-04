"""
기존 MD 파일을 재분석하는 스크립트.
메일/텔레그램 발송 없이 AI 분석 → JSON 사이드카 저장 → HTML 재빌드만 수행.

모드:
  smart (기본): 분석 실패 마커가 있는 언어만 재분석, 성공한 쪽은 그대로 유지
  full        : 전체 초기화 후 EN + KO 모두 재분석

사용법:
  python scripts/reanalyze.py                           # 오늘 날짜, smart 모드
  python scripts/reanalyze.py --date 2026-06-01         # 특정 날짜, smart 모드
  python scripts/reanalyze.py --date 2026-06-01 --mode full  # 전체 재분석
"""
from __future__ import annotations

import argparse
import json
import logging
import re
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

EN_HEADER = "## 🌐 Global News Analysis"
KO_HEADER = "## 🇰🇷 국내 뉴스 분석"
EN_FAIL_MARKER = "⚠ AI analysis failed"
KO_FAIL_MARKER = "⚠ AI 분석 실패"


def _extract_section(md: str, header: str) -> str:
    """헤더 다음 내용을 --- 또는 ## 📋 전까지 추출."""
    m = re.search(re.escape(header) + r"\n([\s\S]*?)(?=\n---|\n## 📋|$)", md)
    return m.group(1).strip() if m else ""


def _replace_section(md: str, header: str, new_content: str) -> str:
    """헤더 다음 내용을 new_content로 교체. --- 또는 ## 📋 앞까지만."""
    if not new_content or not new_content.strip():
        logger.warning(f"  섹션 교체 건너뜀 (새 내용 없음): {header[:30]}")
        return md
    pattern = re.compile(
        re.escape(header) + r"\n[\s\S]*?(?=\n---|\n## 📋|\Z)",
    )
    replacement = header + "\n\n" + new_content.strip() + "\n"
    result = pattern.sub(replacement, md, count=1)
    if result == md:
        logger.warning(f"  섹션 교체 실패 (헤더 없음?): {header[:30]}")
    return result


def _add_category(items: list, label_to_cat: dict, default: str) -> None:
    """category 필드가 없는 아이템에 label 역매핑으로 보완."""
    for item in items:
        if "category" not in item:
            item["category"] = label_to_cat.get(item.get("label", ""), default)


def main(date_str: str, mode: str = "smart") -> None:
    md_path = Path(f"reports/news_{date_str}.md")
    if not md_path.exists():
        logger.error(f"MD 파일 없음: {md_path}")
        sys.exit(1)

    logger.info(f"재분석 대상: {md_path}  (mode={mode})")
    original_md = md_path.read_text(encoding="utf-8")

    # ── 1. MD에서 뉴스 목록 파싱 ────────────────────────────────────────────
    from scripts.build_site import parse_md_for_json
    data = parse_md_for_json(str(md_path), date_str)
    news_en = data.get("news_en", [])
    news_ko = data.get("news_ko", [])
    logger.info(f"  뉴스 파싱: EN {len(news_en)}건, KO {len(news_ko)}건")

    if not news_en and not news_ko:
        logger.error("파싱된 뉴스가 없습니다. MD 형식을 확인하세요.")
        sys.exit(1)

    # label → category 역매핑 보완
    try:
        from config.rss_sources import RSS_FEEDS
        label_to_cat = {meta["label"]: cat for cat, meta in RSS_FEEDS.items()}
    except Exception:
        label_to_cat = {}
    _add_category(news_en, label_to_cat, "technology")
    _add_category(news_ko, label_to_cat, "korean_news")
    logger.info(f"  카테고리 보완: label_to_cat {len(label_to_cat)}개")

    # ── 2. 재분석 대상 언어 결정 ─────────────────────────────────────────────
    if mode == "full":
        do_en = bool(news_en)
        do_ko = bool(news_ko)
        logger.info("  [full] EN·KO 전체 재분석")
    else:  # smart
        en_section = _extract_section(original_md, EN_HEADER)
        ko_section = _extract_section(original_md, KO_HEADER)
        do_en = EN_FAIL_MARKER in en_section and bool(news_en)
        do_ko = KO_FAIL_MARKER in ko_section and bool(news_ko)
        if not do_en and not do_ko:
            logger.info("  [smart] 모든 분석이 이미 완료됨 — 재분석 불필요")
            logger.info("  전체 재분석이 필요하면 --mode full 로 실행하세요.")
            return
        parts = [x for x, ok in [("EN", do_en), ("KO", do_ko)] if ok]
        logger.info(f"  [smart] 실패 항목 감지: {', '.join(parts)} 재분석")

    # ── 3. AI 재분석 ─────────────────────────────────────────────────────────
    from core.news.analyzer import get_analyzer
    logger.info("  AI 분석 중...")
    analyzer = get_analyzer()
    analysis = analyzer.analyze_by_lang(
        en_news=news_en if do_en else [],
        ko_news=news_ko if do_ko else [],
    )
    structured_new = analysis.get("structured", {})
    logger.info(
        f"  분석 완료: EN issues {len(structured_new.get('en',{}).get('issues',[]))}개, "
        f"KO issues {len(structured_new.get('ko',{}).get('issues',[]))}개"
    )

    # ── 4. JSON 사이드카 병합 저장 ───────────────────────────────────────────
    json_path = md_path.with_suffix(".json")
    if structured_new:
        if mode == "smart" and json_path.exists():
            try:
                existing = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                existing = {}
            # 재분석한 언어만 덮어쓰고, 기존 성공 언어는 유지
            if do_en and structured_new.get("en"):
                existing["en"] = structured_new["en"]
            if do_ko and structured_new.get("ko"):
                existing["ko"] = structured_new["ko"]
            merged = existing
        else:
            merged = structured_new
        json_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"  JSON 사이드카 저장: {json_path}")

    # ── 5. MD 분석 섹션 업데이트 ─────────────────────────────────────────────
    new_md = original_md
    if do_en and analysis.get("en") and analysis["en"] != "분석 결과 없음":
        new_md = _replace_section(new_md, EN_HEADER, analysis["en"])
        logger.info("  EN 섹션 업데이트 완료")
    if do_ko and analysis.get("ko") and analysis["ko"] != "분석 결과 없음":
        new_md = _replace_section(new_md, KO_HEADER, analysis["ko"])
        logger.info("  KO 섹션 업데이트 완료")

    if new_md != original_md:
        md_path.write_text(new_md, encoding="utf-8")
        logger.info(f"  MD 저장 완료: {md_path}")
    else:
        logger.warning("  MD 변경 없음 — 분석 결과가 비어있거나 섹션 교체 실패")

    # ── 6. HTML 재빌드 ────────────────────────────────────────────────────────
    logger.info("  HTML 재빌드 중...")
    from scripts.build_site import build
    build(from_date=date_str)
    logger.info(f"  완료: publish/news/{date_str}.html 재생성")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="기존 MD 파일 재분석 (메일 발송 없음)")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                    help="재분석 날짜 (기본: 오늘, 형식: YYYY-MM-DD)")
    ap.add_argument("--mode", choices=["smart", "full"], default="smart",
                    help="smart: 실패 항목만 재분석 (기본) | full: 전체 초기화 후 재분석")
    args = ap.parse_args()
    main(args.date, args.mode)
