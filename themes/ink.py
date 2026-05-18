# themes/ink.py
"""Ink 테마 (신문). Classic 레이아웃, 붉은 accent."""
from themes.base import render_report as _report
from themes.base import render_archive as _archive
from themes.base import render_email as _email
from themes.base import render_stock_report as _stock_report
from themes.base import render_stock_archive as _stock_archive
from themes.base import render_stock_email as _stock_email

_NAME = "ink"


def render_report(ctx: dict) -> str:
    return _report(ctx, _NAME)

def render_archive(ctx: dict) -> str:
    return _archive(ctx, _NAME)

def render_email(ctx: dict) -> str:
    return _email(ctx, _NAME)

def render_stock_report(ctx: dict) -> str:
    return _stock_report(ctx, _NAME)

def render_stock_archive(ctx: dict) -> str:
    return _stock_archive(ctx, _NAME)

def render_stock_email(ctx: dict) -> str:
    return _stock_email(ctx, _NAME)
