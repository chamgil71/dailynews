"""Instagram 카루셀 발송 (graph.instagram.com v22.0).

graph.facebook.com/v21.0 에서 graph.instagram.com/v22.0 으로 이전
(Meta 2025~2026 Instagram Content Publishing API 마이그레이션).
Content Publishing API 는 이미지/동영상 없는 게시물을 지원하지 않으므로 text 모드는 건너뜀.
"""
from __future__ import annotations

import time

import requests

from core.shared.sns_report import PlatformSkipped
from scripts.sns.caption import build_caption
from scripts.sns.common import assert_urls_accessible, env, image_urls

GRAPH_IG = "https://graph.instagram.com/v22.0"


def _ig_post(path: str, params: dict) -> dict:
    # params를 URL 쿼리스트링이 아닌 요청 본문(form data)으로 전송
    r = requests.post(f"{GRAPH_IG}{path}", data=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Instagram Graph API 오류: {data['error']}")
    return data


def _ig_get(path: str, params: dict) -> dict:
    r = requests.get(f"{GRAPH_IG}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _ig_wait_container(container_id: str, token: str, max_wait: int = 60) -> None:
    for _ in range(max_wait // 5):
        data = _ig_get(f"/{container_id}", {"fields": "status_code", "access_token": token})
        status = data.get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Instagram 컨테이너 처리 오류: {data}")
        time.sleep(5)
    raise TimeoutError(f"Instagram 컨테이너 {container_id} 처리 시간 초과")


def _post_with_retry(path: str, params: dict, attempts: int, wait: int, what: str) -> dict:
    """2207027(미디어 준비 타이밍) 오류만 재시도."""
    for attempt in range(1, attempts + 1):
        try:
            return _ig_post(path, params)
        except RuntimeError as e:
            if attempt < attempts and "2207027" in str(e):
                print(f"  [Instagram] {what} 재시도 ({attempt}/{attempts}) — {wait}초 대기")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Instagram {what} 실패")  # 도달 불가 (루프가 반환 또는 raise)


def post_instagram(channel: str, date_str: str, mode: str = "image") -> None:
    """카드 PNG 카루셀 게시. text 모드는 PlatformSkipped."""
    if mode == "text":
        raise PlatformSkipped("텍스트 단독 게시 미지원 (이미지 필수)")
    token      = env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id = env("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    urls = image_urls(channel, date_str)
    assert_urls_accessible(urls, "Instagram")

    # 1. 카루셀 항목 컨테이너 생성
    children: list[str] = []
    for i, url in enumerate(urls):
        print(f"  [Instagram] 미디어 컨테이너 생성 [{i+1}/{len(urls)}]")
        cid = _ig_post(f"/{ig_user_id}/media", {
            "image_url": url, "is_carousel_item": "true", "access_token": token,
        }).get("id", "")
        if not cid:
            raise RuntimeError("Instagram 컨테이너 ID 없음")
        children.append(cid)
        time.sleep(1)

    # 2. 컨테이너 FINISHED 대기 + 내부 처리 여유(2207027 방지, 5장 기준 30초)
    for cid in children:
        _ig_wait_container(cid, token)
    time.sleep(30)

    # 3. 카루셀 컨테이너 생성 (2207027 시 최대 5회, 30초 간격)
    carousel_id = _post_with_retry(f"/{ig_user_id}/media", {
        "media_type":   "CAROUSEL",
        "children":     ",".join(children),
        "caption":      build_caption(channel, date_str, include_link=True),
        "access_token": token,
    }, attempts=5, wait=30, what="카루셀 생성").get("id", "")
    if not carousel_id:
        raise RuntimeError("Instagram 카루셀 컨테이너 생성 실패")

    # 4. 카루셀도 FINISHED 대기 후 게시 (2207027은 게시 단계에서도 발생 — 최대 3회, 10초)
    _ig_wait_container(carousel_id, token)
    time.sleep(5)
    result = _post_with_retry(f"/{ig_user_id}/media_publish", {
        "creation_id": carousel_id, "access_token": token,
    }, attempts=3, wait=10, what="게시")
    print(f"  ✅ Instagram 게시 완료 — media_id: {result.get('id')}")
