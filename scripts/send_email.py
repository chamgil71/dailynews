# scripts/send_email.py
"""
통합 이메일 발송 스크립트.
--type news|stock|ai-issue 로 채널 선택.
core/shared/mailer.py 가 실제 발송 담당.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

from core.shared.mailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("send_email")

KST_TODAY = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")


# ── news ──────────────────────────────────────────────────────────────────────
def _send_news(date_str: str, force: bool = False) -> None:
    md_path   = Path(_ROOT) / "reports" / f"news_{date_str}.md"
    json_path = Path(_ROOT) / "reports" / f"news_{date_str}.json"

    if not md_path.exists():
        logger.error(f"[이메일/뉴스] MD 파일 없음: {md_path}")
        sys.exit(1)

    # AI 분석 실패 시 구독자 발송 건너뜀 (force=True 시 무시)
    if not force and json_path.exists():
        try:
            if not json.loads(json_path.read_text(encoding="utf-8")).get("analysis_ok", True):
                logger.warning("[이메일/뉴스] AI 분석 실패 플래그 감지 — 발송 건너뜀 (강제 발송: --force 사용)")
                return
        except Exception:
            pass

    if force:
        logger.info("[이메일/뉴스] 강제 발송 모드 — analysis_ok 플래그 무시")
    ok = send_email(md_path.read_text(encoding="utf-8"), channel="news")
    logger.info(f"[이메일/뉴스] {'완료' if ok else '실패 또는 건너뜀'}")


# ── stock ─────────────────────────────────────────────────────────────────────
def _stock_analysis_complete(md_path: Path) -> bool:
    raw = md_path.read_text(encoding="utf-8")
    summary_m = re.search(r'## ■ 핵심 요약[^\n]*\n([\s\S]*?)(?=\n---|\n## )', raw)
    temp_m    = re.search(r'## 시장 온도계[^\n]*\n+>\s*(.+)', raw)
    summary   = summary_m.group(1).strip() if summary_m else ""
    reason    = temp_m.group(1).strip() if temp_m else ""
    return len(summary) > 10 and len(reason) > 5


def _send_stock(date_str: str) -> None:
    from config.settings import STOCK_EMAIL_SUBJECT

    md_path = Path(_ROOT) / "reports" / "stock" / f"stock_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[이메일/주식] MD 파일 없음: {md_path}")
        sys.exit(1)

    if not _stock_analysis_complete(md_path):
        logger.warning("[이메일/주식] 분석 미완성 — 발송 건너뜀")
        return

    report_dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday   = ["월","화","수","목","금","토","일"][report_dt.weekday()]
    subject = STOCK_EMAIL_SUBJECT.format(date=date_str, weekday=weekday)
    ok = send_email(md_path.read_text(encoding="utf-8"), template="stock", subject_override=subject, report_date=date_str, channel="stock")
    logger.info(f"[이메일/주식] {'완료' if ok else '실패 또는 건너뜀'}")


# ── weekly-stock ─────────────────────────────────────────────────────────────
def _send_weekly_stock(date_str: str) -> None:
    md_path = Path(_ROOT) / "reports" / "stock" / f"weekly_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[이메일/주간주식] MD 파일 없음: {md_path}")
        sys.exit(1)

    report_dt = datetime.strptime(date_str, "%Y-%m-%d")
    subject = f"📅 [주간 시황] {date_str} 주간 주식 종합 브리핑"
    ok = send_email(
        md_path.read_text(encoding="utf-8"),
        subject_override=subject,
        report_date=date_str,
        channel="stock",
    )
    logger.info(f"[이메일/주간주식] {'완료' if ok else '실패 또는 건너뜀'}")


# ── ai-issue ──────────────────────────────────────────────────────────────────
def _build_ai_issue_html(data: dict, date_str: str) -> str:
    from jinja2 import Environment, BaseLoader
    from config.settings import SITE_BASE_URL, GMAIL_USER

    template_path = Path(_ROOT) / "templates" / "email_ai_issue.html"
    if not template_path.exists():
        raise FileNotFoundError(f"이메일 템플릿 없음: {template_path}")

    env = Environment(loader=BaseLoader())

    def _fmt_sign(val) -> str:
        try:
            return f"{float(val):+.2f}"
        except (ValueError, TypeError):
            return str(val)

    env.filters["weekly_change_pct"] = _fmt_sign
    tpl = env.from_string(template_path.read_text(encoding="utf-8"))

    site_url = (SITE_BASE_URL or "https://chamgil71.github.io/dailynews/").rstrip("/") + "/"
    return tpl.render(
        period=data.get("period", ""),
        date_str=date_str,
        top10=data.get("top10", []),
        weekly_tips=data.get("weekly_tips", []),
        stock_snapshots=data.get("stock_snapshots", []),
        site_url=site_url,
        unsubscribe_url=f"{site_url}api/unsubscribe?email={GMAIL_USER}",
    )


def _send_ai_issue(date_str: str) -> None:
    json_path = Path(_ROOT) / "reports" / "ai-issue" / f"ai_issue_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[이메일/AI이슈] JSON 파일 없음: {json_path}")
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"[이메일/AI이슈] JSON 파싱 에러: {e}")
        sys.exit(1)

    # 빈 top10(=잘린/불완전 데이터)으로 공란 이메일이 발송되는 것을 방지
    if not data.get("top10"):
        logger.error("[이메일/AI이슈] top10 데이터 공란 — 불완전 보고서로 판단, 발송 건너뜀")
        sys.exit(1)

    try:
        html = _build_ai_issue_html(data, date_str)
        logger.info(f"[이메일/AI이슈] 템플릿 컴파일 완료 ({len(html.encode()) // 1024}KB)")
    except Exception as e:
        logger.error(f"[이메일/AI이슈] 템플릿 컴파일 실패: {e}")
        sys.exit(1)

    subject = f"🤖 [AI Weekly] 이번 주 가장 주목할 AI 이슈 & 논문 픽 — {date_str}"
    ok = send_email(html_content=html, subject_override=subject, channel="ai-issue")
    logger.info(f"[이메일/AI이슈] {'완료' if ok else '실패 또는 건너뜀'}")


# ── 진입점 ────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="통합 이메일 발송기")
    parser.add_argument("--type", choices=["news", "stock", "weekly-stock", "ai-issue"], required=True)
    parser.add_argument("--date", default=KST_TODAY, help="대상 날짜 (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="AI 분석 실패 플래그 무시하고 강제 발송 (news 전용)")
    args = parser.parse_args()

    logger.info(f"[이메일] type={args.type} date={args.date} force={args.force}")
    if args.type == "news":
        _send_news(args.date, force=args.force)
    else:
        {"stock": _send_stock, "weekly-stock": _send_weekly_stock, "ai-issue": _send_ai_issue}[args.type](args.date)


if __name__ == "__main__":
    main()
