"""
stock_send.yml 발송 대상 리포트 선택 (일일/주간 + 중복 발송 방지).

규칙 (KST 기준):
  - 일요일      → 주간 리포트(weekly_*.md)만 발송 대상
  - 화~토       → 일일 리포트(stock_*.md)만 발송 대상 (화=월 데이터 … 토=금 데이터)
  - 월요일      → 발송 없음 (cron 도 월요일 제외)
  - 최신 리포트가 3일 넘게 지났으면 발송 안 함 (휴장 연휴 등)
  - 중복 방지: 리포트 파일이 '직전 정기 발송 실행 시작 시각'보다 먼저 커밋돼 있었다면
    그 실행에서 이미 발송된 것으로 보고 건너뜀. 보낸 기록을 따로 커밋하지 않고
    git 이력(파일 최초 커밋 시각)과 GitHub API(직전 실행 시각)만으로 판단한다.
    직전 실행 시각을 모르면 '어제 날짜 리포트만' 발송하는 보수적 규칙으로 대체.
  - --date 지정(수동 재발송) 시 요일·중복 규칙 없이 해당 날짜를 그대로 발송

사용법:
  python scripts/select_stock_send_target.py --prev-run-at 2026-09-28T01:20:52Z
  python scripts/select_stock_send_target.py --date 2026-09-26
결과는 $GITHUB_OUTPUT(exists/report_date/report_file/report_type)에 기록한다.
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.shared.report_date import kst_today  # noqa: E402

logger = logging.getLogger("select_stock_send_target")

REPORTS_DIR = _ROOT / "reports" / "stock"
MAX_AGE_DAYS = 3
_PREFIX = {"daily": "stock_", "weekly": "weekly_"}


@dataclass
class Target:
    """발송 판단 결과. send=False 면 reason 에 사유."""

    send: bool
    reason: str
    report_date: str = ""
    report_type: str = ""
    report_file: str = ""


def expected_type(today: date) -> str | None:
    """요일별 발송 대상 종류. 일=weekly, 화~토=daily, 월=None."""
    wd = today.weekday()  # 월=0 … 일=6
    if wd == 6:
        return "weekly"
    if 1 <= wd <= 5:
        return "daily"
    return None


def latest_report(reports_dir: Path, rtype: str, today: date) -> tuple[str, Path] | None:
    """종류별 가장 최신 리포트 (날짜, 경로).

    아침 발송 대상은 항상 기준일 '이전' 날짜다 (일일=전 거래일, 주간=토요일자를 일요일에).
    당일·미래 날짜 파일(오기 등)은 제외.
    """
    prefix = _PREFIX[rtype]
    for path in sorted(reports_dir.glob(f"{prefix}*.md"), reverse=True):
        rdate = path.stem.removeprefix(prefix)
        try:
            if date.fromisoformat(rdate) < today:
                return rdate, path
        except ValueError:
            logger.warning("날짜 형식이 아닌 리포트 파일 무시: %s", path.name)
    return None


def file_added_at(path: Path) -> datetime | None:
    """git 이력상 파일이 처음 커밋된 시각. 미커밋·git 오류 시 None."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%cI", "--", str(path)],
            cwd=_ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning("git log 실패 (%s): %s", path.name, e)
        return None
    return datetime.fromisoformat(out[-1]) if out else None


def decide(today: date, rtype: str | None, latest: tuple[str, Path] | None,
           added_at: datetime | None, prev_run_at: datetime | None) -> Target:
    """발송 여부 판단 (순수 함수 — 테스트 대상)."""
    if rtype is None:
        return Target(False, "월요일은 발송 없음 (일일=화~토, 주간=일)")
    if latest is None:
        return Target(False, f"{rtype} 리포트 파일 없음")
    rdate, path = latest
    age = (today - date.fromisoformat(rdate)).days
    base = Target(False, "", rdate, rtype, str(path.relative_to(_ROOT)).replace("\\", "/"))
    if age > MAX_AGE_DAYS:
        base.reason = f"{rdate} 리포트 {age}일 경과 — 오래된 리포트 발송 안 함"
        return base
    if prev_run_at is None:
        # 직전 실행 시각을 모르면 '어제 날짜 리포트만' 발송 (중복보다 누락이 덜 해로운 쪽)
        base.send = age == 1
        base.reason = "직전 실행 정보 없음 — 어제 날짜 리포트만 발송" + ("" if base.send else " (해당 없음)")
        return base
    if added_at is not None and added_at < prev_run_at:
        base.reason = (f"{rdate} 리포트는 직전 발송 실행({prev_run_at.isoformat()}) 이전에 "
                       f"올라와 이미 발송됨 — 중복 발송 안 함")
        return base
    base.send = True
    base.reason = f"{rdate} {rtype} 리포트 발송 ({age}일 전)"
    return base


def manual_target(date_str: str, reports_dir: Path) -> Target:
    """수동 재발송: 날짜의 주간 → 일일 순으로 파일을 찾는다 (요일·중복 규칙 미적용)."""
    for rtype in ("weekly", "daily"):
        path = reports_dir / f"{_PREFIX[rtype]}{date_str}.md"
        if path.exists():
            rel = str(path.relative_to(_ROOT)).replace("\\", "/")
            return Target(True, f"수동 지정 {date_str} {rtype}", date_str, rtype, rel)
    return Target(False, f"지정 날짜({date_str}) 리포트 없음")


def write_output(target: Target) -> None:
    """$GITHUB_OUTPUT 기록 (없으면 로그만)."""
    path = os.environ.get("GITHUB_OUTPUT", "")
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(f"exists={'true' if target.send else 'false'}\n")
        if target.send:
            f.write(f"report_date={target.report_date}\n")
            f.write(f"report_type={target.report_type}\n")
            f.write(f"report_file={target.report_file}\n")


def _parse_prev(value: str) -> datetime | None:
    value = value.strip()
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="주식 발송 대상 리포트 선택")
    parser.add_argument("--date", default="", help="수동 재발송 날짜 (YYYY-MM-DD)")
    parser.add_argument("--prev-run-at", default="", help="직전 정기 발송 실행 시작 시각 (ISO8601)")
    parser.add_argument("--today", default="", help="기준일 (테스트용, 기본 KST 오늘)")
    args = parser.parse_args()

    if args.date:
        target = manual_target(args.date, REPORTS_DIR)
    else:
        today = date.fromisoformat(args.today or kst_today())
        rtype = expected_type(today)
        latest = latest_report(REPORTS_DIR, rtype, today) if rtype else None
        added = file_added_at(latest[1]) if latest else None
        target = decide(today, rtype, latest, added, _parse_prev(args.prev_run_at))

    logger.info("%s %s", "✅ 발송 대상:" if target.send else "⏭ 발송 안 함:", target.reason)
    write_output(target)


if __name__ == "__main__":
    main()
