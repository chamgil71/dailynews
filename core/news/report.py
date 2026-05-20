# core/report.py
"""
Markdown 리포트 생성 모듈
- 날짜 포함 파일명 (reports/news_2026-03-08.md)
- Jinja2 템플릿 렌더링
- 언어별 섹션 분리 출력
"""

import json
import logging
import os
import re
from datetime import datetime

from jinja2 import Environment, BaseLoader

from config.keywords import WATCH_KEYWORDS
from config.settings import REPORTS_DIR, REPORT_FILENAME

logger = logging.getLogger(__name__)


def _highlight(text: str) -> str:
    """감시 키워드를 **bold** 처리 (Markdown → HTML 변환 시 <strong> 적용)."""
    for kw in WATCH_KEYWORDS:
        text = re.sub(re.escape(kw), f"**{kw}**", text, flags=re.IGNORECASE)
    return text


def generate(news_data: dict, analysis: dict) -> str:
    """Markdown 리포트 문자열 생성."""
    template_path = os.path.join("templates", "daily_report.md")
    with open(template_path, "r", encoding="utf-8") as f:
        raw = f.read()

    env = Environment(loader=BaseLoader())
    env.filters["highlight"] = _highlight
    tpl = env.from_string(raw)

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M KST")

    return tpl.render(
        date         = date_str,
        analysis_en  = analysis.get("en", ""),
        analysis_ko  = analysis.get("ko", ""),
        combined     = analysis.get("combined", ""),
        news_en      = news_data.get("en", []),
        news_ko      = news_data.get("ko", []),
        keyword_news = news_data.get("keyword", []),
        stats        = news_data.get("stats", {}),
    )


def save_report(md_content: str, structured: dict | None = None) -> str:
    """리포트를 날짜별 파일로 저장. structured 데이터가 있으면 JSON 사이드카도 저장."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_tag  = datetime.now().strftime("%Y-%m-%d")
    filename  = REPORT_FILENAME.format(date=date_tag)
    filepath  = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)
    logger.info(f"[리포트 저장] {filepath}")

    if structured:
        json_path = filepath.replace(".md", ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)
        logger.info(f"[구조화 데이터 저장] {json_path}")

    return filepath
