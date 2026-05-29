# 주식시황 브리핑 — 구현계획서

> 작성일: 2026-05-18  
> 상태: **구현 완료, 실 테스트 대기 중**  
> 목적: 현재 구현 상태 기록 및 이후 개선 계획 정의

---

## 1. 시스템 목표

매일 장 마감 후 국내외 주요 지수·환율·섹터 데이터를 수집·분석하여  
이메일 브리핑과 웹사이트를 자동 배포한다.

**핵심 원칙:**
- 기존 뉴스 시스템과 동일한 설정-코드-콘텐츠 분리 구조 준수
- Claude Code 웹 루틴(Primary) + GitHub Actions(Backup) 병행
- 이메일·HTML 빌드·Pages 배포는 GitHub Actions에 위임

---

## 2. 문제 배경 (기존 방식의 한계)

| 문제 | 내용 |
|------|------|
| Gmail MCP 불안정 | Claude 웹 루틴에서 이메일 발송 실패 반복 |
| 수동 실행 의존 | 매일 장 마감 후 직접 루틴 실행 필요 |
| 비정형 데이터 | 웹 검색 기반 수집 → 오류 가능성 |
| 사이트 미반영 | `publish/stock/` HTML 미생성 |

---

## 3. 아키텍처 설계

### 3-1. 두 경로 병행

```
[Primary — Claude Code 루틴]               [Backup — GitHub Actions]
  PlayMCP UsStockInfo                         yfinance 라이브러리
  NaverSearch                                 Naver News API (선택)
  Claude (구독, API 키 불필요)                Gemini API
  Notion MCP                                  -
  git push → Actions 트리거                   cron: 평일 16:45 KST
```

### 3-2. 트리거 구조

```yaml
on:
  push:
    paths: ['reports/stock/**.md']   # Primary: 루틴 push 감지
  schedule:
    - cron: '45 07 * * 1-5'          # Backup: 평일 KST 16:45
  workflow_dispatch:
    inputs:
      mode: {build_only, full}
```

### 3-3. 데이터 흐름

```
Primary 경로 (Claude Code 루틴):
  루틴 실행 (docs/claude_주식시황.md)
  → UsStockInfo MCP (지수/환율/섹터)
  → NaverSearch (국내 뉴스 헤드라인)
  → Read templates/stock_report.md (형식 확인)
  → Claude가 리포트 작성
  → Write tool → reports/stock/stock_YYYY-MM-DD.md
  → Notion MCP → 주식시황 DB 페이지 생성
  → Bash: git add + commit + push
  → stock_build.yml (push 트리거 발동)
      ① send_stock_email.py → 이메일 발송
      ② build_stock_site.py → publish/stock/*.html 빌드
      ③ build_site.py       → publish/*.html 뉴스 사이트도 재빌드
      ④ git commit + Pages 배포

Backup 경로 (GitHub Actions cron):
  cron: 평일 KST 16:45
  → stock_main.py
      ① stock_collector.py → yfinance + Naver News API
      ② stock_analyzer.py  → LLM 분석
      ③ stock_report.py    → Jinja2 렌더링 → MD 저장
      ④ mailer.send_email() → 이메일 발송 (stock_main 내부에서 직접 호출)
  → build_stock_site.py → publish/stock/*.html 빌드
  → build_site.py       → publish/*.html 뉴스 사이트도 재빌드
  → git commit + Pages 배포
```

> **주의:** `send_stock_email.py`는 Primary(push 트리거) 경로 전용.  
> Backup 경로에서는 `stock_main.py` 내부에서 `mailer.send_email()`을 직접 호출한다.

---

## 4. 구현 완료 파일 목록

### 신규 생성

| 파일 | 역할 | 상태 |
|------|------|------|
| `config/stock_prompts.py` | 루틴 프롬프트 + LLM 분석 프롬프트 + 티커 | 완료 |
| `templates/stock_report.md` | Jinja2 주식 리포트 템플릿 | 완료 |
| `core/stock_collector.py` | yfinance 데이터 수집 | 완료 |
| `core/stock_analyzer.py` | LLM 분석 + 섹션 파싱 | 완료 |
| `core/stock_report.py` | Jinja2 렌더링 + MD 저장 | 완료 |
| `scripts/stock_main.py` | Actions 백업 경로 진입점 | 완료 |
| `scripts/build_stock_site.py` | stock MD → HTML 빌드 | 완료 |
| `scripts/send_stock_email.py` | push 트리거 이메일 발송 | 완료 |
| `.github/workflows/stock_build.yml` | 워크플로우 | 완료 |

### 기존 파일 수정

| 파일 | 변경 내용 | 상태 |
|------|----------|------|
| `config/settings.py` | STOCK_REPORTS_DIR, STOCK_EMAIL_SUBJECT, NAVER_* | 완료 |
| `config/theme_config.py` | NAV/HUB stock 섹션 enabled: True | 완료 |
| `themes/base.py` | render_stock_report/archive/email 추가 | 완료 |
| `themes/classic/ink/forest/minimal.py` | stock 렌더러 wrapper 추가 | 완료 |
| `core/mailer.py` | subject_override 파라미터 추가 | 완료 |
| `requirements.txt` | yfinance>=0.2.40 추가 | 완료 |
| `docs/claude_주식시황.md` | 루틴 프롬프트 전면 재작성 | 완료 |

---

## 5. 수집 데이터 스펙

### 5-1. 시장 지수 (yfinance / UsStockInfo MCP)

| 구분 | 티커 | 항목 |
|------|------|------|
| 국내 | `^KS11` | 코스피 종가 + 등락률 |
| 국내 | `^KQ11` | 코스닥 종가 + 등락률 |
| 환율 | `KRW=X` | 원/달러 |
| 매크로 | `^TNX` | 미 10년물 금리 + 변화bp |
| 매크로 | `CL=F` | WTI 유가 |
| 미국 | `^GSPC` | S&P 500 |
| 미국 | `^IXIC` | 나스닥 |
| 미국 | `^DJI` | 다우존스 |

### 5-2. 섹터 종목

| 섹터 | 종목 | 티커 |
|------|------|------|
| 반도체 | 삼성전자, SK하이닉스, 엔비디아 | 005930.KS, 000660.KS, NVDA |
| 2차전지 | LG에너지솔루션, 삼성SDI | 373220.KS, 006400.KS |
| 바이오 | 삼성바이오로직스, 셀트리온 | 207940.KS, 068270.KS |
| 금융 | KB금융, 신한지주 | 105560.KS, 055550.KS |

---

## 6. 리포트 구조 (고정 헤더)

```markdown
# 📊 일일 주식 시황 브리핑 — YYYY-MM-DD
생성: HH:MM KST | 기준: 오늘 장 마감

## ■ 핵심 요약 (3줄)
## 1. 국내 시장
## 2. 글로벌 시장
## 3. 핵심 키워드 TOP 5   ← ① ② ③ ④ ⑤ 마커 (파서 기준)
## 4. 섹터별 영향 분석    ← MD 표 (파서 기준)
## 5. 내일 주목 이벤트
## 6. 장기투자 관점 코멘트
## 시장 온도계              ← 🔴/🟡/🟢 + 근거: 줄 (파서 기준)
```

두 경로(루틴 + 자동화) 모두 동일한 헤더 구조 출력 → 동일 파서 공유.

---

## 7. 사이트 출력

```
publish/stock/
  index.html          ← 최신 주식시황 페이지
  archive.html        ← 전체 목록
  YYYY-MM-DD.html     ← 날짜별 페이지
  stock-data.json     ← 구조화 데이터
```

---

## 8. 미완료 / 실 테스트 필요

| 항목 | 상태 | 비고 |
|------|------|------|
| 루틴 실 실행 | 대기 중 | docs/claude_주식시황.md를 루틴에 붙여넣기 후 실행 |
| push 트리거 확인 | 대기 중 | stock MD 파일 push 후 Actions 발동 여부 확인 |
| Notion 속성 확인 | 대기 중 | '주식시황' DB 이름 및 속성(날짜/핵심키워드/시장온도) 일치 여부 |
| 이메일 수신 확인 | 대기 중 | Actions 실행 후 이메일 포맷 확인 |
| HTML 렌더링 확인 | 대기 중 | publish/stock/index.html 시각 확인 |
| Naver API 등록 | 선택 | 보유 시 NAVER_CLIENT_ID/SECRET → GitHub Secrets |

---

## 9. 이후 개선 계획

### 9-1. 즉시 반영 가능 (낮은 리스크)

| 항목 | 내용 | 대상 파일 |
|------|------|-----------|
| **중복 이메일 방지** | Backup schedule이 Primary push 당일 실행 시 이메일 중복 발송 → `send_stock_email.py`에 오늘 날짜 이미 발송 여부 체크 로직 추가 | `scripts/send_stock_email.py` |
| **Notion DB ID 고정** | `notion-search`로 매번 DB 탐색 → 실패 포인트. 한 번 확인한 DB ID를 `config/watchlist.yaml`에 고정 | `config/watchlist.yaml` (신규), `docs/claude_주식시황.md` |
| **^KS11 수집 실패 폴백** | PlayMCP가 코스피 티커를 지원하지 않을 경우 NaverSearch로 수치 추출 | `docs/claude_주식시황.md` Step 1에 폴백 명시 |
| **git 커밋 날짜 자동화** | 루틴 Step 5의 커밋 메시지가 `"📊 Stock briefing YYYY-MM-DD"` 문자열 고정 → 실제 날짜 변수 사용: `git -C ... commit -m "📊 Stock briefing $(Get-Date -Format 'yyyy-MM-dd')"` | `docs/claude_주식시황.md` Step 5 |

---

### 9-2. 핵심 개선 — `config/watchlist.yaml` 도입

**문제:** 섹터 종목이 `config/stock_prompts.py::SECTOR_TICKERS`와 `docs/claude_주식시황.md`에 하드코딩 → 종목 추가/삭제 시 코드·루틴 프롬프트 둘 다 수정 필요.

**해결:** 외부 YAML 파일로 분리. `enabled` 플래그로 섹터 단위 토글 가능.

```yaml
# config/watchlist.yaml

notion:
  stock_db_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"   # Notion DB ID 고정

sectors:
  - name: "반도체"
    enabled: true
    stocks:
      - { ticker: "005930.KS", name: "삼성전자",   market: "KR" }
      - { ticker: "000660.KS", name: "SK하이닉스", market: "KR" }
      - { ticker: "NVDA",      name: "엔비디아",   market: "US" }
      - { ticker: "AMD",       name: "AMD",        market: "US" }

  - name: "AI/빅테크"
    enabled: true
    stocks:
      - { ticker: "MSFT",      name: "마이크로소프트", market: "US" }
      - { ticker: "GOOGL",     name: "알파벳",        market: "US" }
      - { ticker: "META",      name: "메타",           market: "US" }
      - { ticker: "035420.KS", name: "NAVER",         market: "KR" }

  - name: "전력인프라"
    enabled: true
    stocks:
      - { ticker: "267260.KS", name: "HD현대일렉트릭",    market: "KR" }
      - { ticker: "CEG",       name: "콘스텔레이션에너지", market: "US" }

  - name: "방산/우주"
    enabled: true
    stocks:
      - { ticker: "012450.KS", name: "한화에어로스페이스", market: "KR" }
      - { ticker: "079550.KS", name: "LIG넥스원",          market: "KR" }
      - { ticker: "LMT",       name: "록히드마틴",          market: "US" }

  - name: "바이오"
    enabled: true
    stocks:
      - { ticker: "207940.KS", name: "삼성바이오로직스", market: "KR" }
      - { ticker: "068270.KS", name: "셀트리온",         market: "KR" }
      - { ticker: "LLY",       name: "일라이릴리",        market: "US" }

  - name: "금융"
    enabled: true
    stocks:
      - { ticker: "105560.KS", name: "KB금융",  market: "KR" }
      - { ticker: "055550.KS", name: "신한지주", market: "KR" }
      - { ticker: "JPM",       name: "JP모건",   market: "US" }

  - name: "2차전지"
    enabled: false           # 비활성화: enabled: false 한 줄로 전체 제외
    stocks:
      - { ticker: "373220.KS", name: "LG에너지솔루션", market: "KR" }
      - { ticker: "TSLA",      name: "테슬라",          market: "US" }

  - name: "로봇"
    enabled: true
    stocks:
      - { ticker: "277810.KS", name: "레인보우로보틱스", market: "KR" }
      - { ticker: "ISRG",      name: "인튜이티브서지컬", market: "US" }
```

**영향 파일:**

| 파일 | 변경 내용 |
|------|----------|
| `config/watchlist.yaml` | 신규 생성 |
| `config/stock_prompts.py` | `SECTOR_TICKERS` dict 제거, YAML 로딩 함수 추가 |
| `core/stock_collector.py` | `collect_sectors()` → YAML 기반으로 수정 |
| `docs/claude_주식시황.md` | Step 1: 하드코딩 티커 제거, YAML Read로 대체 |
| `requirements.txt` | `PyYAML` 추가 |

---

### 9-3. 데이터 자산 — `reports/history/{ticker}.md` 누적 이력

**목표:** 티커별 일별 종가를 누적 저장하여 추후 수익률 계산, 변동성 분석, 차트 생성에 활용.

**경로:** `reports/history/{ticker}.md` (기존 reports/ 관리 체계와 통합, JSON 아닌 MD 테이블)

```markdown
# NVDA — 엔비디아 (US · 반도체)

| 날짜 | 종가 | 등락률 | 거래량 | 메모 |
|------|-----:|-------:|-------:|------|
| 2026-05-16 | 131.38 | +2.14% | 42,800,000 | |
| 2026-05-17 | 135.72 | +3.30% | 51,200,000 | |
```

**`scripts/update_history.py` 로직:**

```python
from pathlib import Path
import re, yaml

HISTORY_DIR = Path("reports/history")
MAX_ROWS = 365

def update_ticker_md(ticker, name, market, sector, entry):
    """
    entry = {"date": "2026-05-18", "price": 135.72,
              "change_pct": 3.30, "volume": 51200000}
    """
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    safe = ticker.replace("/", "_").replace("^", "")
    path = HISTORY_DIR / f"{safe}.md"

    header     = f"# {ticker} — {name} ({market} · {sector})\n\n"
    tbl_header = "| 날짜 | 종가 | 등락률 | 거래량 | 메모 |\n|------|-----:|-------:|-------:|------|\n"

    rows = []
    if path.exists():
        rows = [l for l in path.read_text(encoding="utf-8").splitlines()
                if l.startswith("| 20")]

    today = entry["date"]
    new_row = (f"| {today} | {entry['price']} "
               f"| {entry['change_pct']:+.2f}% "
               f"| {entry.get('volume', 0):,} | |")

    rows = [r for r in rows if not r.startswith(f"| {today}")]
    rows.append(new_row)
    rows = sorted(rows)[-MAX_ROWS:]   # 날짜 오름차순, 최대 365행

    path.write_text(header + tbl_header + "\n".join(rows) + "\n", encoding="utf-8")
```

**워크플로우 연동 (stock_build.yml에 step 추가):**

```yaml
- name: 티커 이력 업데이트
  run: python scripts/update_history.py
  # reports/history/ 자동 생성 및 누적
```

```yaml
# 커밋 대상에 reports/history/ 추가
git add reports/stock/ reports/history/ publish/
```

**MD vs JSON 선택 이유:**
- GitHub에서 직접 표 형태로 열람 가능
- 기존 `reports/` 커밋 범위에 자동 포함
- 정규식으로 파싱 가능 (pandas read 용이)
- 365행 제한으로 파일 크기 관리 가능

---

### 9-4. 리포트 품질 — 국내/해외 섹터 분리

**현재:** 섹터 분석 표가 단일 테이블로 국내/해외 혼재  
**개선:** `market` 기준으로 🇰🇷 국내 / 🇺🇸 해외 섹션 분리

```markdown
## 4. 섹터별 영향 분석

### 🇰🇷 국내
| 섹터 | 대표종목 | 방향 | 핵심 포인트 |
|------|---------|:----:|------------|

### 🇺🇸 해외
| 섹터 | 대표종목 | 방향 | 핵심 포인트 |
|------|---------|:----:|------------|
```

영향 파일: `templates/stock_report.md`, `config/stock_prompts.py::STOCK_ANALYSIS_PROMPT`, `core/stock_analyzer.py::_parse_sectors()`, `scripts/build_stock_site.py`

---

### 9-5. 장기 — 주간 요약

매주 월요일 오전, 주간 시황 종합 리포트 자동 생성. `reports/history/` 데이터가 쌓인 후 구현.

---

### 개선 항목 요약

| 우선순위 | 항목 | 상태 |
|----------|------|------|
| 즉시 | 중복 이메일 방지 | ✅ 완료 |
| 즉시 | Notion DB ID 고정 (watchlist.yaml) | ✅ 완료 |
| 즉시 | ^KS11 폴백 명시 | ✅ 완료 |
| 즉시 | git 커밋 날짜 변수 | ✅ 완료 |
| 1순위 | watchlist.yaml 도입 (섹터 종목 분리) | ✅ 완료 |
| 2순위 | reports/history/{ticker}.md 누적 이력 | ✅ 완료 |
| 3순위 | 국내/해외 섹터 분리 | ✅ 완료 |
| 장기 | 주간 요약 리포트 | 미시행 |

---

## 10. GitHub Secrets 목록

| Secret | 필수 여부 | 설명 |
|--------|-----------|------|
| `GMAIL_USER` | 필수 | Gmail 주소 |
| `GMAIL_APP_PASSWORD` | 필수 | 앱 비밀번호 |
| `RECIPIENT_EMAILS` | 필수 | 수신자 목록 |
| `LLM_PROVIDER` | 백업 경로 필수 | gemini 권장 |
| `GEMINI_API_KEY` | 백업 경로 필수 | AIza... |
| `SITE_BASE_URL` | 선택 | GitHub Pages URL |
| `SITE_THEME` | 선택 | classic (기본) |
| `NAVER_CLIENT_ID` | 선택 | Naver 검색 API 보유 시 |
| `NAVER_CLIENT_SECRET` | 선택 | Naver 검색 API 보유 시 |
