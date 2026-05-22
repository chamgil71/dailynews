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

    # structured 데이터가 ko 또는 en 아래에 감싸져 있는 경우가 대부분이므로 추출 로직 고도화
    data = None
    if "ko" in structured_data and isinstance(structured_data["ko"], dict) and "issues" in structured_data["ko"]:
        data = structured_data["ko"]
    elif "en" in structured_data and isinstance(structured_data["en"], dict) and "issues" in structured_data["en"]:
        data = structured_data["en"]
    elif "issues" in structured_data:
        data = structured_data
    else:
        # structured_data 자체가 비어있거나 올바른 형식이 아닐 경우
        logger.warning("[Telegram] 올바른 구조화(structured) 데이터를 찾을 수 없어 텔레그램 카드뉴스 발송을 취소합니다.")
        return False

    issues = data.get("issues", [])
    trends = data.get("trends", [])

    if not issues:
        logger.warning("[Telegram] 구조화된 이슈 목록이 없어 발송하지 않습니다.")
        return False

    # HTML 마크업 생성
    # 텔레그램 HTML 파싱 에러 방지를 위해 html.escape를 세심히 적용
    msg_lines = []
    msg_lines.append(f"📅 <b>Daily News Brief - {date_str}</b>\n")
    msg_lines.append("🔥 <b>오늘의 핵심 이슈 TOP 3</b>\n")

    emoji_ranks = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}

    for issue in issues[:3]:
        rank = issue.get("rank", 1)
        rank_emoji = emoji_ranks.get(rank, "🔹")
        title = html.escape(issue.get("title", "이슈"))
        summary = html.escape(issue.get("summary", ""))
        
        msg_lines.append(f"{rank_emoji} <b>{title}</b>")
        if summary:
            msg_lines.append(f"➔ {summary}")
            
        # 첫 번째 소스 가져오기
        sources = issue.get("sources", [])
        if sources:
            src = sources[0]
            src_title = html.escape(src.get("title", "원문 보기"))
            src_url = src.get("url", "")
            if src_url:
                msg_lines.append(f"🔗 주요 출처: <a href=\"{src_url}\">{src_title}</a>")
        msg_lines.append("")  # 공백 라인 추가

    if trends:
        msg_lines.append("🔍 <b>오늘의 주목할 트렌드</b>")
        kw_tags = []
        for trend in trends[:5]:
            keyword = trend.get("keyword", "").replace(" ", "_")
            if keyword:
                kw_tags.append(f"#{html.escape(keyword)}")
        if kw_tags:
            msg_lines.append(" ".join(kw_tags))
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
