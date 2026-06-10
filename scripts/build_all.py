# scripts/build_all.py
"""
통합 사이트 빌더 — 뉴스, 주식, AI이슈 3개 채널 오케스트레이션.

사용법:
  python scripts/build_all.py                          # 최신 데이터만 빌드
  python scripts/build_all.py --theme editorial        # 전체 테마 지정 빌드
  python scripts/build_all.py --all                    # 과거 리포트 포함 전체 재빌드 (일괄 업데이트)
  python scripts/build_all.py --type news              # 뉴스 채널만 빌드
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import scripts.build_site as build_news
import scripts.build_stock_site as build_stock
import scripts.build_ai_issue_site as build_ai


def main() -> None:
    parser = argparse.ArgumentParser(description="AI News Brief 통합 사이트 빌더")
    parser.add_argument("--theme", default=None,
                        help="테마 이름 (classic|minimal|ink|forest|editorial|terminal)")
    parser.add_argument("--type", choices=["all", "news", "stock", "ai-issue"], default="all",
                        help="빌드할 채널 (기본: all)")
    parser.add_argument("--from", dest="from_date", default=None, nargs="?",
                        const="TODAY", metavar="YYYY-MM-DD",
                        help="이 날짜 이후 파일만 빌드. "
                             "날짜 생략 시(--from 만 입력) 오늘 파일만 빌드")
    parser.add_argument("--all", action="store_true",
                        help="모든 날짜 강제 재빌드 (일괄 변경)")
    args = parser.parse_args()

    from_date = args.from_date
    if from_date == "TODAY":
        from_date = datetime.now().strftime("%Y-%m-%d")

    channels = ["news", "stock", "ai-issue"] if args.type == "all" else [args.type]
    print(f"\n==========================================")
    print(f"[build-all] 시작 (채널: {args.type}, 테마: {args.theme or '기본값'}, 재빌드: {args.all})")
    print(f"==========================================\n")

    # 1. 뉴스 빌드
    if "news" in channels:
        print("------------------------------------------")
        print("[1/3] 뉴스 브리핑 빌드 기동...")
        print("------------------------------------------")
        build_news.build(
            theme_name=args.theme,
            from_date=from_date,
            rebuild_all=args.all
        )

    # 2. 주식 빌드
    if "stock" in channels:
        print("\n------------------------------------------")
        print("[2/3] 주식 시황 빌드 기동...")
        print("------------------------------------------")
        # 주식 빌더는 --all 옵션이 주어지거나 from_date 필터링이 없을 때 컴파일을 수행
        build_stock.build(theme_name=args.theme)

    # 3. AI이슈 빌드
    if "ai-issue" in channels:
        print("\n------------------------------------------")
        print("[3/3] AI 주간 이슈 빌드 기동...")
        print("------------------------------------------")
        build_ai.build(theme_name=args.theme)

    # 4. 통합 검색 인덱스 재빌드 (전체 완료 후 갱신 보장)
    print("\n------------------------------------------")
    print("[통합] search-index.json 통합 인덱스 빌드...")
    print("------------------------------------------")
    build_news.build_search_index()

    print(f"\n[build-all] 모든 빌드 전과정이 성공 완료되었습니다.\n")


if __name__ == "__main__":
    main()
