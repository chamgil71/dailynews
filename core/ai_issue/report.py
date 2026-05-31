# core/ai_issue/report.py
"""
주간 AI 이슈 보고서 빌드 및 저장 모듈.
templates/ai_issue_report.md (Jinja2) 템플릿에 수집 및 분석 데이터를 주입해 MD와 JSON 파일로 저장합니다.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Environment, BaseLoader

logger = logging.getLogger(__name__)

AI_ISSUE_REPORTS_DIR = "reports/ai-issue"
AI_ISSUE_TEMPLATE = "templates/ai_issue_report.md"


def generate_weekly_report(analysis_data: dict) -> str:
    """
    analysis_data : core/ai_issue/analyzer.analyze_weekly_data()의 결과 딕셔너리
    반환           : 완성된 Markdown 리포트 문자열
    """
    template_path = Path(AI_ISSUE_TEMPLATE)
    if not template_path.exists():
        raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {AI_ISSUE_TEMPLATE}")
        
    raw_template = template_path.read_text(encoding="utf-8")
    
    # Jinja2 템플릿 로더 및 환경 구성
    env = Environment(loader=BaseLoader())
    
    # float 포맷 헬퍼 등록
    def format_float_sign(val) -> str:
        try:
            f_val = float(val)
            return f"{f_val:+.2f}"
        except (ValueError, TypeError):
            return str(val)
            
    env.filters["weekly_change_pct"] = format_float_sign
    tpl = env.from_string(raw_template)
    
    # 생성 시간대 (KST 기준)
    kst_now = datetime.now(timezone(timedelta(hours=9)))
    generated_at_str = kst_now.strftime("%Y-%m-%d %H:%M KST")
    
    # 템플릿 렌더링 수행
    rendered_md = tpl.render(
        period=analysis_data.get("period", ""),
        generated_at=generated_at_str,
        top10=analysis_data.get("top10", []),
        top3_detail=analysis_data.get("top3_detail", []),
        company_trends=analysis_data.get("company_trends", ""),
        weekly_tips=analysis_data.get("weekly_tips", []),
        stock_snapshots=analysis_data.get("stock_snapshots", []),
        paper_picks=analysis_data.get("paper_picks", []),
        next_week_outlook=analysis_data.get("next_week_outlook", "")
    )
    
    return rendered_md


def save_weekly_report(md_content: str, analysis_data: dict) -> tuple[str, str]:
    """주간 마크다운 보고서와 구조화 JSON 데이터를 reports/ai-issue/ 하위에 저장합니다."""
    # 디렉토리 생성 보장
    os.makedirs(AI_ISSUE_REPORTS_DIR, exist_ok=True)
    
    date_str = analysis_data.get("issue_date")
    if not date_str:
        date_str = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
        
    md_filename = f"ai_issue_{date_str}.md"
    json_filename = f"ai_issue_{date_str}.json"
    
    md_filepath = os.path.join(AI_ISSUE_REPORTS_DIR, md_filename)
    json_filepath = os.path.join(AI_ISSUE_REPORTS_DIR, json_filename)
    
    # 1. 마크다운 보고서 쓰기
    Path(md_filepath).write_text(md_content, encoding="utf-8")
    logger.info(f"[주간 보고서 저장] {md_filepath}")
    
    # 2. JSON 구조화 사이드카 쓰기 (인코딩 무결 보장)
    Path(json_filepath).write_text(
        json.dumps(analysis_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info(f"[주간 JSON 저장] {json_filepath}")
    
    return md_filepath, json_filepath


if __name__ == "__main__":
    # 간이 검증용
    pass
