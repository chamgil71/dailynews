"""Telegram 카드뉴스 발송 — 미디어 그룹 + 인라인 버튼 (text 모드: 캡션 + 버튼 1건)."""
from __future__ import annotations

import json

import requests

from scripts.sns.caption import build_caption
from scripts.sns.common import SITE_BASE, channel_label, channel_site_url, env, png_paths

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _tg(token: str, method: str, **kwargs) -> dict:
    url  = TELEGRAM_API.format(token=token, method=method)
    resp = requests.post(url, timeout=30, **kwargs)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API 오류 ({method}): {data.get('description')}")
    return data["result"]


def _telegram_buttons(channel: str) -> dict:
    return {"inline_keyboard": [[
        {"text": "🌐 웹에서 보기", "url": channel_site_url(channel)},
        {"text": "📂 전체 아카이브", "url": f"{SITE_BASE}/archive.html"},
    ]]}


def post_telegram(channel: str, date_str: str, mode: str = "image") -> None:
    """stock → TELEGRAM_CHAT_ID_STOCK, 그 외 → TELEGRAM_CHAT_ID 로 발송."""
    token   = env("TELEGRAM_BOT_TOKEN")
    chat_id = env("TELEGRAM_CHAT_ID_STOCK" if channel == "stock" else "TELEGRAM_CHAT_ID")

    caption = build_caption(channel, date_str, include_link=True)
    if mode == "text":
        # 텍스트 모드: 캡션 + 버튼 1건 (기본 플랫폼 목록에서는 send_telegram.py 와 중복이라 제외됨)
        _tg(token, "sendMessage", json={
            "chat_id": chat_id, "text": caption,
            "disable_web_page_preview": True,
            "reply_markup": _telegram_buttons(channel),
        })
        print("  ✅ Telegram 텍스트 발송 완료")
        return

    paths = png_paths(channel, date_str)
    media = []
    files = {}
    for i, p in enumerate(paths):
        key = f"photo{i}"
        files[key] = (p.name, p.read_bytes(), "image/png")
        item: dict = {"type": "photo", "media": f"attach://{key}"}
        if i == 0:
            item["caption"] = caption
            item["parse_mode"] = "HTML"
        media.append(item)

    print(f"  Telegram 미디어 그룹 발송 ({len(paths)}장) → {channel} 채널 (chat_id={chat_id})")
    _tg(token, "sendMediaGroup",
        data={"chat_id": chat_id, "media": json.dumps(media)}, files=files)
    _tg(token, "sendMessage", json={
        "chat_id":      chat_id,
        "text":         f"📖 {channel_label(channel)} 브리핑 전체 보기",
        "parse_mode":   "HTML",
        "reply_markup": _telegram_buttons(channel),
    })
    print("  ✅ Telegram 발송 완료")
