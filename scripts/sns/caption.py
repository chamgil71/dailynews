"""SNS 캡션 생성 — 원본 발행 데이터(core/shared/sns_source.py) 기반, text/image 공통."""
from __future__ import annotations

from datetime import datetime

from core.shared import sns_source
from core.shared.report_date import weekly_label
from scripts.sns.common import channel_label, channel_site_url

_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
_HASHTAGS = "#AI뉴스 #테크뉴스 #데일리뉴스 #인공지능 #AINews #TechNews"


def _display_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return date_str
    return f"{dt.year}년 {dt.month}월 {dt.day}일 ({_WEEKDAYS[dt.weekday()]})"


def _stock_lines(entry: dict, date_str: str, display: str, label: str) -> list[str]:
    is_weekly = bool(entry.get("is_weekly"))
    header = (f"📅 {weekly_label(date_str)} 주식 시황 종합" if is_weekly
              else f"📈 {display} {label} 브리핑")
    lines = [f"{header}\n"]
    temp_disp = (entry.get("temperature") or {}).get("display", "")
    if temp_disp:
        lines.append(f"🌡 {'주간 온도계' if is_weekly else '시장온도'}: {temp_disp}")
        lines.append("")
    summary = entry.get("summary", "")
    if summary:
        summary_lines = [l.strip().lstrip("- ").strip()
                         for l in summary.splitlines() if l.strip()][:2]
        if summary_lines:
            lines.append("📌 " + "\n".join(summary_lines))
            lines.append("")
    kw_titles = [kw.get("title", "") if isinstance(kw, dict) else str(kw)
                 for kw in entry.get("keywords", [])[:3]]
    kw_titles = [t for t in kw_titles if t]
    if kw_titles:
        lines.append(("🔥 핫 테마: " if is_weekly else "🔑 ") + " | ".join(kw_titles))
    return lines


def build_caption(channel: str, date_str: str, include_link: bool = True) -> str:
    """채널·날짜의 SNS 게시 캡션 (주식: 온도·요약·키워드 / 그 외: 이슈 제목 3개)."""
    entry   = sns_source.caption_fields(channel, date_str)
    display = _display_date(date_str)
    label   = channel_label(channel)

    if channel == "stock":
        lines = _stock_lines(entry, date_str, display, label)
    else:
        icons = ["🔥", "📢", "💡"]
        lines = [f"📰 {display} {label} 브리핑\n"]
        for i, title in enumerate(entry.get("issue_titles", [])[:3]):
            lines.append(f"{icons[i]} {title}")

    if include_link:
        lines.append(f"\n🔗 {channel_site_url(channel)}")
    lines.append(f"\n{_HASHTAGS}")
    return "\n".join(lines)
