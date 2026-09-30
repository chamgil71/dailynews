"""SNS 발송 공통 유틸 — 환경변수·카드 PNG 경로·사이트 URL·CDN 전파 확인."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
CARDNEWS_DIR = ROOT / "publish" / "cardnews"
THEMES_CONFIG_PATH = ROOT / "config" / "cardnews_themes.json"
GITHUB_RAW   = "https://raw.githubusercontent.com/chamgil71/dailynews/main"
SITE_BASE    = "https://ms-dailynews.vercel.app"
MAX_CAROUSEL = 5

_CHANNEL_SITE_PATH = {
    "news":     "",
    "ai-issue": "ai-issue/",
    "stock":    "stock/",
}


def env(key: str, required: bool = True) -> str:
    """환경변수 조회. required 인데 비어 있으면 EnvironmentError."""
    val = os.environ.get(key, "").strip()
    if not val and required:
        raise EnvironmentError(f"환경변수 {key} 가 설정되지 않았습니다.")
    return val


def channel_dir(channel: str) -> Path:
    """채널별 카드뉴스 산출물 폴더."""
    return CARDNEWS_DIR / channel


def png_paths(channel: str, date_str: str) -> list[Path]:
    """해당 날짜 카드 PNG 목록 (최대 MAX_CAROUSEL장). 없으면 FileNotFoundError."""
    paths = sorted(channel_dir(channel).glob(f"{date_str}-*.png"))
    if not paths:
        raise FileNotFoundError(
            f"PNG 없음: {channel_dir(channel)}/{date_str}-*.png"
        )
    return paths[:MAX_CAROUSEL]


def image_urls(channel: str, date_str: str) -> list[str]:
    """카드 PNG의 GitHub Raw 공개 URL 목록 (Meta API 는 URL 로 이미지를 받음)."""
    return [f"{GITHUB_RAW}/publish/cardnews/{channel}/{p.name}"
            for p in png_paths(channel, date_str)]


def channel_label(channel: str) -> str:
    """채널 한글 표기."""
    return {"news": "뉴스", "ai-issue": "AI이슈", "stock": "주식"}.get(channel, channel)


def channel_site_url(channel: str) -> str:
    """채널 웹페이지 URL."""
    return f"{SITE_BASE}/{_CHANNEL_SITE_PATH.get(channel, '')}"


def load_themes_config() -> dict:
    """config/cardnews_themes.json 로드."""
    return json.loads(THEMES_CONFIG_PATH.read_text(encoding="utf-8"))


def _verify_url(url: str, max_wait: int = 120) -> bool:
    """GitHub Raw CDN 전파 여부 확인. 접근 가능하면 True 반환."""
    interval = 10
    for attempt in range(1, max_wait // interval + 2):
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        if attempt * interval < max_wait:
            time.sleep(interval)
    return False


def assert_urls_accessible(urls: list[str], platform: str) -> None:
    """첫 번째 이미지 URL 접근 가능 여부 확인 (CDN 전파 보장)."""
    if not urls:
        return
    url = urls[0]
    if not _verify_url(url, max_wait=120):
        raise RuntimeError(
            f"{platform}: GitHub Raw CDN 미전파 — {url} 에 접근할 수 없습니다. "
            f"workflow에서 CDN 대기 스텝 없이 직접 실행 시 발생할 수 있습니다."
        )
