"""
리포트 생성 시각 추출(결정적 빌드 출력) 검증

실행: python -m pytest tests/test_report_date.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.shared.report_date import report_generated_at  # noqa: E402


@pytest.mark.parametrize("header,expected", [
    # 뉴스
    ("# Daily News Brief\n\n> 📅 생성일시: 2026-09-29 08:18 KST\n", "2026-09-29 08:18"),
    # AI이슈
    ("# AI Weekly\n생성일시: 2026-09-27 09:12 KST | 기준: 주간 AI 동향\n", "2026-09-27 09:12"),
    # 주식 일일
    ("# 📊\n\n> 데이터 기준: 2026-09-28 15:30 KST | 생성: 2026-09-28 21:27 KST\n", "2026-09-28 21:27"),
    # 주식 주간
    ("# 📅\n\n> 기간: 2026-09-21(월) ~ 2026-09-25(금) | 생성: 2026-09-26 09:00 KST\n",
     "2026-09-26 09:00"),
])
def test_extracts_generated_time_from_header(header: str, expected: str) -> None:
    assert report_generated_at(header, fallback="X") == expected


def test_missing_timestamp_uses_fallback() -> None:
    # 초기 포맷(2026-05 중순) 리포트는 머리말에 생성 시각이 없음
    assert report_generated_at("# 📰 Daily IT News — 2026-05-23\n\n> 📊 총 96건\n",
                               fallback="2026-05-23") == "2026-05-23"


def test_ignores_generated_word_in_body() -> None:
    # 본문(머리말 15줄 이후)의 '생성:' 문구는 무시 — 머리말 기준 시각만 사용
    body = "# t\n" + "\n" * 20 + "생성: 2020-01-01 00:00\n"
    assert report_generated_at(body, fallback="F") == "F"


def test_same_input_same_output() -> None:
    md = "> 생성: 2026-09-28 21:27 KST\n"
    assert report_generated_at(md, "F") == report_generated_at(md, "F")
