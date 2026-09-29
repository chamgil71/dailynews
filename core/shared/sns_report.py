"""
SNS 플랫폼별 발송 결과 집계 및 GitHub Actions 출력.

post_cardnews.py 가 플랫폼별 결과를 여기에 기록하면,
- 실패 사유를 사람이 읽을 수 있는 짧은 문구로 분류하고 (토큰 만료 / 환경변수 누락 등)
- $GITHUB_OUTPUT 에 failed / detail 을 남겨
  cardnews.yml 의 알림 스텝(notify_pipeline.py --detail)이 플랫폼별 실패를 텔레그램으로 보낸다.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_MAX_REASON = 120
_CHANNEL_LABELS = {"news": "뉴스", "ai-issue": "AI이슈", "stock": "주식"}


class PlatformSkipped(Exception):
    """해당 모드에서 지원하지 않아 건너뛴 플랫폼 (실패로 집계하지 않음)."""


def classify_error(exc: BaseException) -> str:
    """예외 → 짧은 한글 사유. Meta OAuth code 190 은 토큰 만료로 분류."""
    msg = str(exc)
    if isinstance(exc, EnvironmentError) and "환경변수" in msg:
        return f"환경변수 누락 ({msg.split('환경변수', 1)[1].split()[0]})"
    if re.search(r"'code':\s*190\b", msg) or "Session has expired" in msg:
        return "토큰 만료 (OAuth 190) — 토큰 재발급 필요"
    if "OAuthException" in msg:
        return "인증 오류 (OAuthException)"
    one_line = " ".join(msg.split())
    if len(one_line) > _MAX_REASON:
        one_line = one_line[:_MAX_REASON - 1] + "…"
    return f"{type(exc).__name__}: {one_line}"


@dataclass
class SnsReport:
    """한 번의 발송 실행(채널 1개)에 대한 플랫폼별 결과."""

    channel: str
    date_str: str
    mode: str
    succeeded: list[str] = field(default_factory=list)
    skipped: dict[str, str] = field(default_factory=dict)
    failed: dict[str, str] = field(default_factory=dict)

    def record_success(self, platform: str) -> None:
        self.succeeded.append(platform)

    def record_skip(self, platform: str, reason: str) -> None:
        self.skipped[platform] = reason

    def record_failure(self, platform: str, exc: BaseException) -> None:
        self.failed[platform] = classify_error(exc)

    @property
    def has_failure(self) -> bool:
        return bool(self.failed)

    def detail_text(self) -> str:
        """텔레그램 알림용 다중 행 요약 (실패 → 성공 → 건너뜀 순)."""
        label = _CHANNEL_LABELS.get(self.channel, self.channel)
        lines = [f"[{label}] {self.date_str} · {self.mode} 모드"]
        lines += [f"❌ {p}: {r}" for p, r in self.failed.items()]
        if self.succeeded:
            lines.append(f"✅ 성공: {', '.join(self.succeeded)}")
        lines += [f"⏭ {p}: {r}" for p, r in self.skipped.items()]
        return "\n".join(lines)

    def write_github_output(self, output_path: str | None = None) -> None:
        """$GITHUB_OUTPUT 에 failed(쉼표목록)·detail(다중행) 기록. 로컬 실행 시 생략."""
        path = output_path or os.environ.get("GITHUB_OUTPUT", "")
        if not path:
            return
        delim = "SNS_DETAIL_EOF"
        with Path(path).open("a", encoding="utf-8") as f:
            f.write(f"failed={','.join(self.failed)}\n")
            f.write(f"detail<<{delim}\n{self.detail_text()}\n{delim}\n")
        logger.info("GITHUB_OUTPUT 기록: failed=%s", ",".join(self.failed))
