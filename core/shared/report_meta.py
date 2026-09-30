# core/shared/report_meta.py
"""
리포트 MD 머리말(제목 아래 ~ 첫 `## ` 섹션 전) 메타데이터 파서 — 3채널 공통 단일 진입점.

머리말 형식은 채널·생성 주체(Python 파이프라인 / Claude 루틴)마다 다르다:
  뉴스      > 📅 생성일시: YYYY-MM-DD HH:MM KST
            > 📊 수집: 총 N건 (EN: n / KO: n) | AI 분석: n건 | …
  AI이슈    생성일시: YYYY-MM-DD HH:MM KST | 기준: …
  주식 일일 > 데이터 기준: YYYY-MM-DD HH:MM KST | 생성: YYYY-MM-DD HH:MM KST
            (초기 14개는 > 📅 생성일시: …, 괄호 부연이 붙은 변형 있음)
  주식 주간 > 기간: YYYY-MM-DD(월) ~ YYYY-MM-DD(금) | 생성: YYYY-MM-DD HH:MM KST

형식은 바꾸지 않고(루틴·과거 파일·옵시디언 노트 영향 없음) 읽는 쪽만 여기로 모은다.
검색 범위를 머리말로 한정해 본문의 '기간:' 등 같은 글자에 잘못 매칭되지 않게 한다.
과거 리포트 전체 회귀 테스트: tests/test_report_meta.py
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_MAX_HEADER_LINES = 15
_DATETIME = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})"
_GENERATED_RE = re.compile(r"생성(?:일시)?\s*:\s*" + _DATETIME)
_DATA_AS_OF_RE = re.compile(r"데이터 기준\s*:\s*" + _DATETIME)
_PERIOD_RE = re.compile(r"기간\s*:\s*([^|\n]+)")
_STATS_PATTERNS = {
    "total":      re.compile(r"총 (\d+)건"),
    "en":         re.compile(r"EN:\s*(\d+)"),
    "ko":         re.compile(r"KO:\s*(\d+)"),
    "sent_to_ai": re.compile(r"AI 분석:\s*(\d+)건"),
}


@dataclass(frozen=True)
class ReportMeta:
    """머리말에서 읽은 값. 없으면 빈 문자열 / 0."""

    generated_at: str = ""   # 리포트 실제 생성 시각 'YYYY-MM-DD HH:MM'
    data_as_of: str = ""     # 주식 일일 데이터 기준 시각
    period: str = ""         # 주간 기간 'YYYY-MM-DD(월) ~ YYYY-MM-DD(금)'
    stats: dict[str, int] = field(default_factory=dict)  # 뉴스 수집 통계


def header_block(md_text: str) -> str:
    """제목 다음 줄부터 첫 `## ` 섹션 직전까지 (최대 15줄)."""
    lines: list[str] = []
    for line in md_text.splitlines()[:_MAX_HEADER_LINES]:
        if line.startswith("## "):
            break
        lines.append(line)
    return "\n".join(lines)


def _first(pattern: re.Pattern[str], text: str) -> str:
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def _parse_stats(head: str) -> dict[str, int]:
    """'총 N건'이 있는 머리말 줄에서 수집 통계 추출 (뉴스 전용)."""
    line = next((ln for ln in head.splitlines() if _STATS_PATTERNS["total"].search(ln)), "")
    if not line:
        return {}
    return {k: int(m.group(1)) if (m := p.search(line)) else 0
            for k, p in _STATS_PATTERNS.items()}


def parse_report_meta(md_text: str) -> ReportMeta:
    """리포트 MD 머리말 메타데이터."""
    head = header_block(md_text)
    return ReportMeta(
        generated_at=_first(_GENERATED_RE, head),
        data_as_of=_first(_DATA_AS_OF_RE, head),
        period=_first(_PERIOD_RE, head),
        stats=_parse_stats(head),
    )


def report_generated_at(md_text: str, fallback: str) -> str:
    """리포트가 실제로 생성된 시각(YYYY-MM-DD HH:MM). 머리말에 없으면 fallback.

    정적 페이지 하단 '생성 … KST' 표기에 빌드 시각(datetime.now) 대신 사용한다.
    빌드 시각을 쓰면 전체 재생성하는 주식·AI이슈 페이지가 내용이 같아도 매 빌드마다
    바뀌어 수십~백여 개 파일이 불필요하게 커밋되고, 표기도 실제 생성 시각이 아니게 된다.
    """
    return parse_report_meta(md_text).generated_at or fallback
