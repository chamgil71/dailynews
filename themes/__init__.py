# themes/__init__.py
"""
테마 로더.
SITE_THEME 환경변수(또는 인자)에 따라 테마 모듈을 동적으로 로드한다.

각 테마 모듈은 다음 함수를 반드시 export해야 한다:
  render_report(ctx)  → str   : 날짜별 뉴스 리포트 페이지
  render_archive(ctx) → str   : 전체 목록 페이지
  render_email(ctx)   → str   : 이메일 전용 HTML (인라인 스타일)

ctx 딕셔너리 계약 (build_site.py → theme 전달):
  display_date : "2026년 05월 18일"
  date_str     : "2026-05-18"
  md_html      : markdown2 변환 HTML
  site_title   : 사이트 표시 이름
  now          : "2026-05-18 09:00"
  data         : parse_md_for_json() 결과
                 {"stats": {total, en, ko, sent_to_ai}, news_en, news_ko, ...}
  items        : archive용 [{"date": ..., "display": ...}] (archive 페이지만)
  site_url     : 사이트 베이스 URL
  subscribe_url: 구독 폼 URL
  unsubscribe_url: 구독 취소 URL (이메일 발송 시 per-recipient 설정)
  email_html   : 이메일 축약 본문 HTML (analysis 섹션만, 뉴스 목록 제외)
"""
import importlib
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (themes/ 가 루트 하위임)
_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.theme_config import SITE_THEME  # noqa: E402


def load_theme(name: str | None = None):
    """테마 이름으로 테마 모듈 반환. 없으면 classic으로 폴백."""
    theme_name = name or SITE_THEME
    try:
        return importlib.import_module(f"themes.{theme_name}")
    except ModuleNotFoundError:
        print(f"⚠  테마 '{theme_name}' 없음 → classic으로 폴백")
        return importlib.import_module("themes.classic")
