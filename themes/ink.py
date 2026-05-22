# themes/ink.py
"""Ink 테마 — 신문 스타일, 붉은 accent, 뉴트럴 배경.

[표준 테마] base.py + templates/web_*.html 경유. 레이아웃 수정 → templates/, 색상 수정 → TOKENS.
"""

TOKENS = {
    "meta": {
        "name":     "ink",
        "label":    "Ink",
        "desc":     "신문 인쇄 스타일, 묵직함과 레드",
        "swatch_colors": ["#1a1a1a", "#b91c1c"],
        "font_cdn": "",
        "font_family": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
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
}

from themes.base import render_report as _report
from themes.base import render_archive as _archive
from themes.base import render_stock_report as _stock_report
from themes.base import render_stock_archive as _stock_archive

_NAME = "ink"

def render_report(ctx: dict) -> str:        return _report(ctx, _NAME)
def render_archive(ctx: dict) -> str:       return _archive(ctx, _NAME)
def render_stock_report(ctx: dict) -> str:  return _stock_report(ctx, _NAME)
def render_stock_archive(ctx: dict) -> str: return _stock_archive(ctx, _NAME)
