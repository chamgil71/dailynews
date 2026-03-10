# core/report.py
"""
Markdown 리포트 생성 모듈
- 날짜 포함 파일명 (reports/news_2026-03-08.md)
- Jinja2 템플릿 렌더링
- 언어별 섹션 분리 출력
"""

import logging
import os
from datetime import datetime

from jinja2 import Template

from config.settings import REPORTS_DIR, REPORT_FILENAME

logger = logging.getLogger(__name__)


def generate(news_data: dict, analysis: dict) -> str:
    """Markdown 리포트 문자열 생성."""
    template_path = os.path.join("templates", "daily_report.md")
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M KST")

    return tpl.render(
        date        = date_str,
        analysis_en = analysis.get("en", ""),
        analysis_ko = analysis.get("ko", ""),
        combined    = analysis.get("combined", ""),
        news_en     = news_data.get("en", []),
        news_ko     = news_data.get("ko", []),
        stats       = news_data.get("stats", {}),
    )


def save_report(md_content: str) -> str:
    """리포트를 날짜별 파일로 저장. 저장 경로 반환."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_tag  = datetime.now().strftime("%Y-%m-%d")
    filename  = REPORT_FILENAME.format(date=date_tag)
    filepath  = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info(f"[리포트 저장] {filepath}")
    return filepath
