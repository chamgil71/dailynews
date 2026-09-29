"""
SNS 캡션용 원본 데이터 로더 (3채널 공통).

카드뉴스 빌드 산출물(publish/cardnews/{channel}/data.json)이 아니라
각 채널의 원본 발행 데이터(publish/news|ai-issue|stock)에서 직접 읽는다.
→ 카드 이미지 빌드를 중단(텍스트 모드)해도 SNS 캡션이 최신 데이터로 유지된다.

build_cardnews.py(카드 data.json의 extra 필드)와 post_cardnews.py(캡션)가
이 모듈을 공유한다.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

PUBLISH_DIR = Path(__file__).resolve().parent.parent.parent / "publish"
_DATE_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHANNELS = ("news", "ai-issue", "stock")


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


# ── 채널별 필드 추출 (단일 엔트리 → 캡션 필드) ──────────────────────────────────
def news_fields(entry: dict) -> dict:
    """뉴스 data.json 엔트리 → {"issue_titles": [...]} (상위 3개)."""
    ko = entry.get("structured", {}).get("ko", {})
    titles = [i.get("title", "") for i in ko.get("issues", [])[:3] if i.get("title")]
    return {"issue_titles": titles} if titles else {}


def ai_issue_fields(data: dict) -> dict:
    """AI이슈 날짜별 JSON → {"issue_titles": [...]} (TOP10 중 상위 3개)."""
    titles = [t.get("title", "") for t in data.get("top10", [])[:3] if t.get("title")]
    return {"issue_titles": titles} if titles else {}


def stock_fields(entry: dict) -> dict:
    """주식 data.json 엔트리 → summary/keywords(최대 5)/temperature."""
    kws = [{"title": k.get("title", ""), "body": k.get("body", "")}
           for k in entry.get("keywords", []) if isinstance(k, dict)]
    return {
        "summary":     entry.get("summary", ""),
        "keywords":    kws[:5],
        "temperature": entry.get("temperature", {}),
    }


# ── 채널 전체 로드 ({date: fields}) ─────────────────────────────────────────────
def _load_news(publish: Path) -> dict[str, dict]:
    path = publish / "news" / "data.json"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    for e in _read_json(path):
        d, fields = e.get("date", ""), news_fields(e)
        if d and fields:
            out[d] = fields
    return out


def _load_ai_issue(publish: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for fp in (publish / "ai-issue").glob("*.json"):
        if not _DATE_FILE.match(fp.stem):
            continue
        try:
            fields = ai_issue_fields(_read_json(fp))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("AI이슈 JSON 읽기 실패 %s: %s", fp.name, e)
            continue
        if fields:
            out[fp.stem] = fields
    return out


def _load_stock(publish: Path) -> dict[str, dict]:
    path = publish / "stock" / "data.json"
    if not path.exists():
        return {}
    return {e["date"]: stock_fields(e) for e in _read_json(path) if e.get("date")}


_LOADERS = {"news": _load_news, "ai-issue": _load_ai_issue, "stock": _load_stock}


def load_all(channel: str, publish: Path = PUBLISH_DIR) -> dict[str, dict]:
    """채널의 전체 날짜별 캡션 필드 {date: fields}. 알 수 없는 채널은 ValueError."""
    if channel not in _LOADERS:
        raise ValueError(f"알 수 없는 채널: {channel}")
    return _LOADERS[channel](publish)


def latest_date(channel: str, publish: Path = PUBLISH_DIR) -> str:
    """캡션 데이터가 있는 가장 최근 날짜. 없으면 FileNotFoundError."""
    dates = load_all(channel, publish)
    if not dates:
        raise FileNotFoundError(f"{channel} 원본 발행 데이터 없음 ({publish})")
    return max(dates)


def caption_fields(channel: str, date_str: str, publish: Path = PUBLISH_DIR) -> dict:
    """특정 날짜의 캡션 필드. 데이터가 없으면 빈 dict(날짜·링크만 있는 캡션이 됨)."""
    fields = load_all(channel, publish).get(date_str, {})
    if not fields:
        logger.warning("%s %s 캡션 데이터 없음 — 기본 캡션 사용", channel, date_str)
    return fields
