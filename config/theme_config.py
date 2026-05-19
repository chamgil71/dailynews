# config/theme_config.py
"""
디자인 시스템 설정 — 순수 설정값만 관리.
CSS·폰트·색상 등 렌더링 데이터는 themes/{name}.py의 TOKENS에 정의.

역할 구분:
  config/theme_config.py  → 어떤 테마를 쓸지, 사이트 정보, 푸터 텍스트 (설정)
  themes/{name}.py        → CSS·폰트·레이아웃 렌더링 코드 (구현)

환경변수:
  SITE_THEME       : classic | minimal | ink | forest | editorial | terminal (기본: classic)
  SITE_TITLE       : 사이트 표시 이름
  SUBSCRIBE_URL    : 구독 폼 URL
  THEME_NEWS       : 뉴스브리핑 테마  (기본: SITE_THEME)
  THEME_STOCK      : 주식시황 테마    (기본: SITE_THEME)
  THEME_EMAIL      : 메일링뉴스 테마  (기본: SITE_THEME)
  FOOTER_GENERATOR : AI 생성 모델명  (기본: Gemini 2.0 Flash)
"""
import os

# ── 기본 테마 ──────────────────────────────────────────────────────────────────
SITE_THEME    = os.getenv("SITE_THEME", "classic")
SITE_TITLE    = os.getenv("SITE_TITLE", "AI News Daily")
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL", "https://forms.gle/REPLACE_WITH_GOOGLE_FORM_ID")

# ── 섹션별 테마 (섹션마다 독립 설정 가능) ──────────────────────────────────────
SECTION_THEMES: dict[str, str] = {
    "news":  os.getenv("THEME_NEWS",   SITE_THEME),   # 뉴스브리핑 본문
    "stock": os.getenv("THEME_STOCK",  SITE_THEME),   # 주식시황 본문
    "email": os.getenv("THEME_EMAIL",  SITE_THEME),   # 메일링뉴스
}

# ── 푸터 설정 ──────────────────────────────────────────────────────────────────
FOOTER_CONFIG: dict[str, str] = {
    "generator":   os.getenv("FOOTER_GENERATOR", "Gemini 2.0 Flash"),
    "repo":        os.getenv("FOOTER_REPO",      "chamgil71/dailynews"),
    "powered_by":  "GitHub Actions · RSS Feeds",
    "update_text": "매일 자동 업데이트",
}

# ── 사용 가능한 테마 목록 (UI 표시용) ─────────────────────────────────────────
# 새 테마 추가: themes/{name}.py 생성 후 아래 목록에만 추가하면 됨
DESIGN_TEMPLATES: list[dict] = [
    {"name": "classic",   "label": "Classic Navy",  "desc": "남색 헤더, 파란 배지, 흰 카드"},
    {"name": "minimal",   "label": "Minimal",        "desc": "Pretendard, 넓은 여백, 오렌지 포인트"},
    {"name": "ink",       "label": "Ink (신문)",      "desc": "붉은 포인트, 뉴트럴 배경"},
    {"name": "forest",    "label": "Forest",          "desc": "핀테크 그린, 에메랄드 accent"},
    {"name": "editorial", "label": "Editorial",       "desc": "신문 마스트헤드, Noto Serif KR"},
    {"name": "terminal",  "label": "Terminal Dark",   "desc": "Bloomberg 터미널, 다크 모노스페이스"},
]

# ── 네비게이션 섹션 ────────────────────────────────────────────────────────────
NAV_SECTIONS: list[dict] = [
    {"key": "news",     "label": "📰 뉴스",      "url": "index.html",          "enabled": True},
    {"key": "cardnews", "label": "🃏 카드뉴스",  "url": "cardnews/index.html", "enabled": False},
    {"key": "stock",    "label": "📈 주식",      "url": "stock/index.html",    "enabled": True},
    {"key": "archive",  "label": "📚 전체 목록", "url": "archive.html",         "enabled": True},
]

# ── 허브 섹션 (Phase 2/3 활성화 시 index.html 허브 카드에 표시) ───────────────
HUB_SECTIONS: list[dict] = [
    {
        "key": "cardnews", "icon": "🃏", "label": "카드뉴스",
        "desc": "핵심 이슈 3개 + 트렌드 키워드를 슬라이드 카드로",
        "url": "cardnews/index.html", "enabled": False,
    },
    {
        "key": "stock", "icon": "📈", "label": "주식 브리핑",
        "desc": "코스피·나스닥·주요 종목 일일 시장 동향",
        "url": "stock/index.html", "enabled": True,
    },
]
