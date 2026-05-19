# themes/__init__.py
"""
테마 로더.
SITE_THEME 환경변수(또는 인자)에 따라 테마 모듈을 동적으로 로드한다.

── 테마 종류 ──────────────────────────────────────────────────────────
[레이아웃 테마] 독립 레이아웃·폰트·구조 — CSS 전체 자체 보유
  classic    — 네이비 헤더, 카드 레이아웃, 시스템 폰트
  editorial  — 신문 마스트헤드, Noto Serif KR
  terminal   — Bloomberg 다크 터미널, JetBrains Mono

[색상 변형 테마] base 레이아웃 위임, CSS 토큰(TOKENS)만 교체
  ink        — 붉은 accent (신문 느낌)
  forest     — 에메랄드 accent (핀테크 그린)
  minimal    — 오렌지 accent + 여백 CSS 오버라이드

── 새 테마 추가 방법 ───────────────────────────────────────────────
1. themes/{name}.py 생성
2. TOKENS = { "meta": {...}, "colors": {...}, "typography": {...} } 정의
3. render_report(), render_archive(), render_email() 등 구현
4. (선택) config/theme_config.py DESIGN_TEMPLATES에 추가 (UI 표시용)
──────────────────────────────────────────────────────────────────────

── config vs themes 역할 경계 ─────────────────────────────────────
  config/theme_config.py  → 어떤 테마 쓸지 (SECTION_THEMES, 설정값만)
  themes/{name}.py        → CSS·폰트·레이아웃 렌더링 코드 + TOKENS
  themes/base.py          → 공통 렌더링 엔진, get_tokens() 동적 로드
──────────────────────────────────────────────────────────────────────

각 테마 모듈이 export해야 하는 함수:
  render_report(ctx)        → str  : 날짜별 뉴스 리포트 페이지
  render_archive(ctx)       → str  : 전체 목록 페이지
  render_email(ctx)         → str  : 이메일 전용 HTML
  render_stock_report(ctx)  → str  : 주식시황 리포트
  render_stock_archive(ctx) → str  : 주식 전체 목록
  render_stock_email(ctx)   → str  : 주식 이메일

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
