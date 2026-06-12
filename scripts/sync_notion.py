"""
Notion 데이터베이스 동기화 독립 스크립트.

사용법:
  python scripts/sync_notion.py --type news  [--date 2026-05-27]
  python scripts/sync_notion.py --type stock [--date 2026-05-27]
  python scripts/sync_notion.py --type ai-issue [--date 2026-06-01]

GitHub Actions에서 이메일·텔레그램과 동일하게 별도 스텝으로 실행.
환경변수: NOTION_API_KEY, NOTION_DATABASE_ID_NEWS, NOTION_DATABASE_ID_STOCK,
          NOTION_DATABASE_ID_AI_ISSUE
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sync_notion")

_REPORTS_DIR = Path(_ROOT) / "reports"


# ──────────────────────────────────────────────
# 뉴스 동기화
# ──────────────────────────────────────────────

def sync_news(date_str: str) -> int:
    """publish/news/YYYY-MM-DD.json → Notion 뉴스 DB

    뉴스 리스트(news_en + news_ko)는 reports/news_*.json이 아닌
    publish/news/*.json에 저장됨. 각 항목: label, title, link, summary
    """
    _PUBLISH_NEWS_DIR = Path(_ROOT) / "publish" / "news"
    json_path = _PUBLISH_NEWS_DIR / f"{date_str}.json"

    if not json_path.exists():
        logger.error(f"[뉴스] 파일 없음: {json_path}")
        return 0

    data = json.loads(json_path.read_text(encoding="utf-8"))
    news_en = data.get("news_en", [])
    news_ko = data.get("news_ko", [])
    news_items = news_en + news_ko

    if not news_items:
        logger.warning(f"[뉴스] {date_str} 동기화할 기사 없음.")
        return 0

    logger.info(f"[뉴스] {date_str} — EN:{len(news_en)}건 + KO:{len(news_ko)}건 = {len(news_items)}건 동기화 시작")
    from core.shared.notion import sync_news_to_notion
    count = sync_news_to_notion(news_items, date_str)
    logger.info(f"[뉴스] {date_str} → Notion {count}건 완료")
    return count


# ──────────────────────────────────────────────
# 주식 동기화
# ──────────────────────────────────────────────

def _parse_stock_md(md_path: Path) -> tuple[str, dict, str]:
    """stock_YYYY-MM-DD.md에서 핵심 키워드(Summary용)·주요 지표·시장온도 파싱"""
    text = md_path.read_text(encoding="utf-8")

    # ── Summary: 핵심 키워드 TOP 5 섹션에서 [키워드] 설명 형식으로 추출 ──
    # 형식 A: "① 키워드: 설명 1~2문장"  (루틴 의도 형식)
    # 형식 B: "#키워드1 #키워드2 ..."    (현재 실제 생성 형식)
    summary = ""
    kw_section = ""
    kw_m = re.search(r"##\s*3\.\s*핵심 키워드[^\n]*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if kw_m:
        kw_section = kw_m.group(1).strip()

    if kw_section:
        # 형식 A: ① 키워드: 설명
        described = re.findall(r"[①②③④⑤]\s*([^:\n：]+)[：:]\s*(.+)", kw_section)
        if described:
            summary = "\n".join(f"[{kw.strip()}] {desc.strip()}" for kw, desc in described[:5])
        else:
            # 형식 B: #해시태그 나열
            tags = re.findall(r"#([\w가-힣]+)", kw_section)
            if tags:
                summary = "\n".join(f"[{tag}]" for tag in tags[:5])

    # 주요 지표 파싱 (테이블에서 수치 추출)
    market_data = {}
    patterns = {
        "kospi":         r"코스피\s*\|\s*([\d,\.]+)",
        "kosdaq":        r"코스닥\s*\|\s*([\d,\.]+)",
        "exchange_rate": r"원/달러\s*\|\s*([\d,\.]+)",
        "sp500":         r"S&P\s*500\s*\|\s*([\d,\.]+)",
        "nasdaq":        r"나스닥\s*\|\s*([\d,\.]+)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text)
        if m:
            try:
                market_data[key] = float(m.group(1).replace(",", ""))
            except ValueError:
                pass

    # 시장 온도계 파싱: "## 시장 온도계: 🟠 상승"
    temperature = ""
    temp_m = re.search(r"##\s*시장 온도계[:\s]*(🔴 과열|🟠 상승|🟡 중립|🟢 하락|🔵 침체)", text)
    if temp_m:
        temperature = temp_m.group(1).strip()

    return summary, market_data, temperature


def sync_stock(date_str: str) -> bool:
    """reports/stock/stock_YYYY-MM-DD.md → Notion 주식 DB"""
    md_path = _REPORTS_DIR / "stock" / f"stock_{date_str}.md"
    if not md_path.exists():
        logger.error(f"[주식] 파일 없음: {md_path}")
        return False

    summary, market_data, temperature = _parse_stock_md(md_path)
    logger.info(f"[주식] 파싱 결과 — 요약:{bool(summary)}, 코스피:{market_data.get('kospi')}, 온도:{temperature or '없음'}")

    from core.shared.notion import sync_stock_to_notion
    ok = sync_stock_to_notion(date_str, summary, market_data, temperature)
    logger.info(f"[주식] {date_str} → Notion {'완료' if ok else '실패'}")
    return ok


# ──────────────────────────────────────────────
# AI Issue 동기화
# ──────────────────────────────────────────────

def sync_ai_issue(date_str: str) -> int:
    """reports/ai-issue/ai_issue_YYYY-MM-DD.json → Notion AI Issue DB"""
    json_path = _REPORTS_DIR / "ai-issue" / f"ai_issue_{date_str}.json"
    if not json_path.exists():
        logger.error(f"[AI이슈] 파일 없음: {json_path}")
        return 0

    data = json.loads(json_path.read_text(encoding="utf-8"))
    top10   = data.get("top10", [])
    period  = data.get("period", "")
    outlook = data.get("next_week_outlook", "")

    from core.shared.notion import sync_ai_issue_to_notion
    count = sync_ai_issue_to_notion(date_str, period, top10, outlook)
    logger.info(f"[AI이슈] {date_str} → Notion {count}건 완료")
    return count


# ──────────────────────────────────────────────
# CLI 진입점
# ──────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Notion DB 동기화")
    parser.add_argument(
        "--type", required=True,
        choices=["news", "stock", "ai-issue"],
        help="동기화 대상 유형"
    )
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="대상 날짜 (기본: 오늘, 형식: YYYY-MM-DD)"
    )
    args = parser.parse_args()

    logger.info(f"Notion 동기화 시작: type={args.type}, date={args.date}")

    if args.type == "news":
        count = sync_news(args.date)
        sys.exit(0 if count >= 0 else 1)

    elif args.type == "stock":
        ok = sync_stock(args.date)
        sys.exit(0 if ok else 1)

    elif args.type == "ai-issue":
        count = sync_ai_issue(args.date)
        sys.exit(0 if count >= 0 else 1)


if __name__ == "__main__":
    main()
