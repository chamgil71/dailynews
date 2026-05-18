# scripts/send_stock_email.py
"""
주식 시황 이메일 발송 (Claude 루틴 push 경로 전용).

GitHub Actions stock_build.yml 의 push 트리거에서 호출.
reports/stock/ 에서 최신 MD 파일을 읽어 이메일 발송.
"""
from __future__ import annotations

import glob
import logging
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _weekday_ko(wd: int) -> str:
    return ["월","화","수","목","금","토","일"][wd]


def _email_body_from_md(md_path: str) -> str:
    """
    stock MD 에서 이메일 축약 본문 추출.
    핵심 요약 + 핵심 키워드 TOP 5 + 온도계 섹션만.
    """
    import re
    raw = Path(md_path).read_text(encoding="utf-8")

    # 축약 섹션 추출
    sections = re.findall(
        r'(## (?:■ 핵심 요약|3\. 핵심 키워드|6\. 장기투자|시장 온도계)[\s\S]*?)(?=\n---|\n## [^3^6^시]|\Z)',
        raw,
    )
    body = "\n\n".join(sections).strip()
    if not body:
        # 전체 MD에서 수집 목록 제외 (없으면 전체 반환)
        body = raw

    # 제목 추가
    date_m = re.search(r'# 📊 일일 주식 시황 브리핑 — (.+)', raw)
    title_line = date_m.group(0) if date_m else f"# 📊 주식 시황 브리핑"
    return f"{title_line}\n\n{body}"


def main() -> None:
    md_files = sorted(glob.glob("reports/stock/stock_*.md"), reverse=True)
    if not md_files:
        logger.warning("reports/stock/ 에 MD 파일 없음 — 발송 건너뜀")
        return

    latest   = md_files[0]
    date_str = Path(latest).stem.replace("stock_", "")
    logger.info(f"[send_stock_email] 대상 파일: {latest}")

    email_md = _email_body_from_md(latest)

    from core.mailer import send_email
    from config.settings import STOCK_EMAIL_SUBJECT

    now = datetime.now()
    subject = STOCK_EMAIL_SUBJECT.format(
        date=date_str,
        weekday=_weekday_ko(now.weekday()),
    )
    ok = send_email(email_md, subject_override=subject)
    logger.info(f"[send_stock_email] {'성공' if ok else '실패'}")


if __name__ == "__main__":
    main()
