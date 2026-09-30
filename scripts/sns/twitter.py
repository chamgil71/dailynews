"""Twitter/X 발송 — 이미지 트윗 (API v2 + tweepy). text 모드는 미디어 없이 트윗."""
from __future__ import annotations

import time

from scripts.sns.caption import build_caption
from scripts.sns.common import env, png_paths


def post_twitter(channel: str, date_str: str, mode: str = "image") -> None:
    """카드 PNG(최대 4장) 첨부 트윗. 캡션은 280자로 자름."""
    try:
        import tweepy
    except ImportError:
        raise ImportError("tweepy 미설치. pip install tweepy 실행 후 재시도하세요.")

    api_key    = env("TWITTER_API_KEY")
    api_secret = env("TWITTER_API_SECRET")
    acc_token  = env("TWITTER_ACCESS_TOKEN")
    acc_secret = env("TWITTER_ACCESS_TOKEN_SECRET")

    api = tweepy.API(tweepy.OAuth1UserHandler(api_key, api_secret, acc_token, acc_secret))
    client = tweepy.Client(
        consumer_key=api_key, consumer_secret=api_secret,
        access_token=acc_token, access_token_secret=acc_secret,
    )

    paths   = [] if mode == "text" else png_paths(channel, date_str)
    caption = build_caption(channel, date_str, include_link=True)

    media_ids = []
    for p in paths[:4]:
        media = api.media_upload(filename=str(p))
        media_ids.append(str(media.media_id))
        print(f"  업로드: {p.name} → {media.media_id}")
        time.sleep(1)

    resp = client.create_tweet(text=caption[:280], media_ids=media_ids or None)
    print(f"  ✅ Twitter 발송 완료 — tweet_id: {resp.data['id']}")
