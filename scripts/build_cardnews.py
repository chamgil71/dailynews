"""
카드뉴스 HTML 생성기
publish/reports-data.json → publish/cardnews/YYYY-MM-DD.html
                          → publish/cardnews/cardnews-data.json

각 HTML 파일은 ?card=0..4 쿼리 파라미터로 특정 슬라이드만 표시 (Playwright 스크린샷용).
card=0: 커버, card=1~3: 핵심 이슈, card=4: 트렌드

사용법:
  python scripts/build_cardnews.py                    # 최신 날짜만
  python scripts/build_cardnews.py --date 2026-06-04  # 특정 날짜
  python scripts/build_cardnews.py --all              # 전체 재빌드
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

REPORTS_DATA = Path(_ROOT, "publish", "reports-data.json")
CARDNEWS_DIR = Path(_ROOT, "publish", "cardnews")
CARDNEWS_DIR.mkdir(parents=True, exist_ok=True)

CATEGORY_LABELS = {
    "ai_ml":          "AI·ML",
    "technology":     "기술",
    "economy":        "경제",
    "global_news":    "글로벌",
    "korean_news":    "국내",
    "korean_economy": "한국경제",
    "korean_tech":    "한국기술",
    "security":       "보안",
    "startup":        "스타트업",
}
ISSUE_ICONS  = ["&#128293;", "&#128226;", "&#128161;"]  # 🔥📢💡 HTML entities
ISSUE_COLORS = ["#f59e0b", "#818cf8", "#34d399"]
TREND_ICONS  = ["&#128202;", "&#127919;", "&#9889;"]   # 📊🎯⚡ HTML entities


def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        return f"{dt.year}년 {dt.month}월 {dt.day}일 ({weekdays[dt.weekday()]})"
    except ValueError:
        return date_str


def _cat_label(cat: str) -> str:
    return CATEGORY_LABELS.get(cat, cat)


def _card_html(card_idx: int, total_cards: int, content_html: str, date_str: str,
               layout: str = "") -> str:
    dots = "".join(
        f'<span class="dot {"active" if i == card_idx else ""}"></span>'
        for i in range(total_cards)
    )
    inner_class = f'card-inner{" layout-" + layout if layout else ""}'
    return f"""
<div class="card" id="card-{card_idx}">
  <div class="card-topbar"></div>
  <div class="{inner_class}">
    {content_html}
  </div>
  <div class="card-footer">
    <span class="site-tag">ms-dailynews.vercel.app</span>
    <div class="dots">{dots}</div>
    <span class="date-tag">{date_str}</span>
  </div>
</div>"""


def build_cover(issues: list[dict], date_str: str, display_date: str,
                card_idx: int, total_cards: int) -> str:
    issue_lines = ""
    for i, issue in enumerate(issues[:3]):
        icon = ISSUE_ICONS[i]
        color = ISSUE_COLORS[i]
        title = issue.get("title", "")[:32] + ("..." if len(issue.get("title", "")) > 32 else "")
        issue_lines += f"""
    <div class="cover-issue">
      <span class="cover-icon" style="color:{color}">{icon}</span>
      <span class="cover-issue-text">{title}</span>
    </div>"""

    content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div class="logo-text">
      <div class="logo-main">AI News Brief</div>
      <div class="logo-sub">매일 아침 AI가 정리하는 핵심 뉴스</div>
    </div>
  </div>
  <div class="cover-date">{display_date}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 핵심 이슈</div>
  <div class="cover-issues">{issue_lines}
  </div>
  <div class="cover-tags">#AI뉴스 #테크 #데일리브리핑 #인공지능</div>"""

    return _card_html(card_idx, total_cards, content, _fmt_date(date_str))


def build_issue_card(issue: dict, rank: int, date_str: str,
                     card_idx: int, total_cards: int) -> str:
    icon  = ISSUE_ICONS[rank - 1]
    color = ISSUE_COLORS[rank - 1]
    cat   = _cat_label(issue.get("category", ""))
    title = issue.get("title", "")
    summary = issue.get("summary", "")
    src_count = len(issue.get("sources", []))

    first_source_url = ""
    sources = issue.get("sources", [])
    if sources:
        first_source_url = sources[0].get("url", "")

    content = f"""
  <div class="issue-top" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">핵심 이슈 {rank}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-body">
    <div class="issue-title">{title}</div>
    <div class="issue-divider" style="background:{color}"></div>
    <div class="issue-summary">{summary}</div>
  </div>
  <div class="issue-bottom">
    <span>&#128206; 출처 {src_count}개</span>
    {"&nbsp;&nbsp;·&nbsp;&nbsp;<a href='" + first_source_url + "' style='color:#38bdf8;text-decoration:none;font-size:24px'>원문 보기 →</a>" if first_source_url else ""}
  </div>"""

    return _card_html(card_idx, total_cards, content, _fmt_date(date_str), layout="issue")


def build_trends_card(trends: list[dict], date_str: str,
                      card_idx: int, total_cards: int) -> str:
    trend_items = ""
    for i, trend in enumerate(trends[:3]):
        icon = TREND_ICONS[i]
        kw   = trend.get("keyword", "")
        desc = trend.get("description", "")[:70] + ("..." if len(trend.get("description", "")) > 70 else "")
        trend_items += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{icon}</span>
        <span class="trend-keyword">#{kw}</span>
      </div>
      <div class="trend-desc">{desc}</div>
    </div>"""

    content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주목할 트렌드 키워드</span>
  </div>
  <div class="trends-list">{trend_items}
  </div>"""

    return _card_html(card_idx, total_cards, content, _fmt_date(date_str), layout="trends")


CARD_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: 1080px;
  background: #000;
  font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic',
               'Noto Sans CJK KR', sans-serif;
}
.card {
  width: 1080px;
  height: 1080px;
  display: none;
  flex-direction: column;
  background: linear-gradient(145deg, #0a0f1e 0%, #0f172a 45%, #111f3a 100%);
  position: relative;
  overflow: hidden;
}
.card.active { display: flex; }

/* 배경 장식 */
.card::before {
  content: '';
  position: absolute;
  top: -280px; right: -180px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 65%);
  pointer-events: none;
}
.card::after {
  content: '';
  position: absolute;
  bottom: -200px; left: -120px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 65%);
  pointer-events: none;
}

/* 상단 컬러 라인 */
.card-topbar {
  height: 5px;
  background: linear-gradient(90deg, #38bdf8, #6366f1, #a78bfa);
  flex-shrink: 0;
}

.card-inner {
  flex: 1;
  padding: 60px 80px 28px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  position: relative;
  z-index: 1;
}
/* 이슈 카드만 space-between으로 콘텐츠를 위아래로 배분 */
.card-inner.layout-issue {
  justify-content: space-between;
}

.card-footer {
  padding: 18px 80px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
  border-top: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}
.site-tag { font-size: 24px; color: #38bdf8; font-weight: 600; letter-spacing: -0.3px; }
.date-tag { font-size: 24px; color: #475569; }
.dots { display: flex; gap: 10px; align-items: center; }
.dot { width: 11px; height: 11px; border-radius: 50%; background: rgba(255,255,255,0.18); }
.dot.active { background: #38bdf8; width: 32px; border-radius: 6px; }

/* ── Cover ─────────────────────────────────────────────────── */
.cover-logo {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-bottom: 36px;
}
.logo-badge {
  width: 78px; height: 78px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 30px; font-weight: 900; color: #fff;
  letter-spacing: -1px;
  flex-shrink: 0;
}
.logo-main { font-size: 40px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px; }
.logo-sub  { font-size: 24px; color: #94a3b8; margin-top: 5px; font-weight: 400; }

.cover-date {
  font-size: 32px; color: #38bdf8; font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: -0.3px;
}
.cover-divider {
  height: 2px;
  background: linear-gradient(90deg, rgba(56,189,248,0.8) 0%, transparent 100%);
  margin-bottom: 30px;
}
.cover-headline {
  font-size: 26px; color: #64748b; font-weight: 500;
  margin-bottom: 22px;
  letter-spacing: 3px;
}
.cover-issues { display: flex; flex-direction: column; gap: 18px; }
.cover-issue {
  display: flex; align-items: flex-start; gap: 18px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 16px;
  padding: 18px 24px;
}
.cover-icon { font-size: 32px; flex-shrink: 0; margin-top: 2px; line-height: 1; }
.cover-issue-text {
  font-size: 30px; color: #f1f5f9; font-weight: 600;
  line-height: 1.45; letter-spacing: -0.3px;
}
.cover-tags {
  margin-top: 28px;
  font-size: 24px; color: #334155; font-weight: 400;
}

/* ── Issue Card ─────────────────────────────────────────────── */
.issue-top { /* rank badge + category */
  display: flex; align-items: center; gap: 14px;
}
.rank-icon { font-size: 48px; line-height: 1; }
.rank-label { font-size: 32px; font-weight: 700; letter-spacing: -0.5px; }
.cat-badge {
  font-size: 24px; padding: 8px 22px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 26px;
  color: #cbd5e1;
  margin-left: auto;
  font-weight: 500;
}
.issue-body { /* title + divider + summary - 가운데 영역 flex-grow */
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 32px 0;
}
.issue-title {
  font-size: 50px; font-weight: 800;
  color: #f8fafc;
  line-height: 1.42;
  margin-bottom: 28px;
  letter-spacing: -1px;
  word-break: keep-all;
}
.issue-divider {
  height: 4px; width: 80px;
  border-radius: 2px;
  margin-bottom: 28px;
  flex-shrink: 0;
}
.issue-summary {
  font-size: 31px; color: #94a3b8;
  line-height: 1.9;
  letter-spacing: -0.2px;
  word-break: keep-all;
}
.issue-bottom { /* source count - 하단 고정 */
  font-size: 25px; color: #475569; font-weight: 500;
}

/* ── Trends Card ────────────────────────────────────────────── */
.layout-trends {
  justify-content: flex-start;
}
.trends-header {
  display: flex; align-items: center; gap: 18px;
  margin-bottom: 40px;
  flex-shrink: 0;
}
.trends-icon { font-size: 46px; line-height: 1; }
.trends-title { font-size: 40px; font-weight: 800; color: #f8fafc; letter-spacing: -0.5px; }
.trends-list { display: flex; flex-direction: column; gap: 26px; flex: 1; }
.trend-item {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-left: 5px solid #38bdf8;
  border-radius: 14px;
  padding: 24px 28px;
  flex: 1;
  display: flex; flex-direction: column; justify-content: center;
}
.trend-header { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.trend-icon { font-size: 32px; line-height: 1; }
.trend-keyword { font-size: 32px; font-weight: 700; color: #38bdf8; letter-spacing: -0.3px; }
.trend-desc { font-size: 28px; color: #94a3b8; line-height: 1.8; letter-spacing: -0.2px; word-break: keep-all; }
"""

CARD_JS = """
(function() {
  const params = new URLSearchParams(location.search);
  const idx = parseInt(params.get('card') || '0');
  const cards = document.querySelectorAll('.card');
  cards.forEach((c, i) => c.classList.toggle('active', i === idx));
})();
"""


def build_html(date_str: str, ko_data: dict) -> str:
    issues = ko_data.get("issues", [])[:3]
    trends = ko_data.get("trends", [])[:3]
    display_date = _fmt_date(date_str)

    has_trends = bool(trends)
    total_cards = 1 + len(issues) + (1 if has_trends else 0)

    cards_html = build_cover(issues, date_str, display_date, 0, total_cards)
    for i, issue in enumerate(issues):
        cards_html += build_issue_card(issue, i + 1, date_str, i + 1, total_cards)
    if has_trends:
        cards_html += build_trends_card(trends, date_str, 1 + len(issues), total_cards)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1080">
<title>AI 카드뉴스 {date_str}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
{CARD_CSS}
</style>
</head>
<body>
{cards_html}
<script>{CARD_JS}</script>
</body>
</html>"""


def process_date(date_str: str, entry: dict) -> int:
    """returns number of cards built, 0 if skipped."""
    structured = entry.get("structured", {})
    ko = structured.get("ko", {})
    if not ko.get("issues"):
        print(f"  skip {date_str}: structured.ko.issues 없음")
        return 0

    html = build_html(date_str, ko)
    out  = CARDNEWS_DIR / f"{date_str}.html"
    out.write_text(html, encoding="utf-8")

    issues = ko.get("issues", [])[:3]
    trends = ko.get("trends", [])[:3]
    total  = 1 + len(issues) + (1 if trends else 0)
    print(f"  + cardnews/{date_str}.html  ({total} cards)")
    return total


def update_index(entries: list[dict]) -> None:
    index = []
    for entry in entries:
        date_str   = entry.get("date", "")
        html_path  = CARDNEWS_DIR / f"{date_str}.html"
        if not html_path.exists():
            continue
        structured = entry.get("structured", {})
        ko         = structured.get("ko", {})
        issues     = ko.get("issues", [])
        trends     = ko.get("trends", [])
        total      = 1 + len(issues[:3]) + (1 if trends else 0)
        index.append({
            "date":         date_str,
            "display":      _fmt_date(date_str),
            "total_cards":  total,
            "issue_titles": [iss.get("title", "") for iss in issues[:3]],
        })

    index.sort(key=lambda x: x["date"], reverse=True)
    idx_path = CARDNEWS_DIR / "cardnews-data.json"
    idx_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  + cardnews/cardnews-data.json ({len(index)}개)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="특정 날짜 (YYYY-MM-DD)")
    parser.add_argument("--all",  action="store_true", help="전체 재빌드")
    args = parser.parse_args()

    entries: list[dict] = json.loads(REPORTS_DATA.read_text(encoding="utf-8"))

    if args.date:
        target = [e for e in entries if e.get("date") == args.date]
        if not target:
            print(f"날짜 {args.date} 데이터 없음")
            return
        for e in target:
            process_date(e["date"], e)
    elif args.all:
        for e in entries:
            process_date(e["date"], e)
    else:
        # 최신 날짜만
        for e in entries:
            date_str = e.get("date", "")
            ko = e.get("structured", {}).get("ko", {})
            if ko.get("issues"):
                process_date(date_str, e)
                break
        else:
            print("structured 데이터가 있는 항목 없음")

    update_index(entries)


if __name__ == "__main__":
    main()
