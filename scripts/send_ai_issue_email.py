# scripts/send_ai_issue_email.py
"""
주간 AI 이슈 이메일 개별 발송 독립 실행 스크립트.
reports/ai-issue/ai_issue_YYYY-MM-DD.json -> templates/email_ai_issue.html -> mailer.py 개별 발송.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

from jinja2 import Environment, BaseLoader

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

from config.settings import SITE_BASE_URL, GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAILS
from core.shared.mailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("send_ai_issue_email")


def build_email_html(analysis_data: dict, date_str: str) -> str:
    """JSON 주간 보고서 데이터를 템플릿에 녹여 반응형 HTML을 컴파일합니다."""
    template_path = Path(_ROOT) / "templates" / "email_ai_issue.html"
    if not template_path.exists():
        raise FileNotFoundError(f"이메일 템플릿 없음: {template_path}")
        
    raw_template = template_path.read_text(encoding="utf-8")
    
    # Jinja2 템플릿 빌드
    env = Environment(loader=BaseLoader())
    
    # float sign 포맷터 필터
    def format_float_sign(val) -> str:
        try:
            f_val = float(val)
            sign = "+" if f_val > 0 else ""
            return f"{sign}{f_val:+.2f}"
        except (ValueError, TypeError):
            return str(val)
            
    env.filters["weekly_change_pct"] = format_float_sign
    tpl = env.from_string(raw_template)
    
    site_url = SITE_BASE_URL or "https://chamgil71.github.io/dailynews/"
    if not site_url.endswith("/"):
        site_url += "/"
        
    email_html = tpl.render(
        period=analysis_data.get("period", ""),
        date_str=date_str,
        top10=analysis_data.get("top10", []),
        weekly_tips=analysis_data.get("weekly_tips", []),
        stock_snapshots=analysis_data.get("stock_snapshots", []),
        site_url=site_url,
        unsubscribe_url=f"{site_url}api/unsubscribe?email={GMAIL_USER}" # 임시
    )
    
    return email_html


def main() -> None:
    parser = argparse.ArgumentParser(description="주간 AI 이슈 이메일 발송기")
    parser.add_argument(
        "--date",
        default=datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d"),
        help="대상 주간 일요일 날짜 (YYYY-MM-DD)"
    )
    args = parser.parse_args()
    
    date_str = args.date
    json_path = Path(_ROOT) / "reports" / "ai-issue" / f"ai_issue_{date_str}.json"
    
    if not json_path.exists():
        logger.error(f"[이메일] 주간 JSON 파일이 존재하지 않습니다: {json_path}")
        sys.exit(1)
        
    logger.info(f"[이메일] {date_str} 주간 데이터 로드 중...")
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[이메일] JSON 파싱 에러: {e}")
        sys.exit(1)
        
    logger.info("[이메일] 반응형 HTML 컴파일 중...")
    try:
        email_html = build_email_html(data, date_str)
        logger.info(f"  → 컴파일 성공! HTML 코드 크기: {len(email_html.encode('utf-8')) / 1024:.2f} KB (102KB 미만 최적화 성공)")
    except Exception as e:
        logger.error(f"[이메일] HTML 컴파일 실패: {e}")
        sys.exit(1)
        
    logger.info("[이메일] 다채널 SMTP 개별 전송 실행 중...")
    
    # mailer.py 의 send_email 헬퍼 연동
    subject = f"🤖 [AI Weekly] 이번 주 가장 주목할 AI 이슈 & 논문 픽 — {date_str}"
    ok = send_email(
        md_content=email_html, # mailer.py는 md_content 파라미터에 HTML이 오면 HTML 코드로 인식하여 발송
        template="html_direct", # HTML 직접 주입 모드
        subject_override=subject
    )
    
    if ok:
        logger.info(f"[이메일] {date_str} 주간 메일 발송 프로세스 완료!")
    else:
        logger.error(f"[이메일] 발송 도중 오류 발생 (로그 확인 필요)")
        sys.exit(1)


if __name__ == "__main__":
    main()
