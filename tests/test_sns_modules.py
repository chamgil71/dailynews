"""
scripts/sns/ 플랫폼 모듈 분리 후 공통화된 로직 검증 (네트워크 호출 없음)

실행: python -m pytest tests/test_sns_modules.py -v
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.sns import instagram, threads  # noqa: E402


def test_truncate_caption_keeps_limit() -> None:
    assert threads.truncate_caption("짧음", 500) == "짧음"
    out = threads.truncate_caption("가" * 600, 500)
    assert len(out) == 500 and out.endswith("…")


def test_instagram_retry_only_on_2207027(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange — 2번 타이밍 오류 후 성공
    calls: list[str] = []

    def fake_post(path: str, params: dict) -> dict:
        calls.append(path)
        if len(calls) < 3:
            raise RuntimeError("Instagram Graph API 오류: {'error_subcode': 2207027}")
        return {"id": "OK"}

    monkeypatch.setattr(instagram, "_ig_post", fake_post)
    monkeypatch.setattr(instagram.time, "sleep", lambda s: None)
    # Act
    result = instagram._post_with_retry("/x", {}, attempts=5, wait=30, what="테스트")
    # Assert
    assert result == {"id": "OK"} and len(calls) == 3


def test_instagram_other_errors_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_post(path: str, params: dict) -> dict:
        calls.append(path)
        raise RuntimeError("Instagram Graph API 오류: code 190")

    monkeypatch.setattr(instagram, "_ig_post", fake_post)
    with pytest.raises(RuntimeError, match="190"):
        instagram._post_with_retry("/x", {}, attempts=5, wait=30, what="테스트")
    assert len(calls) == 1


def test_threads_text_retries_transient_then_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_post(path: str, params: dict) -> dict:
        calls.append(path)
        raise RuntimeError("Threads API 오류: {'is_transient': True}")

    monkeypatch.setattr(threads, "_threads_post", fake_post)
    monkeypatch.setattr(threads.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError, match="is_transient"):
        threads._post_threads_text("u", "t", "캡션")
    assert len(calls) == 3
