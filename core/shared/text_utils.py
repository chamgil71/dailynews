# core/shared/text_utils.py
"""LLM(Gemini)이 마크다운 대신 JSON 래퍼로 반환하는 응답을 텍스트로 환원하는 공통 유틸.

Gemini가 반환하는 JSON 래퍼의 리스트 키 이름(points/monitoring_points/...)과
항목 내 필드 이름(commentary/description/analyst_comment/...)이 매번 달라지므로,
특정 키 이름을 하드코딩하지 않고 구조(리스트-오브-딕셔너리)로 감지한다.
"""

_POINT_KEYS = ("point", "title", "name", "keyword")
_DETAIL_KEYS = ("commentary", "comment", "description", "analyst_comment", "detail")


def unwrap_md_wrapper(parsed) -> str | None:
    """{"summary":...} / {"report":...} / {"title":..., "<임의의 리스트 키>": [{...}]} 패턴을
    마크다운 텍스트로 변환한다. 변환 가능한 패턴이 아니면 None을 반환한다."""
    if not isinstance(parsed, dict):
        return None
    for key in ("summary", "report"):
        if key in parsed and isinstance(parsed[key], str):
            return parsed[key]
    list_key = next(
        (k for k, v in parsed.items() if isinstance(v, list) and v and isinstance(v[0], dict)),
        None,
    )
    if list_key is None:
        return None
    title = parsed.get("title", "")
    lines = [f"## {title}\n"] if title else []
    for item in parsed[list_key]:
        if not isinstance(item, dict):
            continue
        point = next((item[k] for k in _POINT_KEYS if item.get(k)), "")
        details = [item[k] for k in _DETAIL_KEYS if item.get(k)]
        if point:
            lines.append(f"- **{point}**")
            for d in details:
                lines.append(f"  {d}")
    return "\n".join(lines) if lines else None


def extract_wrapped_points(parsed, limit: int = 3) -> list[str]:
    """JSON 래퍼의 리스트 항목에서 point류 값만 최대 limit개 추출 (텔레그램 요약용)."""
    if not isinstance(parsed, dict):
        return []
    list_key = next(
        (k for k, v in parsed.items() if isinstance(v, list) and v and isinstance(v[0], dict)),
        None,
    )
    if list_key is None:
        return []
    points = []
    for item in parsed[list_key]:
        if isinstance(item, dict):
            point = next((item[k] for k in _POINT_KEYS if item.get(k)), "")
            if point:
                points.append(point)
    return points[:limit]
