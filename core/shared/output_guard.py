"""
LLM 출력 가드 (Output Guard) — orchestration.md §1 Phase 2 '가드 파트' 이행 모듈.

news/ai_issue analyzer 가 반환하는 구조화 결과(dict)를 검증한다.
1. 구조 검증(format_compliance): issues[]/trends[] 필수 키·타입 확인
2. 그라운딩 검증(anti-hallucination): 출력 source URL 이 입력 뉴스 링크 집합에 존재하는지
3. 개수 제약: issues 3~5건 범위
4. 살균(sanitize): 환각 source 제거본 반환

외부 의존성 없음(표준 라이브러리만). analyzer 실 호출과 무관하게 오프라인 검증 가능.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── 정책 상수 ────────────────────────────────────────────────────────────────
MIN_ISSUES = 3
MAX_ISSUES = 5


@dataclass
class GuardReport:
    """가드 검증 결과."""
    valid: bool                              # 전체 통과 여부 (구조+개수+그라운딩)
    format_ok: bool                          # 구조/타입 적합
    count_ok: bool                           # issues 개수 범위 적합
    grounded: bool                           # 환각 source 없음
    issues_count: int
    trends_count: int
    total_sources: int
    hallucinated_sources: list[str] = field(default_factory=list)  # 입력에 없는 URL
    errors: list[str] = field(default_factory=list)
    sanitized: dict[str, Any] | None = None  # 환각 source 제거본

    @property
    def hallucination_rate(self) -> float:
        """전체 source 대비 환각 source 비율 (0.0~1.0)."""
        if self.total_sources == 0:
            return 0.0
        return round(len(self.hallucinated_sources) / self.total_sources, 4)


def _collect_input_urls(input_news: dict | list) -> set[str]:
    """입력 뉴스에서 유효 링크(URL) 집합을 수집. dict{en,ko} 또는 list 모두 지원."""
    items: list[dict] = []
    if isinstance(input_news, dict):
        for key in ("en", "ko", "combined"):
            v = input_news.get(key)
            if isinstance(v, list):
                items.extend(v)
    elif isinstance(input_news, list):
        items = input_news
    urls: set[str] = set()
    for n in items:
        if not isinstance(n, dict):
            continue
        for k in ("link", "url"):
            u = n.get(k)
            if isinstance(u, str) and u.strip():
                urls.add(u.strip())
    return urls


def validate_structure(result: dict) -> tuple[bool, list[str]]:
    """issues[]/trends[] 구조·타입 검증. (ok, errors) 반환."""
    errors: list[str] = []
    if not isinstance(result, dict):
        return False, ["result 가 dict 가 아님"]

    issues = result.get("issues")
    if not isinstance(issues, list):
        errors.append("issues 키 누락 또는 list 아님")
        issues = []
    for i, it in enumerate(issues):
        if not isinstance(it, dict):
            errors.append(f"issues[{i}] dict 아님")
            continue
        if not str(it.get("title", "")).strip():
            errors.append(f"issues[{i}].title 비어있음")
        if "sources" in it and not isinstance(it["sources"], list):
            errors.append(f"issues[{i}].sources list 아님")

    trends = result.get("trends")
    if trends is not None and not isinstance(trends, list):
        errors.append("trends 가 list 아님")

    return (len(errors) == 0), errors


def guard(result: dict, input_news: dict | list, *, strict: bool = False) -> GuardReport:
    """
    analyzer 출력을 검증하고 GuardReport 반환.

    strict=True 이면 개수·그라운딩 위반도 valid=False 로 처리(릴리즈 게이트용).
    strict=False 이면 구조만 필수, 개수/그라운딩은 경고 수준(운영 관용).
    """
    format_ok, errors = validate_structure(result)
    issues = result.get("issues", []) if isinstance(result, dict) else []
    trends = result.get("trends", []) if isinstance(result, dict) else []
    issues = issues if isinstance(issues, list) else []
    trends = trends if isinstance(trends, list) else []

    # 개수 제약
    count_ok = MIN_ISSUES <= len(issues) <= MAX_ISSUES
    if not count_ok:
        errors.append(f"issues 개수 {len(issues)} 가 허용 범위({MIN_ISSUES}~{MAX_ISSUES}) 밖")

    # 그라운딩(환각 source) 검증
    input_urls = _collect_input_urls(input_news)
    hallucinated: list[str] = []
    total_sources = 0
    sanitized_issues: list[dict] = []
    for it in issues:
        if not isinstance(it, dict):
            continue
        srcs = it.get("sources", []) or []
        kept = []
        for s in srcs:
            url = s.get("url", "").strip() if isinstance(s, dict) else ""
            if not url:
                continue
            total_sources += 1
            # 입력 URL 집합이 비어있으면 그라운딩 검증 스킵(입력 정보 없음)
            if input_urls and url not in input_urls:
                hallucinated.append(url)
            else:
                kept.append(s)
        san = dict(it)
        if input_urls:
            san["sources"] = kept
        sanitized_issues.append(san)

    grounded = len(hallucinated) == 0
    sanitized = {**result, "issues": sanitized_issues} if isinstance(result, dict) else None

    valid = format_ok and (count_ok and grounded if strict else True)

    return GuardReport(
        valid=valid,
        format_ok=format_ok,
        count_ok=count_ok,
        grounded=grounded,
        issues_count=len(issues),
        trends_count=len(trends),
        total_sources=total_sources,
        hallucinated_sources=hallucinated,
        errors=errors,
        sanitized=sanitized,
    )


def fallback_result(reason: str = "가드 검증 실패") -> dict:
    """구조 복구 불가 시 안전 폴백 구조. 파이프라인 중단 대신 빈 구조 반환."""
    return {"issues": [], "trends": [], "_guard_fallback": True, "_reason": reason}
