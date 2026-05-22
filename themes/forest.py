# themes/forest.py
"""Forest 테마 — 핀테크 그린, 에메랄드 accent.

[표준 테마] base.py + templates/web_*.html 경유. 레이아웃 수정 → templates/, 색상 수정 → TOKENS.
"""

TOKENS = {
    "meta": {
        "name":     "forest",
        "label":    "Forest Green",
        "desc":     "에메랄드 그린, 편안한 녹색조",
        "swatch_colors": ["#064e3b", "#047857"],
        "font_cdn": "",
        "font_family": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
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
}

from themes.base import render_report as _report
from themes.base import render_archive as _archive
from themes.base import render_stock_report as _stock_report
from themes.base import render_stock_archive as _stock_archive

_NAME = "forest"

def render_report(ctx: dict) -> str:        return _report(ctx, _NAME)
def render_archive(ctx: dict) -> str:       return _archive(ctx, _NAME)
def render_stock_report(ctx: dict) -> str:  return _stock_report(ctx, _NAME)
def render_stock_archive(ctx: dict) -> str: return _stock_archive(ctx, _NAME)
