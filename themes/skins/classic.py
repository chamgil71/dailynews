# themes/classic.py
"""Classic Navy 테마 — 남색 헤더, 카드 레이아웃, 시스템 폰트.

[표준 테마] base.py + templates/web_*.html 경유. 레이아웃 수정 → templates/, 색상 수정 → TOKENS.
"""

TOKENS = {
    "meta": {
        "name":     "classic",
        "label":    "Classic Navy",
        "desc":     "남색 헤더, 깔끔한 카드 레이아웃",
        "swatch_colors": ["#1e3a5f", "#2563eb"],
        "font_cdn": "",
        "font_family": "-apple-system, 'Segoe UI', 'Apple SD Gothic Neo', sans-serif",
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
}

from themes.base import render_report as _report
from themes.base import render_archive as _archive
from themes.base import render_stock_report as _stock_report
from themes.base import render_stock_archive as _stock_archive

_NAME = "classic"

def render_report(ctx: dict) -> str:        return _report(ctx, _NAME)
def render_archive(ctx: dict) -> str:       return _archive(ctx, _NAME)
def render_stock_report(ctx: dict) -> str:  return _stock_report(ctx, _NAME)
def render_stock_archive(ctx: dict) -> str: return _stock_archive(ctx, _NAME)
