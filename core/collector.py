# core/collector.py
"""
뉴스 수집 모듈
- 카테고리별 RSS 수집 (한국어 / 영어 분리)
- URL 기준 중복 제거 (세션 내 + 전일 캐시)
- 피드별 장애 격리 — 한 피드 실패해도 나머지 계속
- RSS_TIMEOUT_SECONDS 타임아웃 적용
"""

import json
import logging
import os
import socket
import time
from datetime import datetime, timedelta

import feedparser

from config.rss_sources import RSS_FEEDS
from config.settings import (
    CACHE_ENABLED, CACHE_FILE, CACHE_TTL_HOURS,
    MAX_ENTRIES_PER_FEED, MAX_TITLES_TO_ANALYZE,
    RSS_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


# ── 캐시 ──────────────────────────────────────────────────────────────────────

def _load_cache() -> set:
    """전일 URL 캐시 로드 (TTL 초과 항목 자동 제거)"""
    if not CACHE_ENABLED or not os.path.exists(CACHE_FILE):
        return set()
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cutoff = datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)
        return {url for url, ts in data.items()
                if datetime.fromisoformat(ts) > cutoff}
    except Exception as e:
        logger.warning(f"[캐시 로드 실패] {e}")
        return set()


def _save_cache(new_urls: set):
    """신규 URL을 캐시에 추가 저장"""
    if not CACHE_ENABLED:
        return
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        existing = {}
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        now = datetime.utcnow().isoformat()
        existing.update({url: now for url in new_urls})
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"[캐시 저장 실패] {e}")


# ── 단일 피드 수집 ────────────────────────────────────────────────────────────

def _fetch_feed(url: str, category: str, lang: str, label: str,
                seen_urls: set) -> list:
    """단일 RSS 피드 파싱. 실패 시 빈 리스트 반환 (장애 격리)."""
    results = []
    old_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(RSS_TIMEOUT_SECONDS)
        feed = feedparser.parse(url)
        socket.setdefaulttimeout(old_timeout)

        if feed.bozo and not feed.entries:
            logger.warning(f"[RSS 오류] {url} — {feed.bozo_exception}")
            return results

        count = 0
        for entry in feed.entries:
            if count >= MAX_ENTRIES_PER_FEED:
                break
            link  = getattr(entry, "link",  "").strip()
            title = getattr(entry, "title", "").strip()
            if not link or not title or link in seen_urls:
                continue
            seen_urls.add(link)
            results.append({
                "category":  category,
                "label":     label,
                "lang":      lang,
                "title":     title,
                "link":      link,
                "published": getattr(entry, "published", ""),
            })
            count += 1

        logger.info(f"[수집] {label} | {count}건 ← {url}")

    except Exception as e:
        socket.setdefaulttimeout(old_timeout)
        logger.error(f"[피드 실패] {url}: {e}")

    return results


# ── 전체 수집 ─────────────────────────────────────────────────────────────────

def collect_news() -> dict:
    """
    반환:
        {
          "en":    [기사...],   # 영어 전체
          "ko":    [기사...],   # 한국어 전체
          "all":   [기사...],   # 전체
          "trim":  [기사...],   # AI 분석용 (토큰 제한 적용)
          "stats": {...}
        }
    """
    cached_urls = _load_cache()
    seen_urls   = set(cached_urls)
    all_news: list = []

    for category, meta in RSS_FEEDS.items():
        lang, label = meta["lang"], meta["label"]
        for url in meta["feeds"]:
            items = _fetch_feed(url, category, lang, label, seen_urls)
            all_news.extend(items)
            time.sleep(0.3)   # 서버 부하 방지

    en_news = [n for n in all_news if n["lang"] == "en"]
    ko_news = [n for n in all_news if n["lang"] == "ko"]

    # 토큰 예산: 영어 60% + 한국어 40%
    en_cap  = min(len(en_news), int(MAX_TITLES_TO_ANALYZE * 0.6))
    ko_cap  = min(len(ko_news), MAX_TITLES_TO_ANALYZE - en_cap)
    trimmed = en_news[:en_cap] + ko_news[:ko_cap]

    stats = {
        "total":        len(all_news),
        "en":           len(en_news),
        "ko":           len(ko_news),
        "sent_to_ai":   len(trimmed),
        "skipped_dup":  len(cached_urls),
    }
    logger.info(f"[수집 완료] 총 {stats['total']}건 "
                f"(EN:{stats['en']} KO:{stats['ko']}) → AI {stats['sent_to_ai']}건")

    _save_cache({n["link"] for n in all_news} - cached_urls)

    return {"en": en_news, "ko": ko_news, "all": all_news,
            "trim": trimmed, "stats": stats}
