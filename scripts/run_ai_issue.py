# scripts/run_ai_issue.py
"""
주간 AI 이슈 브리핑 수집·분석·저장 진입점 실행 스크립트.

실행: python scripts/run_ai_issue.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("run_ai_issue")


def main() -> None:
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("🤖 주간 AI 이슈 브리핑 (ai-issue) 가동")
    logger.info("=" * 60)
    
    parser = argparse.ArgumentParser(description="AI Issue Weekly Runner")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="주간 발행 기준 일요일 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()
    
    # KST 기준 날짜 정합 검증
    try:
        dt = datetime.strptime(args.date, "%Y-%m-%d")
        target_date = args.date
    except ValueError:
        logger.error(f"❌ 올바르지 않은 날짜 형식입니다 (YYYY-MM-DD 필요): {args.date}")
        sys.exit(1)
        
    # ── [1단계] 주간 원시 데이터셋 수집 (RSS + arXiv 1차 스코어링 + yfinance) ──
    logger.info(f"[1/3] 주간 원시 데이터 수집 개시 (기준일: {target_date})...")
    from core.ai_issue.collector import collect_weekly_raw_data
    raw_data = collect_weekly_raw_data(target_date)
    
    if not raw_data.get("articles") and not raw_data.get("paper_candidates"):
        logger.warning("❌ 이번 주 수집된 기사 및 논문 데이터가 전혀 존재하지 않습니다. 수정을 마칩니다.")
        sys.exit(0)
        
    # ── [2단계] LLM 카테고리별 정교한 종합 분석 가동 ──
    logger.info("[2/3] LLM 주간 핵심 동향 및 심층 분석 연쇄 가동...")
    from core.ai_issue.analyzer import analyze_weekly_data
    try:
        analysis_result = analyze_weekly_data(raw_data)
    except Exception as e:
        logger.error(f"  ❌ [오류] LLM 분석 실패: {e}")
        sys.exit(1)
    
    # ── [3단계] 마크다운 보고서 렌더링 및 로컬 물리 파일 영구 저장 ──
    logger.info("[3/3] Jinja2 보고서 렌더링 및 reports/ai-issue/ 영구 저장...")
    from core.ai_issue.report import generate_weekly_report, save_weekly_report
    try:
        md_content = generate_weekly_report(analysis_result)
        md_path, json_path = save_weekly_report(md_content, analysis_result)
        logger.info(f"  ✅ [성공] 마크다운 저장 완료: {md_path}")
        logger.info(f"  ✅ [성공] 구조화 JSON 저장 완료: {json_path}")
    except Exception as e:
        logger.error(f"  ❌ [오류] 보고서 생성/저장 실패: {e}")
        sys.exit(1)
        
    elapsed = (datetime.now() - start_time).seconds
    logger.info("=" * 60)
    logger.info(f"주간 AI이슈 완료! 소요 시간: {elapsed}초")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
