"""
카드뉴스 멀티 플랫폼 SNS 발송 (3채널 지원)

사용법:
  python scripts/post_cardnews.py --platform instagram,telegram,twitter
  python scripts/post_cardnews.py --type ai-issue --platform telegram --date 2026-06-04
  python scripts/post_cardnews.py --type stock --platform telegram

지원 플랫폼:
  instagram  - 카루셀 포스트 (Graph API v21.0)
  telegram   - 미디어 그룹 + 인라인 버튼 (기존 봇 재활용)
  twitter    - 이미지 트윗 스레드 (API v2 + tweepy)

필요한 GitHub Secrets:
  [Instagram]
    INSTAGRAM_ACCESS_TOKEN
    INSTAGRAM_BUSINESS_ACCOUNT_ID
  [Telegram] (기존 재활용)
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
  [Twitter/X]
    TWITTER_API_KEY
    TWITTER_API_SECRET
    TWITTER_ACCESS_TOKEN
    TWITTER_ACCESS_TOKEN_SECRET
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
GITHUB_RAW   = "https://raw.githubusercontent.com/chamgil71/dailynews/main"
MAX_CAROUSEL = 5


# ── 공통 유틸 ─────────────────────────────────────────────────────────────────
def _env(key: str, required: bool = True) -> str:
    val = os.environ.get(key, "").strip()
    if not val and required:
        raise EnvironmentError(f"환경변수 {key} 가 설정되지 않았습니다.")
    return val


def _channel_dir(channel: str) -> Path:
    return CARDNEWS_DIR / channel


def _load_index(channel: str, date_str: str) -> dict:
    index_path = _channel_dir(channel) / "data.json"
    if not index_path.exists():
        raise FileNotFoundError(f"data.json 없음: {index_path}")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = next((e for e in index if e["date"] == date_str), None)
    if not entry:
        raise ValueError(f"{date_str} 카드뉴스 인덱스 없음 ({channel})")
    return entry


def _png_paths(channel: str, date_str: str) -> list[Path]:
    paths = sorted(_channel_dir(channel).glob(f"{date_str}-*.png"))
    if not paths:
        raise FileNotFoundError(
            f"PNG 없음: {_channel_dir(channel)}/{date_str}-*.png"
        )
    return paths[:MAX_CAROUSEL]


def _channel_label(channel: str) -> str:
    return {"news": "뉴스", "ai-issue": "AI이슈", "stock": "주식"}.get(channel, channel)


def _build_caption(channel: str, date_str: str, include_link: bool = True) -> str:
    try:
        entry = _load_index(channel, date_str)
        issue_titles = entry.get("issue_titles", [])
    except Exception:
        issue_titles = []

    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["월","화","수","목","금","토","일"]
        display = f"{dt.year}년 {dt.month}월 {dt.day}일 ({weekdays[dt.weekday()]})"
    except ValueError:
        display = date_str

    label = _channel_label(channel)
    icons = ["🔥", "📢", "💡"]
    lines = [f"📰 {display} {label} 브리핑\n"]
    for i, title in enumerate(issue_titles[:3]):
        lines.append(f"{icons[i]} {title}")

    if include_link:
        lines.append(f"\n🔗 ms-dailynews.vercel.app/cardnews/{channel}/{date_str}.html")

    lines.append("\n#AI뉴스 #테크뉴스 #데일리뉴스 #인공지능 #AINews #TechNews")
    return "\n".join(lines)


# ── Instagram ─────────────────────────────────────────────────────────────────
def post_instagram(channel: str, date_str: str) -> None:
    from scripts.post_instagram import post_cardnews as _post
    _post(channel, date_str)


# ── Telegram ──────────────────────────────────────────────────────────────────
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _tg(token: str, method: str, **kwargs) -> dict:
    url  = TELEGRAM_API.format(token=token, method=method)
    resp = requests.post(url, timeout=30, **kwargs)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API 오류 ({method}): {data.get('description')}")
    return data["result"]


def post_telegram(channel: str, date_str: str) -> None:
    token   = _env("TELEGRAM_BOT_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    png_paths = _png_paths(channel, date_str)

    caption = _build_caption(channel, date_str, include_link=True)

    media = []
    files = {}
    for i, p in enumerate(png_paths):
        key = f"photo{i}"
        files[key] = (p.name, p.read_bytes(), "image/png")
        item: dict = {"type": "photo", "media": f"attach://{key}"}
        if i == 0:
            item["caption"] = caption
            item["parse_mode"] = "HTML"
        media.append(item)

    label = _channel_label(channel)
    print(f"  Telegram 미디어 그룹 발송 ({len(png_paths)}장) → chat_id={chat_id}")
    result = _tg(token, "sendMediaGroup",
                 data={"chat_id": chat_id, "media": json.dumps(media)},
                 files=files)

    last_msg_id = result[-1]["message_id"] if isinstance(result, list) else result["message_id"]
    link = f"https://ms-dailynews.vercel.app/cardnews/{channel}/{date_str}.html"
    _tg(token, "sendMessage",
        json={
            "chat_id":    chat_id,
            "text":       f"📖 {label} 카드뉴스 전체 보기",
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "🌐 웹에서 보기", "url": link},
                    {"text": "📂 전체 아카이브", "url": "https://ms-dailynews.vercel.app/archive.html"},
                ]]
            },
        })

    print(f"  ✅ Telegram 발송 완료")


# ── Twitter/X ────────────────────────────────────────────────────────────────
def post_twitter(channel: str, date_str: str) -> None:
    try:
        import tweepy
    except ImportError:
        raise ImportError("tweepy 미설치. pip install tweepy 실행 후 재시도하세요.")

    api_key    = _env("TWITTER_API_KEY")
    api_secret = _env("TWITTER_API_SECRET")
    acc_token  = _env("TWITTER_ACCESS_TOKEN")
    acc_secret = _env("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, acc_token, acc_secret)
    api  = tweepy.API(auth)

    client = tweepy.Client(
        consumer_key=api_key, consumer_secret=api_secret,
        access_token=acc_token, access_token_secret=acc_secret,
    )

    png_paths = _png_paths(channel, date_str)
    caption   = _build_caption(channel, date_str, include_link=True)

    media_ids = []
    for p in png_paths[:4]:
        media = api.media_upload(filename=str(p))
        media_ids.append(str(media.media_id))
        print(f"  업로드: {p.name} → {media.media_id}")
        time.sleep(1)

    resp = client.create_tweet(text=caption[:280], media_ids=media_ids or None)
    tweet_id = resp.data["id"]
    print(f"  ✅ Twitter 발송 완료 — tweet_id: {tweet_id}")


# ── Threads ──────────────────────────────────────────────────────────────────
THREADS_API = "https://graph.threads.net/v1.0"


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


def post_threads(channel: str, date_str: str) -> None:
    token   = _env("THREADS_ACCESS_TOKEN")
    user_id = _env("THREADS_USER_ID")

    png_paths  = _png_paths(channel, date_str)
    caption    = _build_caption(channel, date_str, include_link=True)
    image_urls = [f"{GITHUB_RAW}/publish/cardnews/{channel}/{p.name}" for p in png_paths]

    # 1. 카루셀 아이템 컨테이너 생성
    children = []
    for i, url in enumerate(image_urls):
        print(f"  [Threads] 아이템 컨테이너 생성 [{i+1}/{len(image_urls)}]")
        data = _threads_post(f"/{user_id}/threads", {
            "image_url":        url,
            "media_type":       "IMAGE",
            "is_carousel_item": "true",
            "access_token":     token,
        })
        children.append(data["id"])
        time.sleep(1)

    # 2. 카루셀 컨테이너 생성
    print("  [Threads] 카루셀 컨테이너 생성 중...")
    carousel = _threads_post(f"/{user_id}/threads", {
        "media_type":   "CAROUSEL",
        "children":     ",".join(children),
        "text":         caption,
        "access_token": token,
    })
    creation_id = carousel["id"]

    # 3. 상태 확인 후 게시
    for _ in range(12):
        status = _threads_get(f"/{creation_id}", {
            "fields":       "status",
            "access_token": token,
        })
        if status.get("status") == "FINISHED":
            break
        time.sleep(5)

    result = _threads_post(f"/{user_id}/threads_publish", {
        "creation_id":  creation_id,
        "access_token": token,
    })
    print(f"  ✅ Threads 발송 완료 — id: {result.get('id')}")


# ── Facebook Page ─────────────────────────────────────────────────────────────
GRAPH_API = "https://graph.facebook.com/v21.0"


def post_facebook(channel: str, date_str: str) -> None:
    token   = _env("META_PAGE_ACCESS_TOKEN")
    page_id = _env("FACEBOOK_PAGE_ID")

    png_paths  = _png_paths(channel, date_str)
    caption    = _build_caption(channel, date_str, include_link=True)
    image_urls = [f"{GITHUB_RAW}/publish/cardnews/{channel}/{p.name}" for p in png_paths]

    # 1. 각 이미지 비공개 업로드 → photo_id 수집
    photo_ids = []
    for i, url in enumerate(image_urls):
        print(f"  [Facebook] 이미지 업로드 [{i+1}/{len(image_urls)}]")
        r = requests.post(f"{GRAPH_API}/{page_id}/photos", params={
            "url":          url,
            "published":    "false",
            "access_token": token,
        }, timeout=30)
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Facebook 이미지 업로드 오류: {data['error']}")
        photo_ids.append({"media_fbid": data["id"]})
        time.sleep(1)

    # 2. 멀티 사진 포스트 게시
    print("  [Facebook] 멀티 사진 포스트 게시 중...")
    r = requests.post(f"{GRAPH_API}/{page_id}/feed", params={
        "message":        caption,
        "attached_media": json.dumps(photo_ids),
        "access_token":   token,
    }, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Facebook 포스트 오류: {data['error']}")
    print(f"  ✅ Facebook 발송 완료 — post_id: {data.get('id')}")


# ── 메인 ──────────────────────────────────────────────────────────────────────
PLATFORM_HANDLERS = {
    "instagram": post_instagram,
    "telegram":  post_telegram,
    "twitter":   post_twitter,
    "threads":   post_threads,
    "facebook":  post_facebook,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="카드뉴스 SNS 발송")
    parser.add_argument("--type", dest="channel",
                        choices=["news", "ai-issue", "stock"],
                        default="news", help="카드뉴스 채널")
    parser.add_argument("--platform",
                        default="instagram,telegram",
                        help="발송 플랫폼 (쉼표 구분): instagram,telegram,twitter")
    parser.add_argument("--date", help="YYYY-MM-DD (미입력 시 최신)")
    args = parser.parse_args()

    if args.date:
        date_str = args.date
    else:
        data_path = _channel_dir(args.channel) / "data.json"
        if not data_path.exists():
            print(f"data.json 없음 ({args.channel}). build_cardnews.py 먼저 실행하세요.")
            sys.exit(1)
        index = json.loads(data_path.read_text(encoding="utf-8"))
        if not index:
            print("카드뉴스 인덱스가 비어 있습니다.")
            sys.exit(1)
        date_str = index[0]["date"]

    platforms = [p.strip() for p in args.platform.split(",") if p.strip()]
    print(f"[post-cardnews] {args.channel} / {date_str}  플랫폼: {', '.join(platforms)}")

    errors = []
    for platform in platforms:
        handler = PLATFORM_HANDLERS.get(platform)
        if not handler:
            print(f"  ⚠ 알 수 없는 플랫폼: {platform} (지원: {list(PLATFORM_HANDLERS)})")
            continue
        print(f"\n── {platform.upper()} ──────────────────")
        try:
            handler(args.channel, date_str)
        except EnvironmentError as e:
            print(f"  ⚠ 환경변수 누락 — {e}")
            errors.append(platform)
        except Exception as e:
            print(f"  ✗ {platform} 발송 실패: {e}")
            errors.append(platform)

    if errors:
        print(f"\n실패 플랫폼: {errors}")
        sys.exit(1)
    else:
        print(f"\n모든 플랫폼 발송 완료")


if __name__ == "__main__":
    main()
