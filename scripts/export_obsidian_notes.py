"""
AI이슈 주간 리포트를 옵시디언(obsi 저장소 체크아웃) 노트로 내보낸다.

노트가 아직 없는 날짜만 만든다 — 누락 주차는 다음 실행에서 자동 백필되고,
이미 있는 노트(사용자 수기 편집 포함)는 건드리지 않는다. git commit/push는 워크플로우가 담당.

사용:
  python scripts/export_obsidian_notes.py --note-dir obsi/msshin/10-Projects/AI이슈
  python scripts/export_obsidian_notes.py --note-dir ... --date 2026-09-27 --dry-run

환경변수 (인자 미지정 시):
  OBSI_NOTE_DIR   노트 폴더 경로
  OBSI_SYNC_SINCE 이 날짜 이상 리포트만 대상 (기본 2026-08-02 — 이전은 수동 등록분)
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.ai_issue.obsidian_export import plan_exports, write_notes  # noqa: E402

logger = logging.getLogger("export_obsidian_notes")
_DEFAULT_SINCE = "2026-08-02"


def _write_github_output(created: list[str]) -> None:
    """GitHub Actions 스텝 출력(created 건수·날짜 목록)을 기록한다."""
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with Path(out).open("a", encoding="utf-8") as f:
        f.write(f"created={len(created)}\n")
        f.write(f"dates={' '.join(created)}\n")


def main() -> int:
    """인자 파싱 → 대상 계산 → 노트 생성. 성공 시 0."""
    parser = argparse.ArgumentParser(description="AI이슈 주간 리포트 → 옵시디언 노트")
    parser.add_argument("--reports-dir", default=str(_ROOT / "reports" / "ai-issue"))
    parser.add_argument("--note-dir", default=os.environ.get("OBSI_NOTE_DIR", ""))
    parser.add_argument("--since", default=os.environ.get("OBSI_SYNC_SINCE") or _DEFAULT_SINCE)
    parser.add_argument("--date", default=None, help="이 날짜 하나만 검사 (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 대상만 출력")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if not args.note_dir:
        logger.error("--note-dir 또는 OBSI_NOTE_DIR 필요")
        return 2
    note_dir = Path(args.note_dir)
    if not note_dir.is_dir():
        # 체크아웃 경로가 틀린 경우 새 폴더를 만들어 엉뚱한 곳에 게시하지 않도록 중단
        logger.error("노트 폴더 없음: %s", note_dir)
        return 2

    exports = plan_exports(Path(args.reports_dir), note_dir, args.since, args.date)
    if not exports:
        logger.info("새로 만들 노트 없음 (since=%s)", args.since)
        _write_github_output([])
        return 0

    dates = [e.date for e in exports]
    if args.dry_run:
        logger.info("[dry-run] 생성 대상 %d건: %s", len(dates), ", ".join(dates))
        return 0

    write_notes(exports)
    logger.info("노트 %d건 생성: %s", len(dates), ", ".join(dates))
    _write_github_output(dates)
    return 0


if __name__ == "__main__":
    sys.exit(main())
