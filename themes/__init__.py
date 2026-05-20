# themes/__init__.py
"""
테마 로더.

── 역할 분담 ──────────────────────────────────────────────────────────
  templates/*.html     → HTML 구조 (Jinja2 템플릿, HTML 수정 시 이 파일)
  themes/{name}.py     → 색상·폰트 토큰 (TOKENS, 디자인 수정 시 이 파일)
  themes/base.py       → Jinja2 렌더링 엔진 (렌더 로직 수정 시 이 파일)
  config/theme_config.py → 어떤 테마 쓸지 (SECTION_THEMES)

── 테마 종류 ──────────────────────────────────────────────────────────
[표준 테마] templates/*.html + TOKENS으로 구성
  classic    — 네이비 헤더, 카드 레이아웃, 시스템 폰트
  ink        — 붉은 accent (신문 느낌)
  forest     — 에메랄드 accent (핀테크 그린)

[커스텀 레이아웃 테마] 자체 render_* 함수로 완전히 다른 HTML 구조
  minimal    — Pretendard, 넓은 여백, 오렌지 accent
  editorial  — 신문 마스트헤드, Noto Serif KR
  terminal   — Bloomberg 터미널, 다크 모노스페이스

── 테마 파일이 export하는 함수 ────────────────────────────────────────
  render_report(ctx)        → str  : 날짜별 뉴스 리포트 페이지
  render_archive(ctx)       → str  : 전체 목록 페이지
  render_stock_report(ctx)  → str  : 주식시황 리포트
  render_stock_archive(ctx) → str  : 주식 전체 목록

── 이메일 템플릿 ──────────────────────────────────────────────────────
  templates/email_news.html   — 뉴스 이메일 (Jinja2, core/shared/mailer.py가 렌더링)
  templates/email_stock.html  — 주식 이메일 (동일)
  이메일은 테마 render_* 함수와 무관하게 mailer.py가 직접 처리.

── 새 테마 추가 방법 ──────────────────────────────────────────────────
1. themes/{name}.py 생성 후 TOKENS 정의
2. 표준 테마: base.py render_* 함수를 그대로 위임
   커스텀 테마: 자체 render_* 함수 구현
3. config/theme_config.py DESIGN_TEMPLATES에 추가 (UI 표시용)
──────────────────────────────────────────────────────────────────────
"""
import importlib
import sys
from pathlib import Path

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
