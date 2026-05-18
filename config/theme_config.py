# config/theme_config.py
"""
디자인 시스템 설정.
설정(config) - 코드(themes) - 콘텐츠(reports/publish) 분리 원칙에 따라
모든 디자인 토큰과 사이트 구조 설정을 여기서 관리한다.

환경변수:
  SITE_THEME   : classic | minimal | ink | forest  (기본: classic)
  SITE_TITLE   : 사이트 표시 이름                  (기본: AI News Daily)
  SUBSCRIBE_URL: 구독 폼 URL
"""
import os

# ── 활성 테마 ──────────────────────────────────────────────────────────────────
SITE_THEME    = os.getenv("SITE_THEME", "classic")
SITE_TITLE    = os.getenv("SITE_TITLE", "AI News Daily")
SUBSCRIBE_URL = os.getenv("SUBSCRIBE_URL", "https://forms.gle/REPLACE_WITH_GOOGLE_FORM_ID")

# ── 네비게이션 섹션 ────────────────────────────────────────────────────────────
# enabled=False 항목은 해당 Phase 구현 완료 시 True로 전환.
# url은 publish/ 기준 상대경로.
NAV_SECTIONS: list[dict] = [
    {"key": "news",     "label": "📰 뉴스",      "url": "index.html",          "enabled": True},
    {"key": "cardnews", "label": "🃏 카드뉴스",  "url": "cardnews/index.html", "enabled": False},
    {"key": "stock",    "label": "📈 주식",      "url": "stock/index.html",    "enabled": True},
    {"key": "archive",  "label": "📚 전체 목록", "url": "archive.html",         "enabled": True},
]

# ── 허브 섹션 정의 (Phase 2/3 활성화 시 index.html 허브 카드에 표시) ──────────
HUB_SECTIONS: list[dict] = [
    {
        "key":     "cardnews",
        "icon":    "🃏",
        "label":   "카드뉴스",
        "desc":    "핵심 이슈 3개 + 트렌드 키워드를 슬라이드 카드로",
        "url":     "cardnews/index.html",
        "enabled": False,
    },
    {
        "key":     "stock",
        "icon":    "📈",
        "label":   "주식 브리핑",
        "desc":    "코스피·나스닥·주요 종목 일일 시장 동향",
        "url":     "stock/index.html",
        "enabled": True,
    },
]

# ── 테마별 디자인 토큰 ─────────────────────────────────────────────────────────
# colors  : CSS 변수값 (웹용 CSS vars + 이메일 인라인 스타일에 공통 사용)
# typography: 폰트 패밀리, line-height
# meta    : 테마 이름, 라벨, 웹폰트 CDN URL
THEME_TOKENS: dict[str, dict] = {

    # ── Classic Navy (기본) ───────────────────────────────────────────────────
    "classic": {
        "meta": {
            "name":     "classic",
            "label":    "Classic Navy",
            "font_cdn": "",
        },
        "colors": {
            "blue":         "#2563eb",
            "blue_light":   "#60a5fa",
            "blue_50":      "#eff6ff",
            "blue_200":     "#bfdbfe",
            "navy":         "#1e3a5f",
            "bg":           "#f8fafc",
            "card":         "#ffffff",
            "border":       "#e2e8f0",
            "text":         "#1e293b",
            "muted":        "#64748b",
            "code_bg":      "#f1f5f9",
            "green":        "#16a34a",
            "green_50":     "#f0fdf4",
            "green_200":    "#bbf7d0",
            "orange":       "#ea580c",
            "orange_50":    "#fff7ed",
            "orange_200":   "#fed7aa",
        },
        "typography": {
            "font_sans": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
            "leading":   1.7,
        },
    },

    # ── Minimal / Substack풍 ──────────────────────────────────────────────────
    "minimal": {
        "meta": {
            "name":     "minimal",
            "label":    "Minimal",
            "font_cdn": "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css",
        },
        "colors": {
            "blue":         "#ff5a1f",
            "blue_light":   "#ff8c00",
            "blue_50":      "#f1efe8",
            "blue_200":     "#e6e2da",
            "navy":         "#16181a",
            "bg":           "#fafaf7",
            "card":         "#ffffff",
            "border":       "#e6e2da",
            "text":         "#16181a",
            "muted":        "#8a8f95",
            "code_bg":      "#f1efe8",
            "green":        "#16a34a",
            "green_50":     "#f0fdf4",
            "green_200":    "#bbf7d0",
            "orange":       "#ea580c",
            "orange_50":    "#fff7ed",
            "orange_200":   "#fed7aa",
        },
        "typography": {
            "font_sans": "'Pretendard Variable', 'Pretendard', -apple-system, sans-serif",
            "leading":   1.75,
        },
    },

    # ── Ink / 신문 ────────────────────────────────────────────────────────────
    "ink": {
        "meta": {
            "name":     "ink",
            "label":    "Ink (신문)",
            "font_cdn": "",
        },
        "colors": {
            "blue":         "#b91c1c",
            "blue_light":   "#f87171",
            "blue_50":      "#fef2f2",
            "blue_200":     "#fecaca",
            "navy":         "#1a1a1a",
            "bg":           "#f7f5f0",
            "card":         "#ffffff",
            "border":       "#d6d3ce",
            "text":         "#1a1a1a",
            "muted":        "#57534e",
            "code_bg":      "#efece6",
            "green":        "#166534",
            "green_50":     "#f0fdf4",
            "green_200":    "#bbf7d0",
            "orange":       "#c2410c",
            "orange_50":    "#fff7ed",
            "orange_200":   "#fed7aa",
        },
        "typography": {
            "font_sans": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
            "leading":   1.65,
        },
    },

    # ── Forest / 핀테크 그린 ──────────────────────────────────────────────────
    "forest": {
        "meta": {
            "name":     "forest",
            "label":    "Forest",
            "font_cdn": "",
        },
        "colors": {
            "blue":         "#047857",
            "blue_light":   "#6ee7b7",
            "blue_50":      "#ecfdf5",
            "blue_200":     "#a7f3d0",
            "navy":         "#064e3b",
            "bg":           "#f6faf8",
            "card":         "#ffffff",
            "border":       "#d1e7dc",
            "text":         "#0f2922",
            "muted":        "#4b6b5e",
            "code_bg":      "#ecf3ef",
            "green":        "#0f766e",
            "green_50":     "#ecfeff",
            "green_200":    "#99f6e4",
            "orange":       "#b45309",
            "orange_50":    "#fffbeb",
            "orange_200":   "#fde68a",
        },
        "typography": {
            "font_sans": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
            "leading":   1.7,
        },
    },
}
