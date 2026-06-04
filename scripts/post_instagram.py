"""
카드뉴스 PNG → Instagram 카루셀 포스팅 (Graph API v21.0)

필요한 GitHub Secrets:
  INSTAGRAM_ACCESS_TOKEN        - 장기 액세스 토큰 (60일, 자동 갱신 필요)
  INSTAGRAM_BUSINESS_ACCOUNT_ID - Instagram Business 계정 ID

필요 권한 (App Review):
  instagram_content_publish, instagram_manage_comments (선택)

사용법:
  python scripts/post_instagram.py --date 2026-06-04

이미지 URL 전략:
  PNG는 GitHub raw URL로 공개 접근 (push 후 즉시 사용 가능)
  https://raw.githubusercontent.com/{owner}/{repo}/main/publish/cardnews/{date}-{n}.png

Instagram API 흐름:
  1. 각 이미지마다 미디어 컨테이너 생성 (is_carousel_item=true)
  2. 카루셀 컨테이너 생성 (children=컨테이너ID 목록)
  3. 카루셀 게시
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

CARDNEWS_DIR = Path(_ROOT, "publish", "cardnews")
GRAPH_BASE   = "https://graph.facebook.com/v21.0"
GITHUB_RAW   = "https://raw.githubusercontent.com/chamgil71/dailynews/main"

# 최대 카루셀 항목 수 (Instagram 제한: 최대 10개)
MAX_CAROUSEL_ITEMS = 5


def _env(key: str) -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        raise EnvironmentError(f"환경변수 {key} 가 설정되지 않았습니다.")
    return val


def _get(path: str, params: dict) -> dict:
    r = requests.get(f"{GRAPH_BASE}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def _post(path: str, params: dict) -> dict:
    r = requests.post(f"{GRAPH_BASE}{path}", params=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Graph API 오류: {data['error']}")
    return data


def create_carousel_item(ig_user_id: str, token: str, image_url: str) -> str:
    """단일 이미지 미디어 컨테이너 생성 (카루셀 항목). 컨테이너 ID 반환."""
    data = _post(f"/{ig_user_id}/media", {
        "image_url":        image_url,
        "is_carousel_item": "true",
        "access_token":     token,
    })
    container_id = data.get("id", "")
    if not container_id:
        raise RuntimeError(f"컨테이너 생성 실패: {data}")
    return container_id


def wait_for_container(ig_user_id: str, token: str, container_id: str,
                       max_wait: int = 60) -> None:
    """미디어 컨테이너가 FINISHED 상태가 될 때까지 폴링."""
    for _ in range(max_wait // 5):
        data = _get(f"/{container_id}", {"fields": "status_code", "access_token": token})
        status = data.get("status_code", "")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"컨테이너 처리 오류: {data}")
        time.sleep(5)
    raise TimeoutError(f"컨테이너 {container_id} 처리 시간 초과")


def create_carousel(ig_user_id: str, token: str, children: list[str], caption: str) -> str:
    """카루셀 컨테이너 생성. 컨테이너 ID 반환."""
    data = _post(f"/{ig_user_id}/media", {
        "media_type":   "CAROUSEL",
        "children":     ",".join(children),
        "caption":      caption,
        "access_token": token,
    })
    container_id = data.get("id", "")
    if not container_id:
        raise RuntimeError(f"카루셀 컨테이너 생성 실패: {data}")
    return container_id


def publish_carousel(ig_user_id: str, token: str, container_id: str) -> str:
    """카루셀 게시. 미디어 ID 반환."""
    data = _post(f"/{ig_user_id}/media_publish", {
        "creation_id":  container_id,
        "access_token": token,
    })
    media_id = data.get("id", "")
    if not media_id:
        raise RuntimeError(f"게시 실패: {data}")
    return media_id


def build_caption(date_str: str) -> str:
    index_path = CARDNEWS_DIR / "cardnews-data.json"
    issue_titles: list[str] = []
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        for entry in index:
            if entry.get("date") == date_str:
                issue_titles = entry.get("issue_titles", [])
                break

    # 날짜 포맷
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        display = f"{dt.year}년 {dt.month}월 {dt.day}일 ({weekdays[dt.weekday()]})"
    except ValueError:
        display = date_str

    lines = [f"📰 {display} AI 뉴스 브리핑\n"]
    for i, title in enumerate(issue_titles[:3]):
        icons = ["🔥", "📢", "💡"]
        lines.append(f"{icons[i]} {title}")
    lines.append("\n🔗 ms-dailynews.vercel.app")
    lines.append("\n#AI뉴스 #테크뉴스 #데일리뉴스 #인공지능 #AINews #TechNews #DailyBriefing")

    return "\n".join(lines)


def post_cardnews(date_str: str) -> None:
    token       = _env("INSTAGRAM_ACCESS_TOKEN")
    ig_user_id  = _env("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    # 해당 날짜의 PNG 목록 확인
    png_files = sorted(CARDNEWS_DIR.glob(f"{date_str}-*.png"))
    if not png_files:
        raise FileNotFoundError(f"PNG 없음: {CARDNEWS_DIR}/{date_str}-*.png")

    # 최대 MAX_CAROUSEL_ITEMS개로 제한
    png_files = png_files[:MAX_CAROUSEL_ITEMS]
    print(f"  업로드 이미지: {[p.name for p in png_files]}")

    # GitHub raw URL 생성
    image_urls = [
        f"{GITHUB_RAW}/publish/cardnews/{p.name}"
        for p in png_files
    ]

    # 1. 카루셀 항목 컨테이너 생성
    children: list[str] = []
    for i, url in enumerate(image_urls):
        print(f"  미디어 컨테이너 생성 [{i+1}/{len(image_urls)}]: {Path(url).name}")
        cid = create_carousel_item(ig_user_id, token, url)
        children.append(cid)
        print(f"    → {cid}")

    # 2. 컨테이너 처리 완료 대기
    print("  컨테이너 처리 대기 중...")
    for cid in children:
        wait_for_container(ig_user_id, token, cid)

    # 3. 카루셀 컨테이너 생성
    caption = build_caption(date_str)
    print("  카루셀 컨테이너 생성 중...")
    carousel_id = create_carousel(ig_user_id, token, children, caption)
    print(f"    → {carousel_id}")

    # 4. 게시
    print("  Instagram 게시 중...")
    media_id = publish_carousel(ig_user_id, token, carousel_id)
    print(f"  ✅ 게시 완료 — media_id: {media_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (미입력 시 최신)")
    args = parser.parse_args()

    if args.date:
        date_str = args.date
    else:
        index_path = CARDNEWS_DIR / "cardnews-data.json"
        if not index_path.exists():
            print("cardnews-data.json 없음. build_cardnews.py 먼저 실행하세요.")
            sys.exit(1)
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if not index:
            print("카드뉴스 인덱스가 비어 있습니다.")
            sys.exit(1)
        date_str = index[0]["date"]

    print(f"[post-instagram] {date_str}")
    post_cardnews(date_str)


if __name__ == "__main__":
    main()
