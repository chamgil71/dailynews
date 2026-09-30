"""
AI이슈 → 옵시디언 노트 내보내기 검증

실행: python -m pytest tests/test_obsidian_export.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.ai_issue.obsidian_export import (  # noqa: E402
    build_weekly_note, note_filename, plan_exports, write_notes,
)

_EXPECTED_FRONT = (
    "---\ntitle: ai_issue_주간_2026-09-27\npublish: true\ntype:\n  - report\n"
    "tags:\n  - AI이슈\nsource:\ncreated: 2026-09-27\nmodified: 2026-09-27\n---\n\n"
)


def _make_reports(tmp_path: Path, dates: list[str]) -> Path:
    reports = tmp_path / "reports"
    reports.mkdir()
    for d in dates:
        (reports / f"ai_issue_{d}.md").write_bytes(f"# 🤖 AI Issue Weekly {d}\r\n본문\r\n".encode())
        (reports / f"ai_issue_{d}.json").write_text("{}", encoding="utf-8")
    return reports


def test_note_has_frontmatter_and_body_with_lf() -> None:
    # Arrange
    body = "# 🤖 AI Issue Weekly\r\n\r\n본문\r\n"
    # Act
    note = build_weekly_note("2026-09-27", body)
    # Assert — 수동 등록 노트와 동일한 프론트매터 + 본문 그대로(개행만 LF)
    assert note == _EXPECTED_FRONT + "# 🤖 AI Issue Weekly\n\n본문\n"
    assert note_filename("2026-09-27") == "ai_issue_주간_2026-09-27.md"


def test_plan_skips_before_since_and_existing_notes(tmp_path: Path) -> None:
    # Arrange
    reports = _make_reports(tmp_path, ["2026-07-26", "2026-08-02", "2026-08-09", "2026-09-27"])
    notes = tmp_path / "notes"
    notes.mkdir()
    existing = notes / note_filename("2026-08-09")
    existing.write_text("사용자가 고친 노트", encoding="utf-8")
    # Act
    plan = plan_exports(reports, notes, since="2026-08-02")
    # Assert — 07-26(수동 구간)·08-09(이미 존재) 제외, json 무시, 날짜순
    assert [p.date for p in plan] == ["2026-08-02", "2026-09-27"]


def test_only_date_limits_target(tmp_path: Path) -> None:
    reports = _make_reports(tmp_path, ["2026-08-02", "2026-09-27"])
    notes = tmp_path / "notes"
    notes.mkdir()
    plan = plan_exports(reports, notes, since="2026-08-02", only_date="2026-09-27")
    assert [p.date for p in plan] == ["2026-09-27"]


def test_write_never_overwrites_existing_note(tmp_path: Path) -> None:
    # Arrange
    reports = _make_reports(tmp_path, ["2026-08-02", "2026-08-09"])
    notes = tmp_path / "notes"
    notes.mkdir()
    existing = notes / note_filename("2026-08-09")
    existing.write_text("사용자가 고친 노트", encoding="utf-8")
    # Act
    written = write_notes(plan_exports(reports, notes, since="2026-08-02"))
    # Assert
    assert [p.name for p in written] == [note_filename("2026-08-02")]
    assert existing.read_text(encoding="utf-8") == "사용자가 고친 노트"
    created = (notes / note_filename("2026-08-02")).read_bytes().decode("utf-8")
    assert created.startswith("---\ntitle: ai_issue_주간_2026-08-02\n")
    assert "\r" not in created
    # 두 번째 실행은 아무것도 만들지 않음 (멱등)
    assert plan_exports(reports, notes, since="2026-08-02") == []
