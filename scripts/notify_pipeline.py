"""
GitHub Actions 파이프라인 실행 결과 텔레그램 알림.

Usage:
  python scripts/notify_pipeline.py --type news     --status success --date 2026-06-13
  python scripts/notify_pipeline.py --type ai-issue --status failure --date 2026-06-13
  python scripts/notify_pipeline.py --type stock    --status success --date 2026-06-13

환경변수:
  TELEGRAM_BOT_TOKEN       (기존 봇 재활용)
  TELEGRAM_CHAT_ID_MONITOR (별도 모니터링 채널 — GitHub Secret 등록 필요)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_KST = timezone(timedelta(hours=9))

ACTIONS_URL = "https://github.com/chamgil71/dailynews/actions"
SITE_URLS = {
    "news":     "https://ms-dailynews.vercel.app/",
    "ai-issue": "https://ms-dailynews.vercel.app/ai-issue/",
    "stock":    "https://ms-dailynews.vercel.app/stock/",
}


def _send(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "Markdown",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()
        return True
    except Exception as e:
        print(f"[notify] 텔레그램 전송 실패: {e}", file=sys.stderr)
        return False


def _now_kst() -> str:
    return datetime.now(_KST).strftime("%Y-%m-%d %H:%M KST")


# ── 채널별 성공 메시지 ──────────────────────────────────────────────────────────

def _msg_news_success(date_str: str) -> str:
    json_path = _ROOT / "reports" / f"news_{date_str}.json"
    md_path   = _ROOT / "reports" / f"news_{date_str}.md"

    # stats: MD 첫 줄 파싱 (예: 📊 수집: 총 159건 (EN: 87 / KO: 72) | AI 분석: 40건 | 키워드 매칭: 0건)
    total = en_cnt = ko_cnt = ai_cnt = kw_cnt = dup_cnt = 0
    if md_path.exists():
        first_lines = md_path.read_text(encoding="utf-8")[:500]
        m = re.search(r"총\s*(\d+)건.*EN:\s*(\d+).*KO:\s*(\d+).*AI 분석:\s*(\d+)건.*키워드.*?(\d+)건.*중복.*?(\d+)건", first_lines)
        if m:
            total, en_cnt, ko_cnt, ai_cnt, kw_cnt, dup_cnt = (int(x) for x in m.groups())

    # analysis_ok, fallback, top issues
    analysis_ok = True
    fallback_en = fallback_ko = False
    top3: list[str] = []
    if json_path.exists():
        try:
            d = json.loads(json_path.read_text(encoding="utf-8"))
            analysis_ok = d.get("analysis_ok", True)
            fb = d.get("fallback_used", {})
            fallback_en = fb.get("en", False)
            fallback_ko = fb.get("ko", False)
            for section in ("en", "ko"):
                for issue in d.get(section, {}).get("issues", [])[:2]:
                    t = issue.get("title", "")
                    if t and t not in top3:
                        top3.append(t)
                    if len(top3) >= 3:
                        break
                if len(top3) >= 3:
                    break
        except Exception:
            pass

    ai_icon = "✅" if analysis_ok else "⚠️"
    fb_note = ""
    if fallback_en or fallback_ko:
        parts = (["해외"] if fallback_en else []) + (["국내"] if fallback_ko else [])
        fb_note = f"\n⚡ 폴백 모델 사용: {', '.join(parts)}"

    issues_block = ""
    icons = ["🔥", "📢", "💡"]
    for i, t in enumerate(top3):
        short = t[:45] + ("…" if len(t) > 45 else "")
        issues_block += f"  {icons[i]} {short}\n"

    return (
        f"✅ *뉴스 브리핑 완료*\n"
        f"📅 {date_str}  |  {_now_kst()}\n\n"
        f"📊 수집 통계\n"
        f"  총 기사: *{total}건* (EN {en_cnt} / KO {ko_cnt})\n"
        f"  AI 분석: *{ai_cnt}건*  키워드 매칭: *{kw_cnt}건*  중복 제외: {dup_cnt}건\n\n"
        f"{ai_icon} AI 분석 {'완료' if analysis_ok else '미완성'}{fb_note}\n"
        f"{''.join(chr(10) + issues_block) if issues_block else ''}"
        f"\n🌐 {SITE_URLS['news']}"
    )


def _msg_ai_issue_success(date_str: str) -> str:
    json_path = _ROOT / "reports" / "ai-issue" / f"ai_issue_{date_str}.json"

    period = date_str
    top10_cnt = 0
    top3_titles: list[str] = []
    cat_stats: dict = {}

    if json_path.exists():
        try:
            d = json.loads(json_path.read_text(encoding="utf-8"))
            period      = d.get("period", date_str)
            top10       = d.get("top10", [])
            top10_cnt   = len(top10)
            top3_titles = [item.get("title", "") for item in top10[:3]]
            cat_stats   = d.get("category_stats", {})
        except Exception:
            pass

    # 카테고리 요약
    cat_labels = {
        "model": "모델", "service": "서비스", "research": "연구",
        "policy": "정책", "industry": "산업", "infra": "인프라",
        "investment": "투자",
    }
    cat_parts = [f"{cat_labels.get(k, k)} {v}" for k, v in cat_stats.items() if v]
    cat_line = " / ".join(cat_parts) if cat_parts else "-"

    icons = ["🥇", "🥈", "🥉"]
    top3_block = ""
    for i, t in enumerate(top3_titles):
        short = t[:45] + ("…" if len(t) > 45 else "")
        top3_block += f"  {icons[i]} {short}\n"

    return (
        f"✅ *AI 주간이슈 완료*\n"
        f"📅 {period}  |  {_now_kst()}\n\n"
        f"📌 TOP {top10_cnt} 이슈 분석 완료\n"
        f"{top3_block}\n"
        f"📂 카테고리별 수집\n  {cat_line}\n\n"
        f"🌐 {SITE_URLS['ai-issue']}"
    )


def _msg_stock_success(date_str: str) -> str:
    md_path = _ROOT / "reports" / "stock" / f"stock_{date_str}.md"

    temperature = "🟡 중립"
    summary_lines: list[str] = []

    if md_path.exists():
        try:
            text = md_path.read_text(encoding="utf-8")
            m = re.search(r"## 시장 온도계[:\s]*(.*)", text)
            if m:
                temperature = m.group(1).strip()
            sm = re.search(r"## ■ 핵심 요약[^\n]*\n([\s\S]*?)(?=\n---|\n## |\Z)", text, re.M)
            if sm:
                lines = [l.strip(" -·•") for l in sm.group(1).splitlines() if l.strip()]
                summary_lines = lines[:3]
        except Exception:
            pass

    summary_block = ""
    for line in summary_lines:
        short = line[:60] + ("…" if len(line) > 60 else "")
        summary_block += f"  • {short}\n"

    return (
        f"✅ *주식시황 빌드 완료*\n"
        f"📅 {date_str}  |  {_now_kst()}\n\n"
        f"🌡️ 시장 온도계: *{temperature}*\n\n"
        f"📋 핵심 요약\n{summary_block}"
        f"\n🌐 {SITE_URLS['stock']}"
    )


# ── 실패 메시지 ────────────────────────────────────────────────────────────────

def _msg_failure(channel: str, date_str: str) -> str:
    labels = {"news": "뉴스 브리핑", "ai-issue": "AI 주간이슈", "stock": "주식시황"}
    label = labels.get(channel, channel)
    return (
        f"🔴 *{label} 파이프라인 실패*\n"
        f"📅 {date_str}  |  {_now_kst()}\n\n"
        f"GitHub Actions 워크플로우에서 오류가 발생했습니다.\n\n"
        f"🔗 {ACTIONS_URL}"
    )


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="파이프라인 결과 텔레그램 알림")
    parser.add_argument("--type", dest="channel",
                        choices=["news", "stock", "ai-issue"], required=True)
    parser.add_argument("--status", choices=["success", "failure"], default="failure")
    parser.add_argument("--date",
                        default=datetime.now(_KST).strftime("%Y-%m-%d"),
                        help="YYYY-MM-DD (기본: KST 오늘)")
    args = parser.parse_args()

    token   = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID_MONITOR", "").strip()
    if not token or not chat_id:
        print("[notify] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID_MONITOR 미설정 — 알림 건너뜀",
              file=sys.stderr)
        sys.exit(0)  # 미설정 시 워크플로우 실패 전파 방지

    if args.status == "success":
        if args.channel == "news":
            msg = _msg_news_success(args.date)
        elif args.channel == "ai-issue":
            msg = _msg_ai_issue_success(args.date)
        else:
            msg = _msg_stock_success(args.date)
    else:
        msg = _msg_failure(args.channel, args.date)

    ok = _send(token, chat_id, msg)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
