"""Threads 발송 (graph.threads.net v1.0) — 텍스트 단독 / 이미지 카루셀.

Instagram 과 달리 Threads 는 텍스트 단독 포스트를 지원하므로 기본값은 "text".
채널별 모드는 config/cardnews_themes.json channels[].threads_mode 에서 제어:
  "text"     → 이미지 없이 텍스트만 게시 (기본)
  "carousel" → 카드뉴스 PNG를 카루셀로 게시
전체 발송 모드(--mode)가 text 이면 채널 설정과 무관하게 텍스트로 게시.
"""
from __future__ import annotations

import time

import requests

from scripts.sns.caption import build_caption
from scripts.sns.common import assert_urls_accessible, env, image_urls, load_themes_config

THREADS_API = "https://graph.threads.net/v1.0"
THREADS_TEXT_LIMIT = 500


def _get_threads_mode(channel: str) -> str:
    """채널별 Threads 발송 모드 반환. config에 없거나 읽기 실패 시 'text'."""
    try:
        return load_themes_config().get("channels", {}).get(channel, {}).get("threads_mode", "text")
    except (OSError, ValueError):
        return "text"


def _threads_post(path: str, params: dict) -> dict:
    r = requests.post(f"{THREADS_API}{path}", params=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Threads API 오류: {data['error']}")
    return data


def _threads_get(path: str, params: dict) -> dict:
    r = requests.get(f"{THREADS_API}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _threads_publish(user_id: str, token: str, creation_id: str) -> dict:
    """컨테이너 FINISHED 상태 확인 후 게시."""
    for _ in range(12):
        status = _threads_get(f"/{creation_id}", {"fields": "status", "access_token": token})
        if status.get("status") == "FINISHED":
            break
        time.sleep(5)
    return _threads_post(f"/{user_id}/threads_publish", {
        "creation_id": creation_id, "access_token": token,
    })


def _is_transient(err: str) -> bool:
    return "is_transient" in err or "code': 2" in err or "unexpected error" in err.lower()


def _post_threads_text(user_id: str, token: str, caption: str) -> str:
    """텍스트 단독 포스트 생성 후 게시 → post id. 일시적 오류만 최대 3회(10s, 20s 대기)."""
    for attempt in range(1, 4):
        try:
            container = _threads_post(f"/{user_id}/threads", {
                "media_type": "TEXT", "text": caption, "access_token": token,
            })
            return _threads_publish(user_id, token, container["id"]).get("id", "")
        except RuntimeError as e:
            if attempt < 3 and _is_transient(str(e)):
                wait = attempt * 10
                print(f"  [Threads] 일시적 오류 재시도 ({attempt}/3) — {wait}초 대기: {e}")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Threads 텍스트 게시 실패")  # 도달 불가 (루프가 반환 또는 raise)


def _post_threads_carousel(user_id: str, token: str, caption: str, urls: list[str]) -> str:
    """이미지 카루셀 포스트 생성 후 게시 → post id."""
    children = []
    for i, url in enumerate(urls):
        print(f"  [Threads] 아이템 컨테이너 생성 [{i+1}/{len(urls)}]")
        data = _threads_post(f"/{user_id}/threads", {
            "image_url": url, "media_type": "IMAGE",
            "is_carousel_item": "true", "access_token": token,
        })
        children.append(data["id"])
        time.sleep(1)

    print("  [Threads] 카루셀 컨테이너 생성 중...")
    carousel = _threads_post(f"/{user_id}/threads", {
        "media_type": "CAROUSEL", "children": ",".join(children),
        "text": caption, "access_token": token,
    })
    return _threads_publish(user_id, token, carousel["id"]).get("id", "")


def truncate_caption(caption: str, limit: int) -> str:
    """limit 초과 시 말줄임표로 축약 (Threads TEXT 500자 제한)."""
    if len(caption) <= limit:
        return caption
    return caption[:limit - 1].rstrip() + "…"


def post_threads(channel: str, date_str: str, mode: str = "image") -> None:
    """Threads 게시 — 모드는 모듈 docstring 참고."""
    token   = env("THREADS_ACCESS_TOKEN")
    user_id = env("THREADS_USER_ID")
    caption = truncate_caption(build_caption(channel, date_str, include_link=True),
                               THREADS_TEXT_LIMIT)

    threads_mode = "text" if mode == "text" else _get_threads_mode(channel)
    print(f"  [Threads] mode={threads_mode}")

    if threads_mode == "carousel":
        urls = image_urls(channel, date_str)
        assert_urls_accessible(urls, "Threads")
        post_id = _post_threads_carousel(user_id, token, caption, urls)
    else:
        post_id = _post_threads_text(user_id, token, caption)
    print(f"  ✅ Threads 발송 완료 — id: {post_id}")
