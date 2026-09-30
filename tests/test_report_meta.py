"""
리포트 MD 머리말 파서(core/shared/report_meta.py) 검증

- 단위: 채널별 머리말 형식, 머리말 범위 한정(본문 '기간:' 무시)
- 회귀: 저장소의 과거 리포트 전체 — Claude 루틴이 새 머리말 변형을 만들면 여기서 드러난다

실행: python -m pytest tests/test_report_meta.py -v
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.shared.report_meta import parse_report_meta  # noqa: E402

_REPORTS = _ROOT / "reports"
# 초기 포맷이라 머리말에 생성 시각 자체가 없는 리포트 (정상 — fallback 사용)
_NO_GENERATED_AT = {"news_2026-05-23.md", "news_2026-05-24.md", "stock_2026-05-18.md"}


def test_news_header() -> None:
    md = ("# Daily News Brief\n\n> 📅 생성일시: 2026-09-30 07:16 KST\n"
          "> 📊 수집: 총 150건 (EN: 78 / KO: 72) | AI 분석: 40건 | 키워드 매칭: 0건\n\n---\n\n## 🌐 x\n")
    meta = parse_report_meta(md)
    assert meta.generated_at == "2026-09-30 07:16"
    assert meta.stats == {"total": 150, "en": 78, "ko": 72, "sent_to_ai": 40}


def test_stock_daily_header() -> None:
    md = ("# 📊 일일 주식 시황 브리핑 — 2026-09-29\n\n"
          "> 데이터 기준: 2026-09-29 15:30 KST | 생성: 2026-09-29 21:35 KST\n\n---\n")
    meta = parse_report_meta(md)
    assert (meta.data_as_of, meta.generated_at) == ("2026-09-29 15:30", "2026-09-29 21:35")
    assert meta.period == "" and meta.stats == {}


def test_weekly_header_period() -> None:
    md = ("# 📅 주간 주식 시황 종합 — 2026-09-26 (주)\n\n"
          "> 기간: 2026-09-21(월) ~ 2026-09-25(금) | 생성: 2026-09-26 09:00 KST\n"
          "> ※ 추석 연휴로 휴장\n\n---\n\n## ■ 주간 한줄 총평\n")
    meta = parse_report_meta(md)
    assert meta.period == "2026-09-21(월) ~ 2026-09-25(금)"
    assert meta.generated_at == "2026-09-26 09:00"


def test_body_text_is_not_header() -> None:
    # Arrange — 머리말엔 없고 본문 섹션에만 '기간:'/'생성:'이 있는 경우
    md = ("# 📊 일일 주식 시황 브리핑\n\n---\n\n## 1. 일정\n"
          "- 공모 기간: 2026-10-01 ~ 2026-10-02 | 청약\n- 생성: 2026-01-01 00:00\n")
    # Act
    meta = parse_report_meta(md)
    # Assert — 본문은 무시
    assert meta.period == "" and meta.generated_at == ""


def _all_reports() -> list[Path]:
    files = [*_REPORTS.glob("news_*.md"), *(_REPORTS / "ai-issue").glob("ai_issue_*.md"),
             *(_REPORTS / "stock").glob("stock_*.md"), *(_REPORTS / "stock").glob("weekly_*.md")]
    return sorted(files)


@pytest.mark.parametrize("path", _all_reports(), ids=lambda p: p.name)
def test_every_historical_report_header(path: Path) -> None:
    meta = parse_report_meta(path.read_text(encoding="utf-8"))
    date_str = re.search(r"\d{4}-\d{2}-\d{2}", path.name).group()

    if path.name not in _NO_GENERATED_AT:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", meta.generated_at), "생성 시각 없음"
        # 생성 시각은 리포트 날짜 이후 7일 이내 (보통 당일, 수동 백필 예: 08-02 → 08-05 생성)
        assert date_str <= meta.generated_at[:10] <= _plus_days(date_str, 7)
    if path.name.startswith("weekly_"):
        assert re.match(r"\d{4}-\d{2}-\d{2}\(.\) ~ \d{4}-\d{2}-\d{2}\(.\)$", meta.period), meta.period
    if path.name.startswith("news_"):
        assert meta.stats.get("total", 0) > 0, "뉴스 수집 통계 없음"


def _plus_days(date_str: str, days: int) -> str:
    from datetime import date, timedelta
    return (date.fromisoformat(date_str) + timedelta(days=days)).isoformat()
