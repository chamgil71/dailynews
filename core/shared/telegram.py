# core/shared/telegram.py
"""
텔레그램 봇 API를 통한 실시간 뉴스 브리핑 / 카드뉴스 알림 발송 모듈
"""

import logging
import os
import html
import requests
from datetime import datetime
from config.settings import SITE_BASE_URL

logger = logging.getLogger(__name__)

def send_telegram_cardnews(structured_data: dict, date_str: str = None) -> bool:
    """
    구조화된 AI 분석 데이터를 기반으로 텔레그램 알림을 발송합니다.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("[Telegram] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않아 발송을 건너뜁니다.")
        return False

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # structured 데이터 내 ko(국내) 및 en(글로벌) 데이터 동시 추출
    ko_data = structured_data.get("ko") if isinstance(structured_data.get("ko"), dict) else None
    en_data = structured_data.get("en") if isinstance(structured_data.get("en"), dict) else None
    
    # 껍데기 없이 최상위에 직접 있는 경우 폴백
    if not ko_data and not en_data and "issues" in structured_data:
        if structured_data.get("lang") == "ko":
            ko_data = structured_data
        else:
            en_data = structured_data

    if not ko_data and not en_data:
        logger.warning("[Telegram] 올바른 구조화(structured) 데이터를 찾을 수 없어 텔레그램 카드뉴스 발송을 취소합니다.")
        return False

    # HTML 마크업 생성
    msg_lines = []
    msg_lines.append(f"📅 <b>Daily News Brief - {date_str}</b>\n")

    emoji_ranks = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}
    all_trends = []

    # 1. 글로벌 핵심 이슈 (EN) 송출
    if en_data and en_data.get("issues"):
        msg_lines.append("🌐 <b>글로벌 핵심 이슈 TOP 3</b>")
        for issue in en_data.get("issues", [])[:3]:
            rank = issue.get("rank", 1)
            rank_emoji = emoji_ranks.get(rank, "🔹")
            title = html.escape(issue.get("title", "이슈"))
            summary = html.escape(issue.get("summary", ""))
            msg_lines.append(f"{rank_emoji} <b>{title}</b>")
            if summary:
                msg_lines.append(f"➔ {summary}")
            sources = issue.get("sources", [])
            if sources and sources[0].get("url"):
                src = sources[0]
                src_title = html.escape(src.get("title", "원문 보기"))
                msg_lines.append(f"🔗 주요 출처: <a href=\"{src['url']}\">{src_title}</a>")
            msg_lines.append("")
        all_trends.extend(en_data.get("trends", []))

    # 2. 국내 핵심 이슈 (KO) 송출
    if ko_data and ko_data.get("issues"):
        msg_lines.append("🇰🇷 <b>국내 핵심 이슈 TOP 3</b>")
        for issue in ko_data.get("issues", [])[:3]:
            rank = issue.get("rank", 1)
            rank_emoji = emoji_ranks.get(rank, "🔹")
            title = html.escape(issue.get("title", "이슈"))
            summary = html.escape(issue.get("summary", ""))
            msg_lines.append(f"{rank_emoji} <b>{title}</b>")
            if summary:
                msg_lines.append(f"➔ {summary}")
            sources = issue.get("sources", [])
            if sources and sources[0].get("url"):
                src = sources[0]
                src_title = html.escape(src.get("title", "원문 보기"))
                msg_lines.append(f"🔗 주요 출처: <a href=\"{src['url']}\">{src_title}</a>")
            msg_lines.append("")
        all_trends.extend(ko_data.get("trends", []))

    # 3. 해시태그 트렌드 통합 송출
    if all_trends:
        msg_lines.append("🔍 <b>오늘의 주목할 트렌드</b>")
        seen_kws = set()
        kw_tags = []
        for trend in all_trends:
            keyword = trend.get("keyword", "").strip().replace(" ", "_")
            if keyword and keyword.lower() not in seen_kws:
                seen_kws.add(keyword.lower())
                kw_tags.append(f"#{html.escape(keyword)}")
        if kw_tags:
            msg_lines.append(" ".join(kw_tags[:8]))  # 가독성을 위해 최대 8개 제한
        msg_lines.append("")

    # 카드뉴스 및 대시보드 바로가기 링크
    link_url = f"{SITE_BASE_URL}/" if SITE_BASE_URL else ""
    if link_url:
        msg_lines.append("🃏 <b>모바일 가로 스크롤 카드뉴스로 읽기</b>")
        msg_lines.append(f"👉 <a href=\"{link_url}\">데일리 뉴스 대시보드 바로가기</a>")

    message_text = "\n".join(msg_lines)

    # Telegram API 호출
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("[Telegram] 텔레그램 카드뉴스 요약 알림을 성공적으로 발송했습니다.")
            return True
        else:
            logger.error(f"[Telegram] 알림 발송 실패: {res_data.get('description', '알 수 없는 오류')}")
            return False
    except Exception as e:
        logger.error(f"[Telegram] 통신 오류 발생: {e}")
        return False
