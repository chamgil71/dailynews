"""
AI이슈 주간 리포트 → 옵시디언(obsi 저장소) 노트 변환

obsi 저장소에 `publish: true` 노트가 push되면 obsi 쪽 워크플로우가 mywiki(Quartz)로
자동 게시한다. 이 모듈은 노트 파일 내용·경로만 결정하며 git 작업은 하지 않는다.

노트 형식 (2026-07-26까지 수동 등록분과 동일):
  ---
  title: ai_issue_주간_YYYY-MM-DD
  publish: true
  type: [report]
  tags: [AI이슈]
  source:
  created/modified: 리포트 날짜
  ---
  (빈 줄) + reports/ai-issue/ai_issue_YYYY-MM-DD.md 본문 그대로
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

_REPORT_RE = re.compile(r"^ai_issue_(\d{4}-\d{2}-\d{2})\.md$")
NOTE_PREFIX = "ai_issue_주간_"


@dataclass(frozen=True)
class NoteExport:
    """생성 대상 노트 1건."""

    date: str
    report_path: Path
    note_path: Path


def note_filename(date_str: str) -> str:
    """리포트 날짜 → 노트 파일명 (`ai_issue_주간_YYYY-MM-DD.md`)."""
    return f"{NOTE_PREFIX}{date_str}.md"


def build_weekly_note(date_str: str, report_body: str) -> str:
    """리포트 본문 앞에 옵시디언 프론트매터를 붙인 노트 내용을 반환한다 (LF 개행)."""
    body = report_body.replace("\r\n", "\n").lstrip("﻿")
    title = note_filename(date_str)[:-3]
    front = (
        "---\n"
        f"title: {title}\n"
        "publish: true\n"
        "type:\n"
        "  - report\n"
        "tags:\n"
        "  - AI이슈\n"
        "source:\n"
        f"created: {date_str}\n"
        f"modified: {date_str}\n"
        "---\n"
    )
    return f"{front}\n{body}"


def plan_exports(reports_dir: Path, note_dir: Path, since: str,
                 only_date: str | None = None) -> list[NoteExport]:
    """
    아직 노트가 없는 리포트 목록을 날짜순으로 반환한다.

    - since 이전 날짜 리포트는 대상에서 제외 (수동 등록 구간 보호)
    - 노트 파일이 이미 있으면 제외 — 사용자가 옵시디언에서 고친 내용을 덮어쓰지 않는다
    - only_date 지정 시 그 날짜만 검사
    """
    exports: list[NoteExport] = []
    for report in sorted(reports_dir.glob("ai_issue_*.md")):
        m = _REPORT_RE.match(report.name)
        if not m:
            continue
        date_str = m.group(1)
        if date_str < since or (only_date and date_str != only_date):
            continue
        note_path = note_dir / note_filename(date_str)
        if note_path.exists():
            logger.info("건너뜀(이미 존재): %s", note_path.name)
            continue
        exports.append(NoteExport(date_str, report, note_path))
    return exports


def write_notes(exports: list[NoteExport]) -> list[Path]:
    """계획된 노트를 파일로 쓴다. 생성한 경로 목록을 반환한다."""
    written: list[Path] = []
    for item in exports:
        body = item.report_path.read_text(encoding="utf-8")
        item.note_path.parent.mkdir(parents=True, exist_ok=True)
        item.note_path.write_bytes(build_weekly_note(item.date, body).encode("utf-8"))
        written.append(item.note_path)
        logger.info("생성: %s", item.note_path.name)
    return written
