프롬프트 검토하고 섹터 종목 유연성 문제를 분석해볼게요.

## 전반적인 평가

현재 프롬프트는 이전 버전보다 훨씬 구조화되어 있고, 도구별 역할 분리가 명확합니다. 특히 GitHub Actions 위임 방식이 좋습니다.

---

## 주요 개선 사항 (이전 → 현재)

| 항목 | 이전 | 현재 |
|------|------|------|
| 데이터 수집 | 웹 검색 의존 (불안정) | PlayMCP UsStockInfo 티커 직접 호출 (안정적) |
| 저장 방식 | GitHub 커밋 직접 명시 불명확 | Write tool + Git Bash 명확히 분리 |
| 이메일 | Gmail MCP 직접 발송 | GitHub Actions 위임 (루틴 간소화) |
| 템플릿 | 프롬프트에 구조 내포 | 외부 파일 참조 (유지보수 용이) |

---

## 핵심 문제: 섹터 종목이 하드코딩되어 있음

현재 구조의 핵심 취약점은 **섹터 종목 목록이 프롬프트 안에 박혀 있다**는 것입니다. 종목을 추가/삭제하려면 루틴 프롬프트 자체를 수정해야 합니다.

### 해결 방법: 외부 설정 파일로 분리

템플릿 파일처럼 **종목 설정도 별도 파일로 분리**하고, 루틴이 실행 시 읽어오게 하는 방식이 가장 유연합니다.

```
c:\ai\dailynews\
├── templates\
│   └── stock_report.md        ← 기존
├── config\
│   └── watchlist.yaml         ← 추가 (종목 설정)
└── reports\stock\
```

**`watchlist.yaml` 예시:**

```yaml
# 종목 추가/삭제는 이 파일만 수정하면 됩니다
# enabled: false 로 임시 비활성화 가능
sectors:
  - name: "반도체"
    enabled: true
    tickers:
      - { ticker: "005930.KS", name: "삼성전자" }
      - { ticker: "000660.KS", name: "SK하이닉스" }
      - { ticker: "042700.KS", name: "한미반도체" }
      - { ticker: "NVDA",      name: "엔비디아" }

  - name: "2차전지"
    enabled: true
    tickers:
      - { ticker: "373220.KS", name: "LG에너지솔루션" }
      - { ticker: "006400.KS", name: "삼성SDI" }

  - name: "바이오"
    enabled: true
    tickers:
      - { ticker: "207940.KS", name: "삼성바이오로직스" }
      - { ticker: "068270.KS", name: "셀트리온" }

  - name: "금융"
    enabled: true
    tickers:
      - { ticker: "105560.KS", name: "KB금융" }
      - { ticker: "055550.KS", name: "신한지주" }

  - name: "전력인프라"
    enabled: true
    tickers:
      - { ticker: "267260.KS", name: "HD현대일렉트릭" }
      - { ticker: "010120.KS", name: "LS일렉트릭" }

  - name: "방산/우주"
    enabled: true
    tickers:
      - { ticker: "012450.KS", name: "한화에어로스페이스" }
      - { ticker: "047810.KS", name: "한국항공우주" }
      - { ticker: "079550.KS", name: "LIG넥스원" }

  - name: "로봇"
    enabled: true
    tickers:
      - { ticker: "277810.KS", name: "레인보우로보틱스" }
      - { ticker: "395400.KS", name: "에스비비테크" }

  - name: "AI/플랫폼"
    enabled: false
    tickers:
      - { ticker: "035420.KS", name: "NAVER" }
      - { ticker: "035720.KS", name: "카카오" }
      - { ticker: "MSFT",      name: "마이크로소프트" }
      - { ticker: "META",      name: "메타" }

```

**Step 1 프롬프트 수정:**

```markdown
[Step 1: 데이터 수집]
Read tool로 c:\ai\dailynews\config\watchlist.yaml 을 읽어
enabled: true 인 모든 섹터의 티커 목록을 확인한다.
그 후 index / macro / us_index / 각 섹터 티커에 대해
PlayMCP UsStockInfo get_stock_info 를 순서대로 호출한다.
수집 실패 항목은 N/A 로 표기하고 계속 진행한다.
```

---

## 그 외 세부 개선 제안

**1. `^KS11`, `^KQ11` 티커 수집 실패 가능성**

Yahoo Finance 기준 코스피는 `^KS11`, 코스닥은 `^KQ11`인데, PlayMCP UsStockInfo가 이 티커를 지원하는지 사전에 검증이 필요합니다. 실패 시 NaverSearch `search_news`의 본문에서 파싱하는 폴백 로직을 명시해두는 게 안전합니다.

```markdown
코스피·코스닥 수집 실패 시:
NaverSearch search_news "코스피 코스닥 종가" 결과에서
수치를 직접 추출하여 사용한다.
```

**2. Notion 데이터베이스 ID 하드코딩 권장**

`notion-search`로 DB를 매번 탐색하는 건 실패 포인트입니다. 한 번 확인한 DB ID를 `watchlist.yaml`이나 별도 `config.yaml`에 고정해두는 게 낫습니다.

```yaml
# config.yaml
notion:
  stock_db_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

**3. Git 커밋 날짜 변수 명시**

```bash
# 현재 (모호)
git commit -m "📊 Stock briefing YYYY-MM-DD"

# 개선 (명확)
git commit -m "📊 Stock briefing $(date +%Y-%m-%d)"
```

---

## 요약

| 문제 | 해결 |
|------|------|
| 섹터 종목 하드코딩 | `watchlist.yaml` 외부 파일 분리 + `enabled` 플래그 |
| 섹터 전체 임시 제외 | `enabled: false` 한 줄로 토글 |
| 새 섹터 추가 | YAML에 블록 추가만, 프롬프트 무수정 |
| Notion DB 탐색 실패 | DB ID를 설정 파일에 고정 |
| 지수 수집 불안정 | NaverSearch 폴백 명시 |

`watchlist.yaml`을 git으로 관리하면 **종목 변경 이력도 자동으로 추적**됩니다.



좋은 방향이에요. 두 가지를 같이 설계해볼게요.

## 1. 국내/해외 구분 구조

`watchlist.yaml`에 `market` 필드를 추가하고, 섹터도 글로벌 관점으로 재편합니다.

```yaml
# watchlist.yaml

sectors:

  # ─── 반도체 ───────────────────────────────────────
  - name: "반도체"
    enabled: true
    stocks:
      - { ticker: "005930.KS", name: "삼성전자",   market: "KR" }
      - { ticker: "000660.KS", name: "SK하이닉스", market: "KR" }
      - { ticker: "042700.KS", name: "한미반도체", market: "KR" }
      - { ticker: "NVDA",      name: "엔비디아",   market: "US" }
      - { ticker: "AMD",       name: "AMD",        market: "US" }
      - { ticker: "TSM",       name: "TSMC",       market: "US" }  # ADR

  # ─── AI/빅테크 ────────────────────────────────────
  - name: "AI/빅테크"
    enabled: true
    stocks:
      - { ticker: "MSFT", name: "마이크로소프트", market: "US" }
      - { ticker: "GOOGL", name: "알파벳",        market: "US" }
      - { ticker: "META",  name: "메타",           market: "US" }
      - { ticker: "AMZN",  name: "아마존",         market: "US" }
      - { ticker: "035420.KS", name: "NAVER",     market: "KR" }

  # ─── 전력인프라 ───────────────────────────────────
  - name: "전력인프라"
    enabled: true
    stocks:
      - { ticker: "267260.KS", name: "HD현대일렉트릭", market: "KR" }
      - { ticker: "010120.KS", name: "LS일렉트릭",     market: "KR" }
      - { ticker: "ETR",       name: "에버지 (미 전력)", market: "US" }
      - { ticker: "CEG",       name: "콘스텔레이션 에너지", market: "US" }

  # ─── 방산/우주 ────────────────────────────────────
  - name: "방산/우주"
    enabled: true
    stocks:
      - { ticker: "012450.KS", name: "한화에어로스페이스", market: "KR" }
      - { ticker: "047810.KS", name: "한국항공우주",       market: "KR" }
      - { ticker: "079550.KS", name: "LIG넥스원",          market: "KR" }
      - { ticker: "LMT",       name: "록히드마틴",          market: "US" }
      - { ticker: "RTX",       name: "RTX(레이시온)",       market: "US" }

  # ─── 로봇 ─────────────────────────────────────────
  - name: "로봇"
    enabled: true
    stocks:
      - { ticker: "277810.KS", name: "레인보우로보틱스", market: "KR" }
      - { ticker: "ISRG",      name: "인튜이티브서지컬", market: "US" }
      - { ticker: "FANUY",     name: "화낙 (FANUC ADR)", market: "US" }

  # ─── 바이오/헬스케어 ──────────────────────────────
  - name: "바이오"
    enabled: true
    stocks:
      - { ticker: "207940.KS", name: "삼성바이오로직스", market: "KR" }
      - { ticker: "068270.KS", name: "셀트리온",         market: "KR" }
      - { ticker: "LLY",       name: "일라이릴리",        market: "US" }
      - { ticker: "NVO",       name: "노보노디스크",      market: "US" }

  # ─── 금융 ─────────────────────────────────────────
  - name: "금융"
    enabled: true
    stocks:
      - { ticker: "105560.KS", name: "KB금융",  market: "KR" }
      - { ticker: "055550.KS", name: "신한지주", market: "KR" }
      - { ticker: "JPM",       name: "JP모건",   market: "US" }
      - { ticker: "BRK-B",     name: "버크셔B",  market: "US" }

  # ─── 2차전지 ──────────────────────────────────────
  - name: "2차전지"
    enabled: true
    stocks:
      - { ticker: "373220.KS", name: "LG에너지솔루션", market: "KR" }
      - { ticker: "006400.KS", name: "삼성SDI",        market: "KR" }
      - { ticker: "TSLA",      name: "테슬라",          market: "US" }
      - { ticker: "ALBM",      name: "알베마를 (리튬)", market: "US" }
```

---

## 2. 티커별 누적 이력 DB 설계

매일 수집한 데이터를 **티커 단위로 누적 저장**하는 구조입니다.

### 파일 구조

```
c:\ai\dailynews\
├── config\
│   └── watchlist.yaml
├── data\
│   └── history\
│       ├── NVDA.json          ← 티커별 누적 파일
│       ├── 005930.KS.json
│       ├── 000660.KS.json
│       └── ...
└── reports\stock\
```

### 각 티커 JSON 포맷 (`NVDA.json`)

```json
{
  "ticker": "NVDA",
  "name": "엔비디아",
  "market": "US",
  "sector": "반도체",
  "history": [
    {
      "date": "2026-05-16",
      "price": 131.38,
      "change_pct": 2.14,
      "volume": 42800000,
      "market_cap": null,
      "memo": ""
    },
    {
      "date": "2026-05-17",
      "price": 135.72,
      "change_pct": 3.30,
      "volume": 51200000,
      "market_cap": null,
      "memo": ""
    }
  ]
}
```

### 루틴 Step에 추가할 누적 저장 로직 (Step 3-b)

```markdown
[Step 3-b: 티커별 히스토리 누적 저장 — Python/Bash tool]

아래 Python 스크립트를 실행하여 수집 데이터를 누적 저장한다:

  python c:\ai\dailynews\scripts\update_history.py \
    --date {오늘날짜} \
    --data {수집된_JSON_문자열}

update_history.py 동작:
  1. watchlist.yaml 에서 enabled:true 종목 목록 로드
  2. 각 티커의 data/history/{ticker}.json 읽기 (없으면 신규 생성)
  3. 오늘 날짜 데이터가 이미 있으면 덮어쓰기, 없으면 append
  4. history 배열이 365건 초과 시 오래된 것부터 자동 제거 (1년치 유지)
  5. 저장 완료 후 수정된 파일 목록 출력
```

### `update_history.py` 스크립트

```python
import json, yaml, sys, os
from datetime import datetime
from pathlib import Path

BASE = Path("c:/ai/dailynews")
HISTORY_DIR = BASE / "data" / "history"
WATCHLIST   = BASE / "config" / "watchlist.yaml"
MAX_DAYS    = 365

def load_watchlist():
    with open(WATCHLIST) as f:
        return yaml.safe_load(f)

def update_ticker(ticker, name, market, sector, today_data: dict):
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = HISTORY_DIR / f"{ticker.replace('/', '_')}.json"

    if path.exists():
        with open(path) as f:
            record = json.load(f)
    else:
        record = {"ticker": ticker, "name": name,
                  "market": market, "sector": sector, "history": []}

    # 오늘 날짜 중복 제거 후 추가
    record["history"] = [h for h in record["history"]
                         if h["date"] != today_data["date"]]
    record["history"].append(today_data)

    # 최신순 정렬 후 365일 유지
    record["history"].sort(key=lambda x: x["date"])
    record["history"] = record["history"][-MAX_DAYS:]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {ticker} ({len(record['history'])}일치 누적)")

# 실행 시 collected_data는 루틴이 JSON으로 전달
if __name__ == "__main__":
    wl = load_watchlist()
    collected = json.loads(sys.argv[2])  # --data 인자

    for sector in wl["sectors"]:
        if not sector.get("enabled", True):
            continue
        for stock in sector["stocks"]:
            ticker = stock["ticker"]
            if ticker in collected:
                update_ticker(
                    ticker   = ticker,
                    name     = stock["name"],
                    market   = stock["market"],
                    sector   = sector["name"],
                    today_data = collected[ticker]
                )
```

---

## 3. 리포트 섹션에 시장 구분 반영

리포트 템플릿(`stock_report.md`)의 섹터 분석 표도 market 기준으로 분리합니다:

```markdown
## 4. 섹터별 영향 분석

### 🇰🇷 국내
| 섹터 | 대표종목 | 방향 | 코멘트 |
|------|---------|------|--------|
| 반도체 | 삼성전자 / SK하이닉스 | 🟢 | ... |

### 🇺🇸 해외
| 섹터 | 대표종목 | 방향 | 코멘트 |
|------|---------|------|--------|
| AI/빅테크 | NVDA / MSFT | 🟢 | ... |
```

---

## 요약

| 개선 항목 | 방법 |
|-----------|------|
| 국내/해외 구분 | `market: KR / US` 필드 추가, 섹터에 글로벌 종목 혼합 |
| 티커 누적 이력 | `data/history/{ticker}.json` — 365일 자동 롤링 |
| 중복 방지 | 같은 날짜 데이터는 덮어쓰기 처리 |
| 이력 활용 | 추후 `history` JSON으로 수익률 계산, 차트, 변동성 분석 가능 |
| Git 커밋 대상 | `data/history/` 폴더도 커밋 범위에 포함 (`git add data/history/`) |

누적 데이터가 쌓이면 나중에 **30일 수익률 비교, 섹터별 모멘텀 차트, 변동성 랭킹** 같은 분석으로 확장하기 좋은 구조입니다.