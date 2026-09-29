"""
주식 발송 대상 선택(요일 규칙·중복 방지) + 주간 표기 검증

실행: python -m pytest tests/test_stock_send_target.py -v
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from core.shared.report_date import weekly_label  # noqa: E402
from core.shared.sns_source import stock_fields  # noqa: E402
from scripts import select_stock_send_target as sel  # noqa: E402

KST = timezone(timedelta(hours=9))


def _kst(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=KST)


def _report(rtype: str, d: str) -> tuple[str, Path]:
    prefix = "weekly_" if rtype == "weekly" else "stock_"
    return d, _ROOT / "reports" / "stock" / f"{prefix}{d}.md"


# ── 요일 규칙 ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("d,expected", [
    ("2026-09-27", "weekly"),   # 일
    ("2026-09-28", None),       # 월
    ("2026-09-29", "daily"),    # 화
    ("2026-10-03", "daily"),    # 토 (금요일 데이터)
])
def test_expected_type_by_weekday(d: str, expected: str | None) -> None:
    assert sel.expected_type(date.fromisoformat(d)) == expected


# ── 실제 사례 재현 ────────────────────────────────────────────────────────────
def test_weekly_sent_on_sunday() -> None:
    # Arrange — 토 15:19 주간 리포트 push, 직전 정기 실행은 토 10:07
    t = sel.decide(date(2026, 9, 27), "weekly", _report("weekly", "2026-09-26"),
                   added_at=_kst("2026-09-26T15:19:00"), prev_run_at=_kst("2026-09-26T10:07:00"))
    # Assert
    assert t.send and t.report_type == "weekly"
    assert t.report_file == "reports/stock/weekly_2026-09-26.md"


def test_monday_never_sends() -> None:
    # 기존 버그: 월요일에 주간 리포트 재발송 (9/14, 9/21, 9/28)
    t = sel.decide(date(2026, 9, 28), None, None, None, _kst("2026-09-27T10:03:00"))
    assert not t.send


def test_holiday_does_not_resend_same_daily() -> None:
    # 기존 버그: 추석 9/23 리포트가 9/24·9/25·9/26 세 번 발송
    added = _kst("2026-09-23T22:10:00")
    first = sel.decide(date(2026, 9, 24), "daily", _report("daily", "2026-09-23"),
                       added, _kst("2026-09-23T10:10:00"))
    second = sel.decide(date(2026, 9, 25), "daily", _report("daily", "2026-09-23"),
                        added, _kst("2026-09-24T10:00:00"))
    assert first.send
    assert not second.send and "이미 발송" in second.reason


def test_late_report_is_recovered_next_day() -> None:
    # 6/8 사례: 08시 실행 이후 09:45 에 올라온 리포트는 다음 실행에서 발송
    t = sel.decide(date(2026, 6, 10), "daily", _report("daily", "2026-06-08"),
                   added_at=_kst("2026-06-09T09:45:00"), prev_run_at=_kst("2026-06-09T08:30:00"))
    assert t.send


def test_stale_report_skipped() -> None:
    t = sel.decide(date(2026, 10, 6), "daily", _report("daily", "2026-10-01"),
                   _kst("2026-10-01T22:00:00"), None)
    assert not t.send and "경과" in t.reason


@pytest.mark.parametrize("report_day,expected", [("2026-09-28", True), ("2026-09-27", False)])
def test_unknown_prev_run_falls_back_to_yesterday_only(report_day: str, expected: bool) -> None:
    t = sel.decide(date(2026, 9, 29), "daily", _report("daily", report_day),
                   _kst(f"{report_day}T22:00:00"), prev_run_at=None)
    assert t.send is expected


def test_uncommitted_file_is_treated_as_new() -> None:
    t = sel.decide(date(2026, 9, 29), "daily", _report("daily", "2026-09-28"),
                   added_at=None, prev_run_at=_kst("2026-09-28T10:00:00"))
    assert t.send


def test_latest_report_ignores_same_day_future_and_malformed(tmp_path: Path) -> None:
    for name in ("stock_2026-09-23.md", "stock_2026-09-26.md", "stock_2026-09-28.md", "stock_draft.md"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    rdate, _ = sel.latest_report(tmp_path, "daily", date(2026, 9, 26))
    assert rdate == "2026-09-23"
    assert sel.latest_report(tmp_path, "weekly", date(2026, 9, 26)) is None


# ── 수동 재발송 ───────────────────────────────────────────────────────────────
def test_manual_prefers_weekly_then_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sel, "_ROOT", tmp_path)
    (tmp_path / "stock_2026-09-25.md").write_text("x", encoding="utf-8")
    (tmp_path / "weekly_2026-09-26.md").write_text("x", encoding="utf-8")
    assert sel.manual_target("2026-09-26", tmp_path).report_type == "weekly"
    assert sel.manual_target("2026-09-25", tmp_path).report_type == "daily"
    assert not sel.manual_target("2026-09-24", tmp_path).send


def test_write_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    sel.write_output(sel.Target(True, "ok", "2026-09-26", "weekly", "reports/stock/weekly_2026-09-26.md"))
    text = out.read_text(encoding="utf-8")
    assert "exists=true" in text and "report_type=weekly" in text


# ── 주간 표기 ─────────────────────────────────────────────────────────────────
def test_weekly_label_format() -> None:
    assert weekly_label("2026-09-26") == "2026-09-26 (주간)"


def test_weekly_stock_fields_use_hot_themes() -> None:
    entry = {"date": "2026-09-26", "type": "weekly", "summary": "총평",
             "hot_themes": [{"title": "반도체·AI 랠리", "description": "설명"}], "keywords": []}
    fields = stock_fields(entry)
    assert fields["is_weekly"] is True
    assert fields["keywords"] == [{"title": "반도체·AI 랠리", "body": "설명"}]


def test_weekly_caption_header(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import post_cardnews
    monkeypatch.setattr(post_cardnews.sns_source, "caption_fields", lambda c, d: {
        "is_weekly": True, "summary": "총평", "temperature": {"display": "🟠 강세"},
        "keywords": [{"title": "반도체"}]})
    caption = post_cardnews._build_caption("stock", "2026-09-26")
    assert caption.startswith("📅 2026-09-26 (주간) 주식 시황 종합")
    assert "주간 온도계: 🟠 강세" in caption and "🔥 핫 테마: 반도체" in caption
