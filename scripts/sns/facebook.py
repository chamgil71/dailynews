"""Facebook Page 발송 (graph.facebook.com v21.0) — 멀티 사진 / 텍스트+링크."""
from __future__ import annotations

import json
import time

import requests

from scripts.sns.caption import build_caption
from scripts.sns.common import assert_urls_accessible, channel_site_url, env, image_urls

GRAPH_API = "https://graph.facebook.com/v21.0"


def _fb_post(path: str, params: dict, what: str) -> dict:
    r = requests.post(f"{GRAPH_API}{path}", params=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Facebook {what} 오류: {data['error']}")
    return data


def post_facebook(channel: str, date_str: str, mode: str = "image") -> None:
    """image: 카드 PNG 비공개 업로드 후 멀티 사진 포스트 / text: 캡션 + 링크 미리보기."""
    token   = env("META_PAGE_ACCESS_TOKEN")
    page_id = env("FACEBOOK_PAGE_ID")
    caption = build_caption(channel, date_str, include_link=True)

    if mode == "text":
        data = _fb_post(f"/{page_id}/feed", {
            "message": caption, "link": channel_site_url(channel), "access_token": token,
        }, "포스트")
        print(f"  ✅ Facebook 텍스트 발송 완료 — post_id: {data.get('id', '')}")
        return

    urls = image_urls(channel, date_str)
    assert_urls_accessible(urls, "Facebook")

    # 1. 각 이미지 비공개 업로드 → photo_id 수집
    photo_ids = []
    for i, url in enumerate(urls):
        print(f"  [Facebook] 이미지 업로드 [{i+1}/{len(urls)}]")
        data = _fb_post(f"/{page_id}/photos", {
            "url": url, "published": "false", "access_token": token,
        }, "이미지 업로드")
        photo_ids.append({"media_fbid": data["id"]})
        time.sleep(1)

    # 2. 멀티 사진 포스트 게시
    print("  [Facebook] 멀티 사진 포스트 게시 중...")
    data = _fb_post(f"/{page_id}/feed", {
        "message": caption, "attached_media": json.dumps(photo_ids), "access_token": token,
    }, "포스트")
    print(f"  ✅ Facebook 발송 완료 — post_id: {data.get('id')}")
