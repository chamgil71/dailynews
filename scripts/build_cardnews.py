"""
카드뉴스 HTML 생성기 — 3채널 지원

출력 경로:
  publish/cardnews/news/YYYY-MM-DD.html     + data.json
  publish/cardnews/ai-issue/YYYY-MM-DD.html + data.json
  publish/cardnews/stock/YYYY-MM-DD.html    + data.json

각 HTML은 ?card=N 파라미터로 특정 슬라이드만 표시 (Playwright 스크린샷용)

사용법:
  python scripts/build_cardnews.py                           # 뉴스 최신
  python scripts/build_cardnews.py --type ai-issue           # AI이슈 최신
  python scripts/build_cardnews.py --type stock              # 주식 최신
  python scripts/build_cardnews.py --type news --date 2026-06-04
  python scripts/build_cardnews.py --type news --all
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

PUBLISH   = Path(_ROOT, "publish")
CARDNEWS  = PUBLISH / "cardnews"

CATEGORY_LABELS = {
    "ai_ml": "AI·ML", "technology": "기술", "economy": "경제",
    "global_news": "글로벌", "korean_news": "국내",
    "korean_economy": "한국경제", "korean_tech": "한국기술",
    "security": "보안", "startup": "스타트업",
    "model": "모델", "service": "서비스", "research": "연구",
    "policy": "정책", "industry": "산업", "infra": "인프라",
    "investment": "투자",
}

# 타입별 액센트 색상
TYPE_ACCENT = {
    "news":     "#38bdf8",   # sky
    "ai-issue": "#a78bfa",   # violet
    "stock":    "#34d399",   # emerald
}
TYPE_TOPBAR = {
    "news":     "linear-gradient(90deg,#38bdf8,#6366f1,#a78bfa)",
    "ai-issue": "linear-gradient(90deg,#a78bfa,#6366f1,#38bdf8)",
    "stock":    "linear-gradient(90deg,#34d399,#059669,#0ea5e9)",
}
TYPE_LABEL = {
    "news":     "AI News Brief",
    "ai-issue": "AI Issue Brief",
    "stock":    "Stock Brief",
}
TYPE_SUBLABEL = {
    "news":     "매일 아침 AI가 정리하는 핵심 뉴스",
    "ai-issue": "주간 AI·Tech 핵심 이슈",
    "stock":    "AI가 분석하는 시장 시황",
}

ISSUE_COLORS = ["#f59e0b", "#818cf8", "#34d399"]
ISSUE_ICONS  = ["&#128293;", "&#128226;", "&#128161;"]  # 🔥📢💡
TREND_ICONS  = ["&#128202;", "&#127919;", "&#9889;"]    # 📊🎯⚡


# ── 공통 유틸 ─────────────────────────────────────────────────────────────────
def _fmt_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        wd = ["월","화","수","목","금","토","일"][dt.weekday()]
        return f"{dt.year}년 {dt.month}월 {dt.day}일 ({wd})"
    except ValueError:
        return date_str


def _cat(cat: str) -> str:
    return CATEGORY_LABELS.get(cat, cat)


def _trunc(text: str, max_len: int) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


# ── CSS (공통) ────────────────────────────────────────────────────────────────
def _css(accent: str, topbar: str) -> str:
    return f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  width: 1080px; background: #000;
  font-family: 'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic','Noto Sans CJK KR',sans-serif;
}}
.card {{
  width: 1080px; height: 1080px;
  display: none; flex-direction: column;
  background: linear-gradient(145deg, #0a0f1e 0%, #0f172a 45%, #111f3a 100%);
  position: relative; overflow: hidden;
}}
.card.active {{ display: flex; }}
.card::before {{
  content: ''; position: absolute;
  top: -280px; right: -180px; width: 600px; height: 600px;
  background: radial-gradient(circle, {accent}20 0%, transparent 65%);
  pointer-events: none;
}}
.card::after {{
  content: ''; position: absolute;
  bottom: -200px; left: -120px; width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99,102,241,.08) 0%, transparent 65%);
  pointer-events: none;
}}
.card-topbar {{
  height: 5px; flex-shrink: 0;
  background: {topbar};
}}
.card-inner {{
  flex: 1; padding: 60px 80px 28px;
  display: flex; flex-direction: column; justify-content: flex-start;
  position: relative; z-index: 1;
}}
.card-inner.layout-issue {{ justify-content: space-between; }}
.card-inner.layout-trends {{ justify-content: flex-start; }}
.card-footer {{
  padding: 18px 80px 28px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: space-between;
  border-top: 1px solid rgba(255,255,255,.07);
  position: relative; z-index: 1;
}}
.site-tag {{ font-size: 24px; color: {accent}; font-weight: 600; }}
.date-tag {{ font-size: 24px; color: #475569; }}
.dots {{ display: flex; gap: 10px; align-items: center; }}
.dot {{ width: 11px; height: 11px; border-radius: 50%; background: rgba(255,255,255,.18); }}
.dot.active {{ background: {accent}; width: 32px; border-radius: 6px; }}

/* ── Cover ── */
.cover-logo {{ display: flex; align-items: center; gap: 22px; margin-bottom: 32px; }}
.logo-badge {{
  width: 78px; height: 78px; border-radius: 20px; flex-shrink: 0;
  background: linear-gradient(135deg, {accent}, #6366f1);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 900; color: #fff;
}}
.logo-main {{ font-size: 40px; font-weight: 800; color: #f8fafc; letter-spacing: -.5px; }}
.logo-sub  {{ font-size: 24px; color: #94a3b8; margin-top: 5px; }}
.cover-date {{ font-size: 32px; color: {accent}; font-weight: 600; margin-bottom: 22px; letter-spacing: -.3px; }}
.cover-divider {{
  height: 2px; margin-bottom: 28px;
  background: linear-gradient(90deg, {accent}cc 0%, transparent 100%);
}}
.cover-headline {{ font-size: 26px; color: #64748b; font-weight: 500; margin-bottom: 20px; letter-spacing: 3px; }}
.cover-issues {{ display: flex; flex-direction: column; gap: 16px; }}
.cover-issue {{
  display: flex; align-items: flex-start; gap: 18px;
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.09);
  border-radius: 16px; padding: 18px 24px;
}}
.cover-icon {{ font-size: 32px; flex-shrink: 0; margin-top: 2px; line-height: 1; }}
.cover-issue-text {{ font-size: 30px; color: #f1f5f9; font-weight: 600; line-height: 1.45; letter-spacing: -.3px; }}
.cover-tags {{ margin-top: 24px; font-size: 24px; color: #334155; }}

/* ── Issue Card ── */
.issue-top {{ display: flex; align-items: center; gap: 14px; }}
.rank-icon {{ font-size: 48px; line-height: 1; }}
.rank-label {{ font-size: 32px; font-weight: 700; letter-spacing: -.5px; }}
.cat-badge {{
  font-size: 24px; padding: 8px 22px;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.15);
  border-radius: 26px; color: #cbd5e1; margin-left: auto; font-weight: 500;
}}
.issue-body {{ flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 28px 0; }}
.issue-title {{
  font-size: 50px; font-weight: 800; color: #f8fafc;
  line-height: 1.42; margin-bottom: 26px; letter-spacing: -1px; word-break: keep-all;
}}
.issue-divider {{ height: 4px; width: 80px; border-radius: 2px; margin-bottom: 26px; flex-shrink: 0; }}
.issue-summary {{ font-size: 31px; color: #94a3b8; line-height: 1.9; letter-spacing: -.2px; word-break: keep-all; }}
.issue-bottom {{ font-size: 25px; color: #475569; font-weight: 500; }}
.issue-bottom a {{ color: {accent}; text-decoration: none; }}

/* ── Trends / Keywords Card ── */
.trends-header {{ display: flex; align-items: center; gap: 18px; margin-bottom: 36px; flex-shrink: 0; }}
.trends-icon {{ font-size: 46px; line-height: 1; }}
.trends-title {{ font-size: 40px; font-weight: 800; color: #f8fafc; letter-spacing: -.5px; }}
.trends-list {{ display: flex; flex-direction: column; gap: 24px; flex: 1; }}
.trend-item {{
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.09);
  border-left: 5px solid {accent}; border-radius: 14px;
  padding: 22px 26px; flex: 1; display: flex; flex-direction: column; justify-content: center;
}}
.trend-header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }}
.trend-icon {{ font-size: 30px; line-height: 1; }}
.trend-keyword {{ font-size: 30px; font-weight: 700; color: {accent}; letter-spacing: -.3px; }}
.trend-desc {{ font-size: 27px; color: #94a3b8; line-height: 1.8; letter-spacing: -.2px; word-break: keep-all; }}
"""


# ── 공통 카드 HTML 래퍼 ───────────────────────────────────────────────────────
def _card(idx: int, total: int, content: str, date_disp: str,
          layout: str = "", site_tag: str = "ms-dailynews.vercel.app") -> str:
    dots = "".join(
        f'<span class="dot {"active" if i == idx else ""}"></span>'
        for i in range(total)
    )
    cls = f"card-inner{' layout-' + layout if layout else ''}"
    return f"""
<div class="card" id="card-{idx}">
  <div class="card-topbar"></div>
  <div class="{cls}">{content}</div>
  <div class="card-footer">
    <span class="site-tag">{site_tag}</span>
    <div class="dots">{dots}</div>
    <span class="date-tag">{date_disp}</span>
  </div>
</div>"""


def _html_wrapper(title: str, accent: str, topbar: str, cards_html: str,
                  label: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=1080">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>{_css(accent, topbar)}</style>
</head><body>
{cards_html}
<script>
(function(){{
  const i=parseInt(new URLSearchParams(location.search).get('card')||'0');
  document.querySelectorAll('.card').forEach((c,j)=>c.classList.toggle('active',j===i));
}})();
</script>
</body></html>"""


# ── 뉴스 카드 빌더 ────────────────────────────────────────────────────────────
def _news_cover(issues: list[dict], date_str: str, total: int,
                accent: str) -> str:
    lines = ""
    for i, iss in enumerate(issues[:3]):
        lines += f"""
    <div class="cover-issue">
      <span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>
      <span class="cover-issue-text">{_trunc(iss.get('title',''), 34)}</span>
    </div>"""
    content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{TYPE_LABEL['news']}</div>
      <div class="logo-sub">{TYPE_SUBLABEL['news']}</div>
    </div>
  </div>
  <div class="cover-date">{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 핵심 이슈</div>
  <div class="cover-issues">{lines}</div>
  <div class="cover-tags">#AI뉴스 #테크 #데일리브리핑 #인공지능</div>"""
    return _card(0, total, content, _fmt_date(date_str))


def _news_issue(issue: dict, rank: int, date_str: str,
                idx: int, total: int) -> str:
    color = ISSUE_COLORS[rank - 1]
    icon  = ISSUE_ICONS[rank - 1]
    cat   = _cat(issue.get("category", ""))
    src   = issue.get("sources", [])
    url   = src[0].get("url", "") if src else ""
    link  = f"&nbsp;·&nbsp;<a href='{url}'>원문 보기 →</a>" if url else ""
    content = f"""
  <div class="issue-top" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">핵심 이슈 {rank}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-body">
    <div class="issue-title">{issue.get('title','')}</div>
    <div class="issue-divider" style="background:{color}"></div>
    <div class="issue-summary">{issue.get('summary','')}</div>
  </div>
  <div class="issue-bottom">&#128206; 출처 {len(src)}개{link}</div>"""
    return _card(idx, total, content, _fmt_date(date_str), layout="issue")


def _news_trends(trends: list[dict], date_str: str, idx: int, total: int,
                 accent: str) -> str:
    items = ""
    for i, t in enumerate(trends[:3]):
        items += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[i]}</span>
        <span class="trend-keyword">#{t.get('keyword','')}</span>
      </div>
      <div class="trend-desc">{_trunc(t.get('description',''), 80)}</div>
    </div>"""
    content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주목할 트렌드 키워드</span>
  </div>
  <div class="trends-list">{items}</div>"""
    return _card(idx, total, content, _fmt_date(date_str), layout="trends")


def build_news_html(date_str: str, entry: dict) -> str | None:
    ko = entry.get("structured", {}).get("ko", {})
    if not ko.get("issues"):
        return None
    issues = ko["issues"][:3]
    trends = ko.get("trends", [])[:3]
    accent = TYPE_ACCENT["news"]
    total  = 1 + len(issues) + (1 if trends else 0)
    cards  = _news_cover(issues, date_str, total, accent)
    for i, iss in enumerate(issues):
        cards += _news_issue(iss, i + 1, date_str, i + 1, total)
    if trends:
        cards += _news_trends(trends, date_str, 1 + len(issues), total, accent)
    return _html_wrapper(f"AI 뉴스 카드뉴스 {date_str}", accent,
                         TYPE_TOPBAR["news"], cards, TYPE_LABEL["news"])


# ── AI이슈 카드 빌더 ──────────────────────────────────────────────────────────
def build_ai_issue_html(date_str: str, data: dict) -> str:
    top10  = data.get("top10", [])
    top3   = top10[:3]
    accent = TYPE_ACCENT["ai-issue"]
    period = data.get("period", date_str)
    # 트렌드 대신 paper_picks or weekly_tips 사용
    extras = data.get("paper_picks", []) or data.get("weekly_tips", [])
    total  = 1 + len(top3) + (1 if extras else 0)

    # 커버
    lines = ""
    for i, item in enumerate(top3):
        lines += f"""
    <div class="cover-issue">
      <span class="cover-icon" style="color:{ISSUE_COLORS[i]}">{ISSUE_ICONS[i]}</span>
      <span class="cover-issue-text">{_trunc(item.get('title',''), 34)}</span>
    </div>"""
    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">AI</div>
    <div>
      <div class="logo-main">{TYPE_LABEL['ai-issue']}</div>
      <div class="logo-sub">{period}</div>
    </div>
  </div>
  <div class="cover-date">{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">이번 주 TOP 이슈</div>
  <div class="cover-issues">{lines}</div>
  <div class="cover-tags">#AI이슈 #테크트렌드 #인공지능 #AINews</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    # 이슈 카드
    for i, item in enumerate(top3):
        color = ISSUE_COLORS[i]
        icon  = ISSUE_ICONS[i]
        cat   = _cat(item.get("category", ""))
        srcs  = item.get("sources", [])
        url   = srcs[0].get("url", "") if srcs else ""
        link  = f"&nbsp;·&nbsp;<a href='{url}'>원문 →</a>" if url else ""
        content = f"""
  <div class="issue-top" style="color:{color}">
    <span class="rank-icon">{icon}</span>
    <span class="rank-label">TOP {item.get('rank', i+1)}</span>
    <span class="cat-badge">{cat}</span>
  </div>
  <div class="issue-body">
    <div class="issue-title">{item.get('title','')}</div>
    <div class="issue-divider" style="background:{color}"></div>
    <div class="issue-summary">{_trunc(item.get('summary',''), 120)}</div>
  </div>
  <div class="issue-bottom">&#128206; 출처 {len(srcs)}개{link}</div>"""
        cards += _card(i + 1, total, content, _fmt_date(date_str), layout="issue")

    # 추가 카드 (paper_picks / weekly_tips)
    if extras:
        items_html = ""
        for j, ex in enumerate(extras[:3]):
            tip   = ex if isinstance(ex, str) else ex.get("title", str(ex))
            items_html += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[j % 3]}</span>
        <span class="trend-keyword">{_trunc(tip, 30)}</span>
      </div>
    </div>"""
        extra_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128240;</span>
    <span class="trends-title">주목할 AI 연구·논문</span>
  </div>
  <div class="trends-list">{items_html}</div>"""
        cards += _card(1 + len(top3), total, extra_content,
                       _fmt_date(date_str), layout="trends")

    return _html_wrapper(f"AI이슈 카드뉴스 {date_str}", accent,
                         TYPE_TOPBAR["ai-issue"], cards, TYPE_LABEL["ai-issue"])


# ── 주식 카드 빌더 ────────────────────────────────────────────────────────────
def build_stock_html(date_str: str, data: dict) -> str:
    accent  = TYPE_ACCENT["stock"]
    temp    = data.get("temperature", {})
    temp_disp = temp.get("display", "")
    market  = data.get("market", {})
    summary_lines = [l.strip().lstrip("- ") for l in
                     data.get("summary", "").split("\n") if l.strip()][:3]
    keywords = data.get("keywords", [])[:4]
    total   = 2 + (1 if keywords else 0)

    # 커버: 온도계 + 시황 요약
    sum_html = ""
    for line in summary_lines:
        parts = line.split("—", 1)
        bold  = parts[0].strip() if len(parts) > 1 else ""
        rest  = parts[1].strip() if len(parts) > 1 else line
        if bold:
            sum_html += f"""
    <div class="cover-issue">
      <div>
        <div style="font-size:28px;font-weight:700;color:#f1f5f9;margin-bottom:6px">{_trunc(bold,30)}</div>
        <div style="font-size:25px;color:#94a3b8;line-height:1.5">{_trunc(rest,60)}</div>
      </div>
    </div>"""
        else:
            sum_html += f"""
    <div class="cover-issue">
      <span class="cover-issue-text">{_trunc(line, 60)}</span>
    </div>"""

    cover_content = f"""
  <div class="cover-logo">
    <div class="logo-badge">&#128200;</div>
    <div>
      <div class="logo-main">{TYPE_LABEL['stock']}</div>
      <div class="logo-sub">{TYPE_SUBLABEL['stock']}</div>
    </div>
  </div>
  <div class="cover-date" style="font-size:36px">{temp_disp}&nbsp;&nbsp;{_fmt_date(date_str)}</div>
  <div class="cover-divider"></div>
  <div class="cover-headline">오늘의 시황 요약</div>
  <div class="cover-issues">{sum_html}</div>
  <div class="cover-tags">#주식 #시황 #코스피 #투자</div>"""
    cards = _card(0, total, cover_content, _fmt_date(date_str))

    # 시장 지표 카드
    def _idx(key: str, label: str, sub_key: str = "") -> str:
        info = market.get(key, {})
        if not info:
            return ""
        close = info.get("close_str", "")
        chg   = info.get("chg_str", "")
        return f"""
    <div class="trend-item" style="border-left-color:{accent}">
      <div class="trend-header" style="margin-bottom:8px">
        <span class="trend-keyword" style="font-size:28px">{label}</span>
        <span style="font-size:26px;color:#f8fafc;font-weight:700;margin-left:auto">{close}</span>
      </div>
      <div class="trend-desc" style="font-size:24px">{chg}</div>
    </div>"""

    mkt_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128200;</span>
    <span class="trends-title">주요 시장 지표</span>
  </div>
  <div class="trends-list">
    {_idx('kospi',   '코스피')}
    {_idx('kosdaq',  '코스닥')}
    {_idx('usd_krw', 'USD/KRW')}
    {_idx('wti',     'WTI')}
  </div>"""
    cards += _card(1, total, mkt_content, _fmt_date(date_str), layout="trends")

    # 키워드 카드
    if keywords:
        kw_items = ""
        for j, kw in enumerate(keywords[:3]):
            title = kw.get("title", "") if isinstance(kw, dict) else str(kw)
            body  = kw.get("body",  "") if isinstance(kw, dict) else ""
            kw_items += f"""
    <div class="trend-item">
      <div class="trend-header">
        <span class="trend-icon">{TREND_ICONS[j % 3]}</span>
        <span class="trend-keyword">{_trunc(title, 22)}</span>
      </div>
      <div class="trend-desc">{_trunc(body, 80)}</div>
    </div>"""
        kw_content = f"""
  <div class="trends-header">
    <span class="trends-icon">&#128269;</span>
    <span class="trends-title">핵심 키워드</span>
  </div>
  <div class="trends-list">{kw_items}</div>"""
        cards += _card(2, total, kw_content, _fmt_date(date_str), layout="trends")

    return _html_wrapper(f"주식 카드뉴스 {date_str}", accent,
                         TYPE_TOPBAR["stock"], cards, TYPE_LABEL["stock"])


# ── 인덱스 업데이트 ───────────────────────────────────────────────────────────
def _update_index(type_dir: Path, channel: str) -> None:
    index = []
    for html in sorted(type_dir.glob("[0-9][0-9][0-9][0-9]-??-??.html"), reverse=True):
        date_str = html.stem
        index.append({
            "date":    date_str,
            "display": _fmt_date(date_str),
            "type":    channel,
            "html":    f"cardnews/{channel}/{date_str}.html",
        })
    (type_dir / "data.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  + cardnews/{channel}/data.json ({len(index)}개)")


# ── 메인 빌드 함수 ────────────────────────────────────────────────────────────
def build_news(date_str: str | None = None, rebuild_all: bool = False) -> None:
    out_dir = CARDNEWS / "news"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = json.loads((PUBLISH / "news" / "data.json").read_text(encoding="utf-8"))
    if date_str:
        entries = [e for e in entries if e.get("date") == date_str]
    elif not rebuild_all:
        entries = [e for e in entries
                   if e.get("structured", {}).get("ko", {}).get("issues")][:1]

    built = 0
    for e in entries:
        d = e.get("date", "")
        html = build_news_html(d, e)
        if not html:
            print(f"  skip {d}: structured 데이터 없음")
            continue
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        ko = e.get("structured", {}).get("ko", {})
        n  = 1 + len(ko.get("issues", [])[:3]) + (1 if ko.get("trends") else 0)
        print(f"  + cardnews/news/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "news")


def build_ai_issue(date_str: str | None = None, rebuild_all: bool = False) -> None:
    import glob as _glob
    out_dir = CARDNEWS / "ai-issue"
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(_glob.glob(str(PUBLISH / "ai-issue" / "[0-9][0-9][0-9][0-9]-??-??.json")),
                   reverse=True)
    if date_str:
        files = [f for f in files if Path(f).stem == date_str]
    elif not rebuild_all:
        files = files[:1]

    built = 0
    for fp in files:
        d    = Path(fp).stem
        data = json.loads(Path(fp).read_text(encoding="utf-8"))
        html = build_ai_issue_html(d, data)
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        n = 1 + min(3, len(data.get("top10", []))) + (1 if data.get("paper_picks") or data.get("weekly_tips") else 0)
        print(f"  + cardnews/ai-issue/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "ai-issue")


def build_stock(date_str: str | None = None, rebuild_all: bool = False) -> None:
    out_dir = CARDNEWS / "stock"
    out_dir.mkdir(parents=True, exist_ok=True)

    stock_path = PUBLISH / "stock" / "data.json"
    if not stock_path.exists():
        print("  stock-data.json 없음")
        return

    entries = json.loads(stock_path.read_text(encoding="utf-8"))
    entries.sort(key=lambda x: x.get("date", ""), reverse=True)

    if date_str:
        entries = [e for e in entries if e.get("date") == date_str]
    elif not rebuild_all:
        entries = entries[:1]

    built = 0
    for e in entries:
        d    = e.get("date", "")
        html = build_stock_html(d, e)
        (out_dir / f"{d}.html").write_text(html, encoding="utf-8")
        n = 2 + (1 if e.get("keywords") else 0)
        print(f"  + cardnews/stock/{d}.html  ({n} cards)")
        built += 1

    if built:
        _update_index(out_dir, "stock")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="카드뉴스 HTML 빌드")
    parser.add_argument("--type",  choices=["news","ai-issue","stock","all"],
                        default="news", help="채널 (기본: news)")
    parser.add_argument("--date",  help="YYYY-MM-DD (미입력 시 최신)")
    parser.add_argument("--all",   action="store_true", help="전체 날짜 재빌드")
    args = parser.parse_args()

    channels = ["news","ai-issue","stock"] if args.type == "all" else [args.type]
    print(f"[build-cardnews] type={args.type}  date={args.date or '최신'}  all={args.all}")

    for ch in channels:
        if ch == "news":
            build_news(args.date, args.all)
        elif ch == "ai-issue":
            build_ai_issue(args.date, args.all)
        elif ch == "stock":
            build_stock(args.date, args.all)


if __name__ == "__main__":
    main()
