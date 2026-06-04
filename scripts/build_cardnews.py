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
ISSUE_ICONS = ["🔥", "📢", "💡"]
ISSUE_COLORS = ["#f59e0b", "#818cf8", "#34d399"]
TREND_ICONS  = ["📊", "🎯", "⚡"]


def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        return f"{dt.year}년 {dt.month}월 {dt.day}일 ({weekdays[dt.weekday()]})"
    except ValueError:
        return date_str


def _cat_label(cat: str) -> str:
    return CATEGORY_LABELS.get(cat, cat)


def _card_html(card_idx: int, total_cards: int, content_html: str, date_str: str) -> str:
    dots = "".join(
        f'<span class="dot {"active" if i == card_idx else ""}"></span>'
        for i in range(total_cards)
    )
    return f"""
<div class="card" id="card-{card_idx}">
  <div class="card-inner">
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

    content = f"""
  <div class="issue-rank-badge" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">핵심 이슈 {rank}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-title">{title}</div>
  <div class="issue-divider" style="background:{color}"></div>
  <div class="issue-summary">{summary}</div>
  <div class="issue-sources">📎 출처 {src_count}개</div>"""

    return _card_html(card_idx, total_cards, content, _fmt_date(date_str))


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
    <span class="trends-icon">📈</span>
    <span class="trends-title">주목할 트렌드 키워드</span>
  </div>
  <div class="trends-list">{trend_items}
  </div>"""

    return _card_html(card_idx, total_cards, content, _fmt_date(date_str))


CARD_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  width: 1080px;
  background: #000;
  font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
}
.card {
  width: 1080px;
  height: 1080px;
  display: none;
  flex-direction: column;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #0f2040 100%);
  position: relative;
  overflow: hidden;
}
.card.active { display: flex; }
.card::before {
  content: '';
  position: absolute;
  top: -200px; right: -200px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(56,189,248,0.15) 0%, transparent 70%);
  pointer-events: none;
}
.card::after {
  content: '';
  position: absolute;
  bottom: -150px; left: -150px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
  pointer-events: none;
}
.card-inner {
  flex: 1;
  padding: 64px 72px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  z-index: 1;
}
.card-footer {
  padding: 20px 72px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.site-tag { font-size: 22px; color: #38bdf8; font-weight: 500; }
.date-tag { font-size: 22px; color: #64748b; }
.dots { display: flex; gap: 8px; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: rgba(255,255,255,0.2); }
.dot.active { background: #38bdf8; width: 28px; border-radius: 5px; }

/* ── Cover ─────────────────────────────────────────────────── */
.cover-logo {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 40px;
}
.logo-badge {
  width: 72px; height: 72px;
  background: linear-gradient(135deg, #38bdf8, #6366f1);
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 900; color: #fff;
  letter-spacing: -1px;
}
.logo-main { font-size: 36px; font-weight: 700; color: #f8fafc; }
.logo-sub  { font-size: 22px; color: #94a3b8; margin-top: 4px; }
.cover-date {
  font-size: 28px; color: #38bdf8; font-weight: 500;
  margin-bottom: 28px;
}
.cover-divider {
  height: 2px;
  background: linear-gradient(90deg, #38bdf8 0%, transparent 100%);
  margin-bottom: 32px;
}
.cover-headline {
  font-size: 28px; color: #94a3b8; font-weight: 500;
  margin-bottom: 24px;
  text-transform: uppercase; letter-spacing: 2px;
}
.cover-issues { display: flex; flex-direction: column; gap: 20px; }
.cover-issue {
  display: flex; align-items: flex-start; gap: 16px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 16px 20px;
}
.cover-icon { font-size: 28px; flex-shrink: 0; margin-top: 2px; }
.cover-issue-text { font-size: 26px; color: #f1f5f9; font-weight: 500; line-height: 1.4; }
.cover-tags {
  margin-top: 32px;
  font-size: 22px; color: #475569;
}

/* ── Issue Card ─────────────────────────────────────────────── */
.issue-rank-badge {
  display: flex; align-items: center; gap: 14px;
  margin-bottom: 36px;
}
.rank-icon { font-size: 40px; }
.rank-label { font-size: 26px; font-weight: 700; }
.cat-badge {
  font-size: 20px; padding: 6px 16px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 20px;
  color: #cbd5e1;
  margin-left: auto;
}
.issue-title {
  font-size: 40px; font-weight: 700;
  color: #f8fafc;
  line-height: 1.35;
  margin-bottom: 28px;
}
.issue-divider {
  height: 3px; width: 80px;
  border-radius: 2px;
  margin-bottom: 28px;
}
.issue-summary {
  font-size: 27px; color: #94a3b8;
  line-height: 1.7;
  flex: 1;
}
.issue-sources {
  margin-top: 28px;
  font-size: 22px; color: #475569;
}

/* ── Trends Card ────────────────────────────────────────────── */
.trends-header {
  display: flex; align-items: center; gap: 16px;
  margin-bottom: 40px;
}
.trends-icon { font-size: 40px; }
.trends-title { font-size: 34px; font-weight: 700; color: #f8fafc; }
.trends-list { display: flex; flex-direction: column; gap: 28px; }
.trend-item {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-left: 4px solid #38bdf8;
  border-radius: 12px;
  padding: 20px 24px;
}
.trend-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.trend-icon { font-size: 28px; }
.trend-keyword { font-size: 26px; font-weight: 700; color: #38bdf8; }
.trend-desc { font-size: 23px; color: #94a3b8; line-height: 1.5; }
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
