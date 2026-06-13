"""
주식 루틴 v6 + 주간 루틴 변경사항 검증 테스트

실행: python tests/test_stock_v6.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.build_stock_site import _parse_sectors, parse_stock_md
from scripts.build_cardnews import build_stock_html

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
_failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  {PASS}  {name}")
    else:
        msg = f"{name}" + (f" — {detail}" if detail else "")
        print(f"  {FAIL}  {msg}")
        _failures.append(msg)


# ─────────────────────────────────────────────────────────────
# 1. _parse_sectors: v6 형식 (### 2-1. 섹터 요약 9행)
# ─────────────────────────────────────────────────────────────
print("\n[1] _parse_sectors — v6 3-테이블 형식")

V6_MD = """
## 2. 섹터 동향

### 2-1. 섹터 요약 (카드뉴스용)

| 섹터 | 대표종목 | 현재가 | 등락 |
|---|---|---|---|
| 반도체 | 삼성전자 | 75,400 | +1.2% ▲ |
| AI/빅테크 | 알파벳 | 175.2 | +0.8% ▲ |
| 전력인프라 | HD현대일렉트릭 | 382,000 | +0.5% ▲ |
| 원전/SMR | 두산에너빌리티 | 45,000 | +1.1% ▲ |
| 방산 | 한화에어로스페이스 | 520,000 | +1.8% ▲ |
| 우주 | 한국항공우주 | 68,000 | +0.9% ▲ |
| 로봇 | 레인보우로보틱스 | 180,000 | -0.4% ▼ |
| 바이오 | 삼성바이오로직스 | 1,050,000 | +0.3% ▲ |
| 금융 | 우리은행 | 17,500 | +0.2% ▲ |

### 2-2. 국내 상세

| 섹터 | 종목 | 현재가 | 등락 |
|---|---|---|---|
| 반도체 | 삼성전자 | 75,400 | +1.2% ▲ |
| 반도체 | SK하이닉스 | 215,000 | +1.5% ▲ |

### 2-3. 해외 상세

| 섹터 | 종목 | 현재가 | 등락 |
|---|---|---|---|
| 반도체 | 엔비디아 | 1,120.5 | +2.1% ▲ |

## 3. 핵심 키워드
"""

s_v6 = _parse_sectors(V6_MD)
check("9개 섹터 파싱", len(s_v6) == 9, f"실제: {len(s_v6)}")
check("첫 번째 섹터명", s_v6[0]["sector"] == "반도체", s_v6[0]["sector"])
check("마지막 섹터명", s_v6[-1]["sector"] == "금융", s_v6[-1]["sector"])
check("2-2/2-3 미포함 (SK하이닉스 없음)", all(r["name"] != "SK하이닉스" for r in s_v6))
check("2-2/2-3 미포함 (엔비디아 없음)", all(r["name"] != "엔비디아" for r in s_v6))
check("필드 키 완전성", all({"sector","name","price","change"} == set(r.keys()) for r in s_v6))


# ─────────────────────────────────────────────────────────────
# 2. _parse_sectors: 구 flat 형식 (## 2. 섹터 동향 단일 테이블)
# ─────────────────────────────────────────────────────────────
print("\n[2] _parse_sectors — 구 flat 형식 (하위 호환)")

OLD_MD = """
## 2. 섹터 동향

| 섹터 | 대표종목 | 현재가 | 등락 |
|---|---|---|---|
| 반도체 | 삼성전자 | 322,500원 | -1.07% ▼ |
| AI/빅테크 | 엔비디아 | $205.19 | +0.16% ▲ |
| 전력인프라 | HD현대일렉트릭 | 1,130,000원 | +2.08% ▲ |
| 방산/우주 | 한화에어로스페이스 | 1,078,000원 | +4.15% ▲ |
| 로봇 | 인튜이티브서지컬 | $411.06 | -0.95% ▼ |
| 바이오 | 일라이릴리 | $1,133.00 | -2.75% ▼ |
| 금융 | KB금융 | 161,200원 | +3.33% ▲ |

---
"""

s_old = _parse_sectors(OLD_MD)
check("7개 섹터 파싱", len(s_old) == 7, f"실제: {len(s_old)}")
check("첫 번째 섹터명", s_old[0]["sector"] == "반도체", s_old[0]["sector"])
check("sector 필드 빈값 없음", all(r["sector"] for r in s_old))
check("헤더행 제외", all(r["sector"] != "섹터" for r in s_old))
check("구분자행 제외", all("---" not in r["sector"] for r in s_old))


# ─────────────────────────────────────────────────────────────
# 3. _parse_sectors: SPCX '-' 데이터 (에러 없이 통과)
# ─────────────────────────────────────────────────────────────
print("\n[3] _parse_sectors — SPCX '-' 데이터")

SPCX_MD = """
## 2. 섹터 동향

### 2-1. 섹터 요약 (카드뉴스용)

| 섹터 | 대표종목 | 현재가 | 등락 |
|---|---|---|---|
| 우주 | 스페이스X | - | - |
| 방산 | 한화에어로스페이스 | 520,000 | +1.8% ▲ |
"""

try:
    s_spcx = _parse_sectors(SPCX_MD)
    check("에러 없이 파싱", True)
    check("SPCX price='-'", s_spcx[0]["price"] == "-", s_spcx[0]["price"])
    check("SPCX change='-'", s_spcx[0]["change"] == "-", s_spcx[0]["change"])
    check("다음 섹터 정상", s_spcx[1]["sector"] == "방산")
except Exception as e:
    check("에러 없이 파싱", False, str(e))


# ─────────────────────────────────────────────────────────────
# 4. _parse_sectors: 섹터 테이블 없는 MD → 빈 리스트
# ─────────────────────────────────────────────────────────────
print("\n[4] _parse_sectors — 섹터 테이블 없는 MD (빈 리스트)")

NO_SECTOR_MD = """
# 📊 일일 주식 시황

## 1. 주요 지수
| 코스피 | 2650 | +0.8% |

## 3. 핵심 키워드
"""

s_none = _parse_sectors(NO_SECTOR_MD)
check("빈 리스트 반환", s_none == [], f"실제: {s_none}")


# ─────────────────────────────────────────────────────────────
# 5. parse_stock_md: 실제 MD 파일 — sectors 필드 포함
# ─────────────────────────────────────────────────────────────
print("\n[5] parse_stock_md — 실제 MD 파일 sectors 필드")

real_mds = sorted(Path("reports/stock").glob("stock_*.md"), reverse=True)
check("실제 MD 파일 존재", bool(real_mds), "reports/stock/에 stock_*.md 없음")

if real_mds:
    latest_md = real_mds[0]
    date_str = latest_md.stem.replace("stock_", "")
    data = parse_stock_md(str(latest_md), date_str)

    check("sectors 키 존재", "sectors" in data)
    check("date 일치", data["date"] == date_str)
    check("temperature 존재", bool(data.get("temperature", {}).get("display")))
    check("market 존재", bool(data.get("market")))

    sectors = data["sectors"]
    check("sectors는 리스트", isinstance(sectors, list))
    if sectors:
        check("sector 필드 존재", all("sector" in r for r in sectors))
        check("name 필드 존재", all("name" in r for r in sectors))
        check("sector 빈값 없음", all(r["sector"] for r in sectors))


# ─────────────────────────────────────────────────────────────
# 6. build_stock_html: sectors 있을 때 4장, 없을 때 3장
# ─────────────────────────────────────────────────────────────
print("\n[6] build_stock_html — 카드 수")

BASE_DATA = {
    "date": "2026-06-13",
    "temperature": {"display": "🟠 상승", "level": "rising"},
    "market": {
        "kospi":   {"close_str": "2,650", "chg_str": "+0.8% ▲"},
        "kosdaq":  {"close_str": "850",   "chg_str": "-0.3% ▼"},
        "usd_krw": {"close_str": "1,380", "chg_str": "-0.1%"},
        "wti":     {"close_str": "78.4",  "chg_str": "-0.7%"},
    },
    "summary": "라인 1\n라인 2\n라인 3",
    "keywords": [{"title": "반도체", "body": "상승 주도"}],
}

# 4장: sectors 있음
data_with = {**BASE_DATA, "sectors": [
    {"sector": "반도체", "name": "삼성전자", "price": "75,400", "change": "+1.2% ▲"},
    {"sector": "바이오", "name": "삼성바이오", "price": "1,050,000", "change": "-0.3% ▼"},
]}
html_with = build_stock_html("2026-06-13", data_with)
cards_with = re.findall(r'id="card-\d+"', html_with)
check("sectors 있을 때 4장", len(cards_with) == 4, f"실제: {len(cards_with)}")
check("섹터 동향 텍스트 포함", "섹터 동향" in html_with)

# 3장: sectors 없음 (하위 호환)
data_without = {**BASE_DATA, "sectors": []}
html_without = build_stock_html("2026-06-13", data_without)
cards_without = re.findall(r'id="card-\d+"', html_without)
check("sectors 없을 때 3장", len(cards_without) == 3, f"실제: {len(cards_without)}")
check("섹터 동향 텍스트 미포함", "섹터 동향" not in html_without)

# sectors 키 자체 없는 경우 (구 data.json 호환)
data_nokey = {k: v for k, v in BASE_DATA.items()}  # sectors 키 없음
html_nokey = build_stock_html("2026-06-13", data_nokey)
cards_nokey = re.findall(r'id="card-\d+"', html_nokey)
check("sectors 키 없어도 3장 (구 data.json 호환)", len(cards_nokey) == 3, f"실제: {len(cards_nokey)}")


# ─────────────────────────────────────────────────────────────
# 7. build_stock_html: 섹터 색상 코딩 (▲=green, ▼=red)
# ─────────────────────────────────────────────────────────────
print("\n[7] build_stock_html — 섹터 색상 코딩")

data_color = {**BASE_DATA, "sectors": [
    {"sector": "반도체", "name": "삼성전자", "price": "75,400", "change": "+1.2% ▲"},
    {"sector": "바이오", "name": "일라이릴리", "price": "850.0", "change": "-2.1% ▼"},
    {"sector": "금융", "name": "JP모건", "price": "245.0", "change": "0.0%"},
]}
html_color = build_stock_html("2026-06-13", data_color)
check("상승(▲) → green(#34d399)", "#34d399" in html_color)
check("하락(▼) → red(#f87171)", "#f87171" in html_color)
check("보합 → gray(#94a3b8)", "#94a3b8" in html_color)


# ─────────────────────────────────────────────────────────────
# 8. weekly_*.md → build_stock_site.py glob 제외
# ─────────────────────────────────────────────────────────────
print("\n[8] weekly_*.md — stock 빌드에서 제외")

import glob as _glob
weekly_files = _glob.glob("reports/stock/weekly_*.md")
stock_files  = _glob.glob("reports/stock/stock_*.md")
check("weekly_*.md glob 패턴 stock과 분리", not any(f in stock_files for f in weekly_files))

# stock_build.yml 트리거 패턴 확인
yml = Path(".github/workflows/stock_build.yml").read_text(encoding="utf-8")
check("stock_build.yml 트리거가 stock_*.md만", "stock_*.md" in yml and "**.md" not in yml)
# paths 블록에서 실제 트리거 패턴만 추출 (주석 제외)
paths_block = re.search(r'paths:\s*\n((?:\s+-[^\n]+\n)+)', yml)
trigger_paths = []
if paths_block:
    for line in paths_block.group(1).splitlines():
        line = line.strip().lstrip("- ").split("#")[0].strip().strip("'\"")
        if line:
            trigger_paths.append(line)
check(
    "paths 트리거에 weekly_*.md 없음 (주석 제외)",
    not any("weekly" in p for p in trigger_paths),
    f"실제 트리거: {trigger_paths}",
)


# ─────────────────────────────────────────────────────────────
# 9. data.json 전체 구조 검증
# ─────────────────────────────────────────────────────────────
print("\n[9] data.json 전체 구조")

dj_path = Path("publish/stock/data.json")
check("data.json 존재", dj_path.exists())

if dj_path.exists():
    dj = json.loads(dj_path.read_text(encoding="utf-8"))
    check("배열 형식", isinstance(dj, list))
    check("최소 1개 이상", len(dj) >= 1)
    for entry in dj:
        required_keys = {"date", "temperature", "market", "summary", "keywords", "sectors"}
        missing = required_keys - set(entry.keys())
        if missing:
            check(f"{entry['date']} 필드 완전성", False, f"누락: {missing}")
            break
    else:
        check("모든 항목에 sectors 필드 존재", True)

    # 최신 항목 날짜 순서
    dates = [e["date"] for e in dj]
    check("날짜 내림차순 정렬", dates == sorted(dates, reverse=True), f"첫 3개: {dates[:3]}")


# ─────────────────────────────────────────────────────────────
# 10. 주간 루틴 파서
# ─────────────────────────────────────────────────────────────
print("\n[10] 주간 MD 파서")

from scripts.build_stock_site import (
    _parse_week_range, _parse_weekly_summary, _parse_weekly_temperature,
    _parse_weekly_indices, _parse_weekly_sectors, _parse_hot_themes,
    _parse_next_week_schedule, parse_weekly_md,
)

WEEKLY_MD = """
# 📅 주간 주식 시황 종합 — 2026-06-14 (주)

> 기간: 2026-06-09(월) ~ 2026-06-13(금) | 생성: 2026-06-14 09:30 KST

---

## ■ 주간 한줄 총평

방산·반도체 주도 강세, 바이오 조정 속 지수 주간 +2% 상승.

---

## 1. 주간 지수 성과

| 지수 | 주간 시가 | 주간 종가 | 주간 변동 |
|---|---|---|---|
| 코스피 | 2,600.0 | 2,650.3 | +1.93% ▲ |
| 코스닥 | 840.0 | 850.1 | +1.20% ▲ |
| S&P 500 | 5,250.0 | 5,300.2 | +0.96% ▲ |
| 나스닥 | 18,200.0 | 18,500.0 | +1.65% ▲ |
| 원/달러 | - | 1,380.5원 | 주간 변동폭 |

---

## 2. 섹터 주간 성과

### 상위 섹터

| 섹터 | 대표종목 | 주간 누적 |
|---|---|---|
| 방산 | 한화에어로스페이스 | +5.2% |
| 반도체 | 삼성전자 | +3.1% |
| 전력인프라 | HD현대일렉트릭 | +2.8% |

### 하위 섹터

| 섹터 | 대표종목 | 주간 누적 |
|---|---|---|
| 바이오 | 삼성바이오로직스 | -1.5% |
| 로봇 | 레인보우로보틱스 | -0.8% |

---

## 3. 이번 주 핫 테마 TOP 3

### ① [방산 수출]
방위산업 글로벌 수요 급증으로 한화에어로스페이스 사상 최고가 경신.

### ② [AI 반도체]
엔비디아 차세대 칩 발표 기대로 SK하이닉스 HBM 수혜 지속.

### ③ [전력인프라]
미국 데이터센터 전력 수요 증가로 관련 종목 동반 상승.

---

## 4. 차주 주요 일정

| 날짜 | 이벤트 | 예상 영향 |
|---|---|---|
| 06-16(월) | 엔비디아 GTC | 반도체 변동성 |
| 06-17(화) | FOMC 의사록 | 금리 방향성 |
| 06-19(목) | 한국 금통위 | 원화 환율 |

---

## 5. 차주 전략 포인트

1. 방산·전력인프라 핵심 포지션 유지
2. 바이오 단기 반등 매도 기회 활용
3. FOMC 이후 달러/원 변동 주시

---

## 주간 온도계: 🟠 강세

> 방산·반도체 쌍두마차로 코스피 주간 +1.93% 상승, 거래대금 증가.

"""

check("week_range 파싱",         _parse_week_range(WEEKLY_MD) != "")
check("weekly_summary 파싱",     "강세" in _parse_weekly_summary(WEEKLY_MD))

wt = _parse_weekly_temperature(WEEKLY_MD)
check("weekly_temperature 파싱", wt["emoji"] == "🟠", wt.get("display"))
check("weekly_temperature level", wt["level"] == "rising")

wi = _parse_weekly_indices(WEEKLY_MD)
check("weekly_indices 5행",      len(wi) == 5, f"실제: {len(wi)}")
check("weekly_indices 첫 항목",   wi[0]["label"] == "코스피", wi[0].get("label"))
check("weekly_indices change",   "▲" in wi[0]["change"])
check("weekly_indices 헤더 제외", all(r["label"] != "지수" for r in wi))

ws = _parse_weekly_sectors(WEEKLY_MD)
check("weekly_sectors 상위+하위", len(ws) == 5, f"실제: {len(ws)}")
check("weekly_sectors 첫 섹터",   ws[0]["sector"] == "방산", ws[0].get("sector"))
check("weekly_sectors change",   ws[0]["change"] == "+5.2%", ws[0].get("change"))

ht = _parse_hot_themes(WEEKLY_MD)
check("hot_themes 3개",          len(ht) == 3, f"실제: {len(ht)}")
check("hot_themes rank",         ht[0]["rank"] == 1)
check("hot_themes title",        ht[0]["title"] == "방산 수출", ht[0].get("title"))
check("hot_themes description",  "한화에어로스페이스" in ht[0].get("description", ""))

ns = _parse_next_week_schedule(WEEKLY_MD)
check("next_week_schedule 3행",  len(ns) == 3, f"실제: {len(ns)}")
check("next_week_schedule date", ns[0]["date"] == "06-16(월)", ns[0].get("date"))
check("next_week_schedule event",ns[0]["event"] == "엔비디아 GTC", ns[0].get("event"))


# ─────────────────────────────────────────────────────────────
# 11. parse_weekly_md 전체 구조
# ─────────────────────────────────────────────────────────────
print("\n[11] parse_weekly_md — 전체 구조")

import tempfile, os as _os
with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
    f.write(WEEKLY_MD)
    tmp_weekly = f.name

try:
    wd = parse_weekly_md(tmp_weekly, "2026-06-14")
    check("type=weekly",              wd["type"] == "weekly")
    check("date 일치",                wd["date"] == "2026-06-14")
    check("week_range 존재",          bool(wd.get("week_range")))
    check("weekly_indices 리스트",    isinstance(wd["weekly_indices"], list) and len(wd["weekly_indices"]) > 0)
    check("sectors 리스트",           isinstance(wd["sectors"], list) and len(wd["sectors"]) > 0)
    check("hot_themes 리스트",        isinstance(wd["hot_themes"], list) and len(wd["hot_themes"]) > 0)
    check("next_week_schedule 리스트",isinstance(wd["next_week_schedule"], list) and len(wd["next_week_schedule"]) > 0)
    check("market 빈 dict",           wd["market"] == {})
    check("keywords 빈 리스트",        wd["keywords"] == [])
finally:
    _os.unlink(tmp_weekly)


# ─────────────────────────────────────────────────────────────
# 12. build_weekly_stock_html — 카드 구조
# ─────────────────────────────────────────────────────────────
print("\n[12] build_weekly_stock_html — 카드 구조")

from scripts.build_cardnews import build_weekly_stock_html

WEEKLY_DATA = {
    "date":       "2026-06-14",
    "type":       "weekly",
    "week_range": "2026-06-09 ~ 2026-06-13",
    "temperature": {"display": "🟠 강세", "level": "rising"},
    "market":     {},
    "summary":    "방산·반도체 주도 강세, 바이오 조정 속 지수 주간 +2% 상승.",
    "keywords":   [],
    "sectors":    [
        {"sector": "방산", "name": "한화에어로스페이스", "price": "", "change": "+5.2%"},
    ],
    "weekly_indices": [
        {"label": "코스피", "open": "2,600.0", "close": "2,650.3", "change": "+1.93% ▲"},
        {"label": "코스닥", "open": "840.0",   "close": "850.1",   "change": "+1.20% ▲"},
    ],
    "hot_themes": [
        {"rank": 1, "title": "방산 수출",   "description": "한화에어로스페이스 사상 최고가."},
        {"rank": 2, "title": "AI 반도체",   "description": "SK하이닉스 HBM 수혜."},
        {"rank": 3, "title": "전력인프라",   "description": "미국 데이터센터 전력 수요."},
    ],
    "next_week_schedule": [
        {"date": "06-16(월)", "event": "엔비디아 GTC",  "impact": "반도체 변동성"},
        {"date": "06-17(화)", "event": "FOMC 의사록",   "impact": "금리 방향성"},
    ],
}

html_weekly = build_weekly_stock_html("2026-06-14", WEEKLY_DATA)
cards_weekly = re.findall(r'id="card-\d+"', html_weekly)
check("주간 카드 4장",            len(cards_weekly) == 4, f"실제: {len(cards_weekly)}")
check("주간 총평 포함",           "주간 총평" in html_weekly)
check("주간 지수 성과 포함",      "주간 지수 성과" in html_weekly)
check("핫 테마 포함",             "핫 테마" in html_weekly)
check("차주 주요 일정 포함",      "차주 주요 일정" in html_weekly)
check("코스피 데이터 포함",       "코스피" in html_weekly)
check("방산 수출 테마 포함",      "방산 수출" in html_weekly)
check("엔비디아 GTC 일정 포함",   "엔비디아 GTC" in html_weekly)
check("주간 지수 상승 green",     "#34d399" in html_weekly)

# weekly_build.yml 존재 및 트리거 확인
print("\n  [12b] weekly_build.yml 확인")
weekly_yml_path = Path(".github/workflows/weekly_build.yml")
check("weekly_build.yml 존재",    weekly_yml_path.exists())
if weekly_yml_path.exists():
    wyml = weekly_yml_path.read_text(encoding="utf-8")
    check("weekly_build.yml 트리거 weekly_*.md",  "weekly_*.md" in wyml)
    check("weekly_build.yml GitHub Pages 배포",   "deploy-pages" in wyml)


# ─────────────────────────────────────────────────────────────
# 결과 요약
# ─────────────────────────────────────────────────────────────
total = sum(1 for line in open(__file__) if "check(" in line and "check_" not in line)
passed = total - len(_failures)

print(f"\n{'='*60}")
if _failures:
    print(f"\033[31m실패 {len(_failures)}건:\033[0m")
    for f in _failures:
        print(f"  - {f}")
    print(f"\n총 {passed}/{total} 통과")
    sys.exit(1)
else:
    print(f"\033[32m전체 통과 ({passed}건)\033[0m")
