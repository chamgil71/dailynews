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


def send_stock_telegram(stock_data: dict, date_str: str = None) -> bool:
    """
    주식 시황 MD 파싱 데이터를 텔레그램 @msstockbrief 채널로 발송.
    stock_data: parse_stock_md() 반환값
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id   = os.getenv("TELEGRAM_CHAT_ID_STOCK")

    if not bot_token or not chat_id:
        logger.warning("[Telegram/주식] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID_STOCK 미설정 — 발송 건너뜀")
        return False

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    try:
        _wd = ["월","화","수","목","금","토","일"][datetime.strptime(date_str, "%Y-%m-%d").weekday()]
        date_label = f"{date_str} ({_wd})"
    except (ValueError, IndexError):
        date_label = date_str

    temp     = stock_data.get("temperature", {})
    market   = stock_data.get("market", {})
    summary  = stock_data.get("summary", "")
    keywords = stock_data.get("keywords", [])

    lines = [f"📈 <b>Ms Stock Brief</b> — {html.escape(date_label)}", ""]
    lines.append(f"🌡 <b>시장 온도계</b>: {html.escape(temp.get('display', '🟡 중립'))}")
    lines.append("")

    if summary:
        lines.append("📌 <b>핵심 요약</b>")
        for line in summary.splitlines():
            line = line.strip().lstrip("- ").strip()
            if line:
                lines.append(f"  • {html.escape(line)}")
        lines.append("")

    index_rows = []
    for key, label in [("kospi", "코스피"), ("kosdaq", "코스닥"), ("sp500", "S&P500"), ("usd_krw", "원/달러")]:
        if market.get(key):
            k = market[key]
            suffix = "원" if key == "usd_krw" else ""
            index_rows.append(f"{label} {html.escape(k['close_str'])}{suffix} ({html.escape(k['chg_str'])})")
    if index_rows:
        lines.append("📊 <b>주요 지수</b>")
        for row in index_rows:
            lines.append(f"  {row}")
        lines.append("")

    if keywords:
        lines.append("🔑 <b>핵심 키워드</b>")
        for kw in keywords[:3]:
            lines.append(f"  • <b>{html.escape(kw.get('title', ''))}</b>")
        lines.append("")

    link_url = f"{SITE_BASE_URL}/stock/" if SITE_BASE_URL else ""
    if link_url:
        lines.append(f"📰 <a href=\"{link_url}\">전체 시황 보기</a>")

    message_text = "\n".join(lines)
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message_text, "parse_mode": "HTML", "disable_web_page_preview": True}

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("[Telegram/주식] 발송 완료")
            return True
        else:
            logger.error(f"[Telegram/주식] 발송 실패: {res_data.get('description', '알 수 없는 오류')}")
            return False
    except Exception as e:
        logger.error(f"[Telegram/주식] 통신 오류: {e}")
        return False


def send_weekly_stock_telegram(data: dict, date_str: str = None) -> bool:
    """주간 주식 시황 종합을 @msstockbrief 채널로 발송."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id   = os.getenv("TELEGRAM_CHAT_ID_STOCK")

    if not bot_token or not chat_id:
        logger.warning("[Telegram/주간주식] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID_STOCK 미설정 — 발송 건너뜀")
        return False

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    week_range     = data.get("week_range", "")
    temp           = data.get("temperature", {})
    summary        = data.get("summary", "")
    hot_themes     = data.get("hot_themes", [])
    weekly_indices = data.get("weekly_indices", [])
    next_week      = data.get("next_week_schedule", [])

    header = html.escape(week_range or date_str)
    lines = [f"📅 <b>Ms Stock Weekly</b> — {header}", ""]
    lines.append(f"🌡 <b>주간 온도계</b>: {html.escape(temp.get('display', '🟡 중립'))}")
    lines.append("")

    if summary:
        lines.append(f"📌 <b>주간 총평</b>: {html.escape(summary)}")
        lines.append("")

    if weekly_indices:
        lines.append("📊 <b>주간 지수 성과</b>")
        for row in weekly_indices[:4]:
            lines.append(
                f"  {html.escape(row.get('label',''))}: "
                f"{html.escape(row.get('close',''))} "
                f"({html.escape(row.get('change',''))})"
            )
        lines.append("")

    if hot_themes:
        lines.append("🔥 <b>이번 주 핫 테마</b>")
        for t in hot_themes[:3]:
            lines.append(f"  • <b>{html.escape(t.get('title',''))}</b>")
        lines.append("")

    if next_week:
        lines.append("📅 <b>차주 주요 일정</b>")
        for row in next_week[:3]:
            lines.append(
                f"  {html.escape(row.get('date',''))}: {html.escape(row.get('event',''))}"
            )
        lines.append("")

    link_url = f"{SITE_BASE_URL}/stock/" if SITE_BASE_URL else ""
    if link_url:
        lines.append(f'📰 <a href="{link_url}">전체 시황 보기</a>')

    message_text = "\n".join(lines)
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message_text, "parse_mode": "HTML",
               "disable_web_page_preview": True}

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("[Telegram/주간주식] 발송 완료")
            return True
        else:
            logger.error(f"[Telegram/주간주식] 발송 실패: {res_data.get('description', '알 수 없는 오류')}")
            return False
    except Exception as e:
        logger.error(f"[Telegram/주간주식] 통신 오류: {e}")
        return False


def send_ai_issue_telegram(report_data: dict, date_str: str = None) -> bool:
    """
    주간 AI Issue 보고서 요약을 텔레그램으로 발송.
    report_data: reports/ai-issue/ai_issue_YYYY-MM-DD.json 내용
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.warning("[Telegram/AI이슈] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 미설정 — 발송 건너뜀")
        return False

    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    period = report_data.get("period", date_str)
    top10 = report_data.get("top10", [])
    _raw_outlook = report_data.get("next_week_outlook", "")
    # Gemini가 JSON 문자열로 반환하는 경우 파싱하여 포인트 목록으로 변환
    if isinstance(_raw_outlook, str) and _raw_outlook.strip().startswith("{"):
        try:
            import json as _json
            _obj = _json.loads(_raw_outlook)
            _points = _obj.get("points", [])
            outlook = " / ".join(p.get("point", "") for p in _points[:3] if p.get("point"))
        except Exception:
            outlook = _raw_outlook
    else:
        outlook = _raw_outlook

    lines = [f"🤖 <b>AI Issue Weekly</b> — {html.escape(period)}", ""]

    # TOP 3 이슈
    cat_icons = {
        "model": "🤖", "service": "🚀", "research": "🔬",
        "policy": "⚖️", "industry": "🏭", "infra": "🖥️", "investment": "💰",
    }
    rank_emojis = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣"}
    lines.append("🔝 <b>이번 주 TOP 3 이슈</b>")
    for item in top10[:3]:
        rank = item.get("rank", 1)
        cat = item.get("category", "")
        icon = cat_icons.get(cat, "🔹")
        title = html.escape(item.get("title", ""))
        summary = html.escape(item.get("summary", ""))
        lines.append(f"{rank_emojis.get(rank, '🔹')} {icon} <b>{title}</b>")
        if summary:
            lines.append(f"  ➔ {summary}")
        lines.append("")

    # 4~10위 심플 목록
    if len(top10) > 3:
        lines.append("📋 <b>그 외 주요 이슈</b>")
        for item in top10[3:]:
            rank = item.get("rank", "")
            title = html.escape(item.get("title", ""))
            lines.append(f"  {rank}. {title}")
        lines.append("")

    # 차주 전망
    if outlook:
        short = html.escape(outlook[:120])
        if len(outlook) > 120:
            short += "..."
        lines.append(f"🔮 <b>차주 전망</b>: {short}")
        lines.append("")

    # 사이트 링크
    link_url = f"{SITE_BASE_URL}/ai-issue/" if SITE_BASE_URL else ""
    if link_url:
        lines.append(f"📰 <a href=\"{link_url}\">전체 보고서 보기</a>")

    message_text = "\n".join(lines)

    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("[Telegram/AI이슈] 발송 완료")
            return True
        else:
            logger.error(f"[Telegram/AI이슈] 발송 실패: {res_data.get('description', '알 수 없는 오류')}")
            return False
    except Exception as e:
        logger.error(f"[Telegram/AI이슈] 통신 오류: {e}")
        return False
