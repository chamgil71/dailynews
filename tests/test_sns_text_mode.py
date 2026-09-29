"""
카드뉴스 SNS 텍스트 모드 · 플랫폼별 실패 리포트 검증

실행: python -m pytest tests/test_sns_text_mode.py -v
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.shared import sns_source  # noqa: E402
from core.shared.sns_report import PlatformSkipped, SnsReport, classify_error  # noqa: E402
from scripts import notify_pipeline, post_cardnews  # noqa: E402


@pytest.fixture
def publish(tmp_path: Path) -> Path:
    """3채널 원본 발행 데이터 최소 샘플."""
    (tmp_path / "news").mkdir()
    (tmp_path / "news" / "data.json").write_text(json.dumps([
        {"date": "2026-09-28", "structured": {"ko": {"issues": [{"title": "A"}, {"title": "B"}]}}},
        {"date": "2026-09-29", "structured": {"ko": {"issues": [{"title": "C"}]}}},
        {"date": "2026-09-30", "structured": {"ko": {"issues": []}}},  # 분석 실패일
    ]), encoding="utf-8")
    (tmp_path / "ai-issue").mkdir()
    (tmp_path / "ai-issue" / "2026-09-27.json").write_text(
        json.dumps({"top10": [{"title": "T1"}, {"title": "T2"}]}), encoding="utf-8")
    (tmp_path / "ai-issue" / "data.json").write_text("[]", encoding="utf-8")  # 날짜 파일 아님
    (tmp_path / "stock").mkdir()
    (tmp_path / "stock" / "data.json").write_text(json.dumps([
        {"date": "2026-09-28", "summary": "요약", "keywords": [{"title": "K"}, "bad"],
         "temperature": {"display": "🟠 상승"}},
    ]), encoding="utf-8")
    return tmp_path


# ── sns_source ────────────────────────────────────────────────────────────────
def test_latest_date_skips_days_without_issues(publish: Path) -> None:
    # Act
    latest = sns_source.latest_date("news", publish)
    # Assert — 이슈 없는 09-30 은 캡션 데이터가 없으므로 제외
    assert latest == "2026-09-29"


def test_ai_issue_ignores_non_date_json(publish: Path) -> None:
    assert sns_source.load_all("ai-issue", publish) == {"2026-09-27": {"issue_titles": ["T1", "T2"]}}


def test_stock_fields_drop_non_dict_keywords(publish: Path) -> None:
    fields = sns_source.caption_fields("stock", "2026-09-28", publish)
    assert fields["keywords"] == [{"title": "K", "body": ""}]
    assert fields["temperature"]["display"] == "🟠 상승"


def test_latest_date_raises_when_no_data(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        sns_source.latest_date("stock", tmp_path)


def test_unknown_channel_rejected(publish: Path) -> None:
    with pytest.raises(ValueError):
        sns_source.load_all("weekly", publish)


# ── classify_error ────────────────────────────────────────────────────────────
def test_classify_expired_meta_token() -> None:
    # Arrange — 2026-09-28 실제 Threads 실패 로그 형태
    exc = RuntimeError("Threads API 오류: {'message': 'Error validating access token: "
                       "Session has expired on Monday', 'type': 'OAuthException', 'code': 190}")
    # Act / Assert
    assert classify_error(exc).startswith("토큰 만료")


def test_classify_missing_env() -> None:
    exc = EnvironmentError("환경변수 THREADS_ACCESS_TOKEN 가 설정되지 않았습니다.")
    assert classify_error(exc) == "환경변수 누락 (THREADS_ACCESS_TOKEN)"


def test_classify_long_message_truncated() -> None:
    reason = classify_error(RuntimeError("x" * 500))
    assert len(reason) < 160 and reason.endswith("…")


# ── SnsReport ─────────────────────────────────────────────────────────────────
def test_report_detail_and_github_output(tmp_path: Path) -> None:
    # Arrange
    report = SnsReport(channel="news", date_str="2026-09-29", mode="text")
    report.record_success("facebook")
    report.record_skip("instagram", "텍스트 단독 게시 미지원")
    report.record_failure("threads", RuntimeError("'code': 190"))
    out = tmp_path / "gh_output"
    # Act
    report.write_github_output(str(out))
    # Assert
    written = out.read_text(encoding="utf-8")
    assert "failed=threads\n" in written
    assert "❌ threads: 토큰 만료" in written
    assert "✅ 성공: facebook" in written
    assert "⏭ instagram" in written
    assert report.has_failure


def test_report_without_failure_is_clean() -> None:
    report = SnsReport(channel="stock", date_str="2026-09-28", mode="text")
    report.record_success("threads")
    assert not report.has_failure


# ── post_cardnews.run (네트워크 없이 핸들러 대체) ─────────────────────────────
def test_run_isolates_platform_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange — 실제 발송 API 를 호출하지 않도록 핸들러를 가짜로 교체
    calls: list[tuple[str, str]] = []

    def ok(channel: str, date_str: str, mode: str) -> None:
        calls.append(("ok", mode))

    def expired(channel: str, date_str: str, mode: str) -> None:
        raise RuntimeError("'code': 190")

    monkeypatch.setattr(post_cardnews, "PLATFORM_HANDLERS", {
        "threads": expired, "facebook": ok,
        "instagram": post_cardnews.post_instagram,  # text 모드 → 네트워크 전에 skip
    })
    # Act
    report = post_cardnews.run("news", "2026-09-29", "text",
                               ["threads", "facebook", "instagram"])
    # Assert — threads 실패가 facebook 발송을 막지 않고, instagram 은 실패가 아닌 skip
    assert report.failed.keys() == {"threads"}
    assert report.succeeded == ["facebook"]
    assert "instagram" in report.skipped
    assert calls == [("ok", "text")]


def test_instagram_text_mode_skips_before_env_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)
    with pytest.raises(PlatformSkipped):
        post_cardnews.post_instagram("news", "2026-09-29", mode="text")


def test_default_platforms_per_mode() -> None:
    # text 모드: instagram(불가)·telegram(send_telegram.py 와 중복) 제외
    assert post_cardnews._default_platforms("text") == ["threads", "facebook"]
    assert "instagram" in post_cardnews._default_platforms("image")


# ── notify_pipeline ───────────────────────────────────────────────────────────
def test_failure_message_includes_escaped_detail() -> None:
    msg = notify_pipeline._msg_failure("cardnews", "2026-09-29",
                                       "❌ threads: THREADS_ACCESS_TOKEN [x]")
    assert "THREADS\\_ACCESS\\_TOKEN \\[x]" in msg
    assert "GitHub Actions 워크플로우에서 오류" not in msg


def test_failure_message_without_detail_keeps_default() -> None:
    msg = notify_pipeline._msg_failure("news", "2026-09-29")
    assert "GitHub Actions 워크플로우에서 오류가 발생했습니다." in msg
