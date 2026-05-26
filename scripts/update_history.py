# scripts/update_history.py
"""
티커별 일별 종가 누적 이력 관리.

- 신규 파일   : templates/stock_history.md 기반으로 초기화
- 레거시 파일 : 단순 가격 테이블 → 새 템플릿 형식으로 자동 마이그레이션
- 기존 신규 형식 : 가격 이력 테이블만 업데이트 (동향·이슈 섹션은 루틴이 처리)

마커 규칙:
  <!-- PRICE_TABLE_END -->   : 가격 테이블 행 삽입 위치 (이 마커 바로 위)
  <!-- ISSUES_TOP --> : 루틴이 동향 이슈 항목을 프리펜드하는 위치

실행:
  python scripts/update_history.py              # 오늘 날짜, yfinance 수집
  python scripts/update_history.py --date 2026-05-18
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

_HISTORY_DIR  = Path(__file__).parent.parent / "reports" / "history"
_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "stock_history.md"
_MAX_ROWS = 365

# ── 거래소 매핑 (US 주요 종목) ────────────────────────────────────────────────
_NYSE_TICKERS   = {"TSM", "VST", "LMT", "RTX", "LLY", "NVO", "JPM", "BRK-B", "CEG"}
_OTC_TICKERS    = {"FANUY"}


# ── 유틸 ──────────────────────────────────────────────────────────────────────

def _safe_name(ticker: str) -> str:
    """파일명에 사용 가능한 티커명 변환 (/ → _, ^ 제거)."""
    return ticker.replace("/", "_").replace("^", "")


def _is_new_format(content: str) -> bool:
    """새 템플릿 형식 여부 — PRICE_TABLE_END 마커 존재 여부로 판단."""
    return "<!-- PRICE_TABLE_END -->" in content


def _get_exchange(ticker: str, market: str) -> str:
    """거래소 문자열 결정."""
    if market == "KR":
        return "KOSDAQ" if ".KQ" in ticker else "KOSPI"
    if ticker in _NYSE_TICKERS:
        return "NYSE"
    if ticker in _OTC_TICKERS:
        return "OTC"
    return "NASDAQ"


def _get_links(ticker: str, market: str) -> str:
    """국내/해외 관련 링크 생성."""
    if market == "KR":
        code = re.sub(r"\.(KS|KQ)$", "", ticker)
        return (
            f"- [네이버금융](https://finance.naver.com/item/main.naver?code={code})\n"
            f"- [KRX 공시](http://kind.krx.co.kr/)\n"
            f"- [DART 전자공시](https://dart.fss.or.kr/)"
        )
    return (
        f"- [Yahoo Finance](https://finance.yahoo.com/quote/{ticker})\n"
        f"- [SEC Edgar](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker})"
    )


# ── 파일 초기화 / 마이그레이션 ──────────────────────────────────────────────

def _render_template(ticker: str, name: str, market: str, sector: str, today: str) -> str:
    """templates/stock_history.md 로드 후 변수 치환. 파일 없으면 인라인 폴백 사용."""
    content = (
        _TEMPLATE_PATH.read_text(encoding="utf-8")
        if _TEMPLATE_PATH.exists()
        else _INLINE_TEMPLATE
    )
    country  = "KR" if market == "KR" else "US"
    exchange = _get_exchange(ticker, market)
    links    = _get_links(ticker, market)

    for k, v in {
        "{{ticker}}":   ticker,
        "{{name}}":     name,
        "{{exchange}}": exchange,
        "{{country}}":  country,
        "{{sector}}":   sector,
        "{{market}}":   market,
        "{{created}}":  today,
        "{{modified}}": today,
        "{{links}}":    links,
    }.items():
        content = content.replace(k, v)
    return content


def _migrate_legacy(
    content: str, ticker: str, name: str, market: str, sector: str, today: str
) -> str:
    """
    레거시(단순 가격 테이블) 형식 → 새 템플릿 형식 마이그레이션.
    기존 가격 행은 새 템플릿의 가격 이력 섹션에 보존한다.
    """
    existing_rows = re.findall(r"^\| 20\d\d-\d\d-\d\d \|.*$", content, re.MULTILINE)

    new_content = _render_template(ticker, name, market, sector, today)

    if existing_rows:
        rows_str = "\n".join(sorted(set(existing_rows))[-_MAX_ROWS:])
        new_content = new_content.replace(
            "<!-- PRICE_TABLE_END -->",
            rows_str + "\n<!-- PRICE_TABLE_END -->",
        )

    logger.info(f"  [{ticker}] 마이그레이션 완료 — 기존 {len(existing_rows)}행 보존")
    return new_content


# ── 가격 테이블 업데이트 ─────────────────────────────────────────────────────

def _update_price_table(content: str, today: str, price: float, chg: float) -> str:
    """
    가격 이력 테이블에 오늘 행을 추가/덮어씀.
    1) 전체 콘텐츠에서 날짜형 테이블 행(| 20xx-…) 추출
    2) 오늘 날짜 행 제거 → 새 행 추가 → 정렬 → 365행 제한
    3) 기존 행 모두 제거 후 지정 위치에 재삽입
    """
    new_row = f"| {today} | {price:,.2f} | {chg:+.2f}% | |"

    # 기존 행 수집 후 오늘 것 교체
    rows = re.findall(r"^\| 20\d\d-\d\d-\d\d \|.*$", content, re.MULTILINE)
    rows = [r for r in rows if not r.startswith(f"| {today} ")]
    rows.append(new_row)
    rows = sorted(rows)[-_MAX_ROWS:]

    # 기존 행 전부 제거
    content = re.sub(r"^\| 20\d\d-\d\d-\d\d \|.*\n?", "", content, flags=re.MULTILINE)

    # 삽입: 새 형식 → PRICE_TABLE_END 마커 앞, 레거시 → 구분선 뒤
    if "<!-- PRICE_TABLE_END -->" in content:
        content = content.replace(
            "<!-- PRICE_TABLE_END -->",
            "\n".join(rows) + "\n<!-- PRICE_TABLE_END -->",
        )
    else:
        sep = "|------|-----:|-------:|------|"
        if sep in content:
            content = content.replace(sep, sep + "\n" + "\n".join(rows), 1)
        else:
            content += "\n" + "\n".join(rows) + "\n"

    return content


# ── 진입점 ────────────────────────────────────────────────────────────────────

def update_ticker_md(
    ticker: str,
    name: str,
    market: str,
    sector: str,
    entry: dict,
) -> None:
    """
    단일 티커 이력 파일 업데이트.

    entry: {"date": "2026-05-26", "price": 224.59, "change_pct": 1.38}

    처리 흐름:
      - 파일 없음      → 새 템플릿으로 초기화
      - 레거시 형식    → 새 템플릿으로 마이그레이션 (기존 가격 보존)
      - 새 형식        → 가격 테이블만 업데이트
                         (동향·이슈 섹션은 루틴이 별도 처리)
    """
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = _HISTORY_DIR / f"{_safe_name(ticker)}.md"

    today = entry["date"]
    price = entry.get("price") or 0.0
    chg   = entry.get("change_pct") or 0.0

    if not path.exists():
        content = _render_template(ticker, name, market, sector, today)
        logger.info(f"  [{ticker}] 새 파일 생성")
    else:
        content = path.read_text(encoding="utf-8")
        if not _is_new_format(content):
            content = _migrate_legacy(content, ticker, name, market, sector, today)

    # 가격 테이블 업데이트
    content = _update_price_table(content, today, price, chg)

    # frontmatter modified 갱신
    content = re.sub(
        r'^modified: "[\d-]+"',
        f'modified: "{today}"',
        content,
        flags=re.MULTILINE,
    )

    path.write_text(content, encoding="utf-8")

    row_count = len(re.findall(r"^\| 20", content, re.MULTILINE))
    logger.info(f"  [{ticker}] 저장 완료 — 가격 이력 {row_count}행")


def run(date_str: str | None = None) -> int:
    """watchlist.yaml 기반 전체 티커 이력 업데이트. 갱신된 티커 수 반환."""
    from config.watchlist import get_all_tickers
    from core.stock.collector import _fetch_ticker

    today   = date_str or datetime.now().strftime("%Y-%m-%d")
    tickers = get_all_tickers()
    logger.info(f"[update_history] {today} — {len(tickers)}개 티커 처리 시작")

    ok_count = 0
    for t in tickers:
        raw = _fetch_ticker(t["ticker"])
        if raw["close"] is None:
            logger.warning(f"  [skip] {t['ticker']}: 데이터 없음")
            continue
        update_ticker_md(
            ticker  = t["ticker"],
            name    = t["name"],
            market  = t["market"],
            sector  = t["sector"],
            entry   = {
                "date":       today,
                "price":      raw["close"],
                "change_pct": raw["change_pct"] or 0.0,
            },
        )
        ok_count += 1

    logger.info(f"[update_history] 완료 — {ok_count}/{len(tickers)}개 갱신")
    return ok_count


# ── 인라인 폴백 템플릿 (templates/stock_history.md 없을 때) ─────────────────
_INLINE_TEMPLATE = """\
---
publish: false
tags:
  - 종목분석
ticker: "{{ticker}}"
종목명: "{{name}}"
exchange: "{{exchange}}"
country: "{{country}}"
sector: "{{sector}}"
market: "{{market}}"
상태: "관심"
created: "{{created}}"
modified: "{{modified}}"
---

# {{name}} ({{ticker}})

## 📊 기본 정보

| 항목 | 내용 |
|------|------|
| 티커 | `{{ticker}}` |
| 거래소 | {{exchange}} |
| 국가 | {{country}} |
| GICS 섹터 | {{sector}} |
| 주요사업 | |
| 상태 | 관심 |

## 🎯 투자 포인트

### 강점
-

### 리스크
-

## 📈 주요 테마

- **핵심 테마**:
- **연관 테마**:

## 🔗 연관 기업

### 상위 기업 (고객사 / 대주주 / 플랫폼)
-

### 하위 기업 (공급업체 / 자회사 / 파트너)
-

### 경쟁 기업
-

---

## 📰 동향 및 이슈

> 루틴이 매일 자동 추가 (최신 항목이 위). 수동 메모도 마커 위에 작성 가능.

<!-- ISSUES_TOP -->

---

## 📈 가격 이력

| 날짜 | 종가 | 등락률 | 메모 |
|------|-----:|-------:|------|
<!-- PRICE_TABLE_END -->

---

## 💰 재무 정보

> 기준: 최근 분기

| 지표 | 값 | 비고 |
|------|----|------|
| 매출액 | | |
| 영업이익 | | |
| 영업이익률 | | |
| PER | | |
| PBR | | |
| ROE | | |
| 부채비율 | | |

---

## 🎯 개인 메모

### 매수/매도 기준
- **목표가**:
- **손절가**:
- **매도 조건**:

### 체크포인트
- [ ] 분기 실적 확인
- [ ] 주요 뉴스 모니터링
- [ ] 테마 동향 점검
- [ ] 연관 기업 동향 점검
- [ ] 환율/금리 영향 점검

---

## 🔗 관련 링크

{{links}}

---

## 연결된 노트

- [[{{sector}}]]
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="티커 이력 업데이트")
    parser.add_argument("--date", default=None, help="날짜 (YYYY-MM-DD, 기본: 오늘)")
    args = parser.parse_args()
    run(args.date)
