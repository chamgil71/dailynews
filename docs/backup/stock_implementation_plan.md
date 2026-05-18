# 주식 시황 브리핑 — 구현 계획서

> 작성일: 2026-05-18  
> 목표: Claude Code 웹 루틴 → GitHub Actions + Python 스크립트로 완전 자동화  
> 원칙: 기존 뉴스 시스템과 동일한 **설정(config) - 코드(core/themes) - 콘텐츠(reports/publish)** 분리 구조 준수

---

## 1. 현재 상태 분석

### 1-1. 현재 루틴 (Claude Code 웹)

```
docs/claude_주식시황.md 프롬프트 → Claude 웹 실행
  1. 웹 검색으로 지수·환율·금리·유가 수집
  2. AI가 리포트 작성 (reports/stock/stock_YYYY-MM-DD.md)
  3. Gmail MCP로 이메일 발송  ← 실패 원인
  4. Notion MCP로 페이지 생성
```

**문제점:**
- 이메일 발송: Claude 웹 루틴에서 Gmail MCP 불안정 → 실패 반복
- 수동 실행 필요: 매일 장 마감 후 직접 루틴 실행해야 함
- 데이터 수집: 웹 검색 의존 → 비정형, 오류 가능성 높음
- 사이트 미반영: `publish/stock/` HTML 생성 없음 (MD만 저장됨)

### 1-2. 재사용 가능한 기존 자산

| 모듈 | 재사용 방법 |
|------|-----------|
| `core/mailer.py` | `send_email()` 그대로 사용 (Gmail SMTP, 테마 연동) |
| `core/analyzer.py` 패턴 | LLM 호출 구조 동일하게 stock_analyzer.py 작성 |
| `themes/base.py` | `render_report/email()` 확장하여 stock 전용 렌더링 추가 |
| `config/theme_config.py` | NAV_SECTIONS/HUB_SECTIONS `stock` 항목 enabled 전환 |
| `config/settings.py` | GMAIL_USER, LLM_PROVIDER 등 공유 |
| `.github/workflows/news.yml` | stock.yml 템플릿으로 활용 |
| `scripts/build_site.py` 패턴 | build_stock_site.py 동일 구조로 작성 |

---

## 2. GitHub Actions vs 별도 처리 분리

### GitHub Actions로 처리 (자동화 가능)

| 작업 | 방법 | 비고 |
|------|------|------|
| 지수/환율/금리/유가 수집 | `yfinance` 라이브러리 | ^KS11, ^GSPC, ^TNX, CL=F 등 |
| 섹터 대표 종목 수집 | `yfinance` | 005930.KS, 000660.KS 등 |
| 국내 뉴스 헤드라인 | Naver News API | NAVER_CLIENT_ID/SECRET 시크릿 등록 |
| AI 분석 + 리포트 작성 | Gemini/GPT/Claude API | 기존 LLM 인프라 재사용 |
| MD 파일 저장 | `core/stock_report.py` | reports/stock/stock_YYYY-MM-DD.md |
| HTML 빌드 | `scripts/build_stock_site.py` | publish/stock/index.html |
| 이메일 발송 | `core/mailer.py` | 기존 SMTP 방식 — GitHub Actions에서 정상 작동 |
| Git 커밋 + Pages 배포 | workflow 내 git step | 기존 news.yml 동일 패턴 |

### Claude Code 웹 / MCP 유지 (자동화 불가)

| 작업 | 이유 |
|------|------|
| Notion 페이지 생성 | MCP 전용 — GitHub Actions 환경 없음 |
| 비정형 이벤트 검색 | 실시간 웹 검색 필요 시 수동 보완 |
| 리포트 수동 보정 | 이상값 발생 시 사람이 확인 후 재실행 |

---

## 3. 데이터 수집 설계 (yfinance 기반)

### 3-1. 수집 대상 및 티커

```python
MARKET_TICKERS = {
    # 국내 지수
    "kospi":      "^KS11",    # 코스피
    "kosdaq":     "^KQ11",    # 코스닥
    # 환율
    "usd_krw":    "KRW=X",    # 원/달러
    # 미국 지수
    "sp500":      "^GSPC",    # S&P 500
    "nasdaq":     "^IXIC",    # 나스닥
    "dow":        "^DJI",     # 다우존스
    # 매크로
    "us10y":      "^TNX",     # 미국 10년물 금리
    "wti":        "CL=F",     # WTI 유가
}

SECTOR_TICKERS = {
    # 반도체
    "삼성전자":   "005930.KS",
    "SK하이닉스": "000660.KS",
    "엔비디아":   "NVDA",
    # 2차전지
    "LG에너지솔루션": "373220.KS",
    "삼성SDI":    "006400.KS",
    # 바이오
    "삼성바이오로직스": "207940.KS",
    "셀트리온":   "068270.KS",
    # 금융
    "KB금융":     "105560.KS",
    "신한지주":   "055550.KS",
}
```

### 3-2. 수집 데이터 구조

```python
StockData = {
    "date": "2026-05-18",
    "market": {
        "kospi":  {"close": 7493.18, "change_pct": -6.12},
        "kosdaq": {"close": 1129.82, "change_pct": -5.30},
        "usd_krw":{"close": 1500.8,  "change_pct": 0.66},
        "sp500":  {"close": 7408.50, "change_pct": -1.24},
        "nasdaq": {"close": 26225.15,"change_pct": -1.54},
        "dow":    {"close": 49526.17,"change_pct": -1.07},
        "us10y":  {"value": 4.595,   "change_bp": 13.4},
        "wti":    {"close": 101.02,  "change_pct": 4.23},
    },
    "sectors": {
        "삼성전자":   {"close": 87400, "change_pct": -8.61},
        "SK하이닉스": {"close": 198000,"change_pct": -7.66},
        # ...
    },
    "news_ko": [...],  # Naver API 국내 증시 뉴스 5~10건
    "generated_at": "2026-05-18T07:30:00+09:00",
}
```

---

## 4. 신규 파일 구조

```
[신규 생성]
core/
  stock_collector.py      # yfinance + Naver API 데이터 수집
  stock_analyzer.py       # 수집 데이터 → LLM 분석 → 구조화 리포트
  stock_report.py         # MD 파일 저장

config/
  stock_prompts.py        # 주식 분석 프롬프트 (기존 prompts.py 패턴 동일)

templates/
  stock_report.md         # Jinja2 MD 템플릿

scripts/
  stock_main.py           # 주식 브리핑 진입점 (기존 main.py 패턴)
  build_stock_site.py     # stock MD → HTML (기존 build_site.py 패턴)

.github/workflows/
  stock.yml               # GitHub Actions 워크플로우

[기존 수정]
config/settings.py        # NAVER_CLIENT_ID/SECRET, STOCK_REPORTS_DIR 추가
config/theme_config.py    # NAV_SECTIONS/HUB_SECTIONS stock enabled: True
themes/base.py            # render_stock_report(), render_stock_email() 추가
                          # OR themes/stock.py 별도 모듈
requirements.txt          # yfinance 추가
```

---

## 5. 각 모듈 설계

### 5-1. `core/stock_collector.py`

```python
# 책임: 시장 데이터 수집 (yfinance + Naver News API)
# 반환: StockData dict (LLM 프롬프트 주입용)

def collect_market_data() -> dict:
    """yfinance로 지수·환율·금리·유가·섹터 종목 수집."""

def collect_news_ko(query: str = "코스피 증시") -> list[dict]:
    """Naver News API로 국내 증시 뉴스 헤드라인 수집."""

def build_stock_data() -> dict:
    """collect_market_data + collect_news_ko 통합 → StockData 반환."""
```

**yfinance 장단점:**
- 장점: 무료, 한국 지수 지원(`^KS11`, `^KQ11`), 종목 시세
- 단점: 장 마감 후 15~30분 딜레이, 실시간 아님
- 대안: FinanceDataReader(한국), 네이버금융 RSS

### 5-2. `config/stock_prompts.py`

```python
STOCK_PROMPT_TEMPLATE: str = """\
당신은 주식 시황 분석 전문가입니다. 아래 시장 데이터를 분석하세요.
**반드시 한국어로 답변하세요.**

출력 형식 (반드시 준수 — 헤더 레벨 변경 금지):

## ■ 핵심 요약 (3줄)
- **[요약1]** — 핵심 지수 동향
- **[요약2]** — 글로벌 매크로
- **[요약3]** — 이번 주 주목 이벤트

## 3. 핵심 키워드 TOP 5

### [키워드 제목]
2~3문장 분석. 배경·영향 포함.

### [키워드 제목]
...

## 6. 장기투자 관점 코멘트
2~3문장. 펀더멘털 기반 관점.

## 시장 온도계
🔴리스크오프 | 🟡중립 | 🟢리스크온 중 하나를 선택하고 근거 1줄.

시장 데이터:
{market_block}

국내 뉴스 헤드라인:
{news_block}
"""
```

### 5-3. `core/stock_analyzer.py`

```python
# 책임: StockData → LLM 분석 → 분석 텍스트 반환
# 기존 analyzer.py의 get_analyzer() 패턴 재사용

def build_stock_prompt(stock_data: dict) -> str:
    """StockData → STOCK_PROMPT_TEMPLATE 포맷."""

def analyze_stock(stock_data: dict) -> dict:
    """
    반환:
    {
        "summary": str,         # 핵심 요약 3줄
        "keywords": str,        # 핵심 키워드 TOP 5 섹션
        "lt_comment": str,      # 장기투자 코멘트
        "temperature": str,     # 시장 온도계 결과 ("리스크오프"|"중립"|"리스크온")
        "combined": str,        # 전체 AI 출력 (MD 삽입용)
    }
    """
```

### 5-4. `templates/stock_report.md`

```markdown
# 📊 일일 주식 시황 브리핑 — {{ date }}

> 📅 생성일시: {{ generated_at }}  
> 📊 데이터 기준: {{ market_close_time }}

---

## ■ 핵심 요약 (3줄)
{{ analysis.summary }}

---

## 1. 국내 시장

| 지수 | 종가 | 등락률 |
|------|-----:|-------:|
| 코스피 | {{ market.kospi.close }} | {{ market.kospi.change_pct }}% |
| 코스닥 | {{ market.kosdaq.close }} | {{ market.kosdaq.change_pct }}% |
| 원/달러 | {{ market.usd_krw.close }}원 | {{ market.usd_krw.change_pct }}% |

---

## 2. 글로벌 시장

| 지수/지표 | 수치 | 등락 |
|-----------|-----:|------:|
| S&P 500 | {{ market.sp500.close }} | {{ market.sp500.change_pct }}% |
| 나스닥 | {{ market.nasdaq.close }} | {{ market.nasdaq.change_pct }}% |
| 다우존스 | {{ market.dow.close }} | {{ market.dow.change_pct }}% |
| 미국 10년물 금리 | {{ market.us10y.value }}% | {{ market.us10y.change_bp }}bp |
| WTI 유가 | ${{ market.wti.close }} | {{ market.wti.change_pct }}% |

---

{{ analysis.combined }}

---

## 4. 섹터별 영향 분석

| 섹터 | 대표 종목 | 종가 | 등락 |
|------|---------|-----:|------:|
{% for name, data in sectors.items() %}
| - | {{ name }} | {{ data.close }} | {{ data.change_pct }}% |
{% endfor %}

---

{{ analysis.events }}

---

## 시장 온도계: {{ analysis.temperature_display }}

---
※ 투자 권유 아님. 데이터 기준: {{ market_close_time }}
```

### 5-5. `scripts/build_stock_site.py`

```python
# 기존 build_site.py 패턴 그대로 — stock 전용
# reports/stock/stock_*.md → publish/stock/*.html + publish/stock/index.html

def parse_stock_md(md_path, date_str) -> dict:
    """MD에서 지수표·온도계·키워드 추출 (구조화 데이터)."""

def build_stock_ctx(md_path, date_str, data) -> dict:
    """stock 전용 ctx — themes.render_stock_report(ctx)에 전달."""

def build_stock(theme_name=None) -> None:
    """stock MD 전체 빌드 → publish/stock/ 생성."""
```

### 5-6. `scripts/stock_main.py`

```python
# 진입점 — main.py 패턴 동일
def main():
    # 1. 데이터 수집    (core/stock_collector.py)
    # 2. AI 분석        (core/stock_analyzer.py)
    # 3. MD 저장        (core/stock_report.py → reports/stock/)
    # 4. 이메일 발송    (core/mailer.py — 기존 그대로)
    # 5. HTML 빌드      (scripts/build_stock_site.py)
    # Notion은 제외 (MCP 전용)
```

---

## 6. GitHub Actions 워크플로우 설계

### `.github/workflows/stock.yml`

```yaml
name: Stock Briefing

on:
  schedule:
    - cron: '30 07 * * 1-5'   # UTC 07:30 = KST 16:30 (월~금, KOSPI 장 마감 후)
  workflow_dispatch:             # 수동 실행 가능

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  stock:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -r requirements.txt

      - name: 주식 데이터 수집 및 리포트 생성
        run: python scripts/stock_main.py
        env:
          LLM_PROVIDER:       ${{ secrets.LLM_PROVIDER }}
          GEMINI_API_KEY:     ${{ secrets.GEMINI_API_KEY }}
          GMAIL_USER:         ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAILS:   ${{ secrets.RECIPIENT_EMAILS }}
          SITE_BASE_URL:      ${{ secrets.SITE_BASE_URL }}
          NAVER_CLIENT_ID:    ${{ secrets.NAVER_CLIENT_ID }}    # 신규 추가 필요
          NAVER_CLIENT_SECRET:${{ secrets.NAVER_CLIENT_SECRET }} # 신규 추가 필요

      - name: 사이트 빌드 (stock MD → HTML)
        run: python scripts/build_stock_site.py

      - name: 커밋 + 푸시
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "actions@github.com"
          git add reports/stock/ publish/stock/
          git diff --staged --quiet || \
            git commit -m "📊 Stock briefing $(date +'%Y-%m-%d')"
          git push

      - name: GitHub Pages 배포
        uses: actions/upload-pages-artifact@v3
        with:
          path: publish/

      - name: Deploy
        uses: actions/deploy-pages@v4
```

**스케줄 근거:**
- KST 16:30 (UTC 07:30): KOSPI 장 마감(15:30) + 1시간 여유 → 당일 국내 시장 데이터 확정
- 미국 시장 데이터: 전일 종가 (yfinance에서 이미 확정값 제공)
- 월~금만 실행 (`1-5`): 주말·공휴일 제외

---

## 7. 테마/디자인 시스템 연동

### 기존 `config/theme_config.py` 수정 (최소)

```python
# NAV_SECTIONS: stock enabled: False → True
{"key": "stock", "label": "📈 주식", "url": "stock/index.html", "enabled": True},

# HUB_SECTIONS: stock enabled: False → True
{"key": "stock", ..., "enabled": True},
```

### `themes/base.py` 추가 함수

```python
def render_stock_report(ctx: dict, theme_name: str) -> str:
    """주식 리포트 전용 렌더러.
    - 지수표: 등락률 색상 (양수=green, 음수=red)
    - 온도계: 🔴/🟡/🟢 배지
    - 섹터 표: 색상 coded rows
    ctx 계약: build_stock_ctx()와 동일 키 사용
    """

def render_stock_email(ctx: dict, theme_name: str) -> str:
    """주식 이메일 전용 렌더러 (인라인 스타일).
    Gmail 102KB 클리핑 방지: 핵심 요약 + 지수표 + 키워드만 포함.
    """
```

### `publish/stock/` 디렉토리 구조

```
publish/stock/
  index.html          ← 최신 주식 브리핑 (stock/index.html)
  2026-05-18.html     ← 날짜별 아카이브
  archive.html        ← 전체 목록
  stock-data.json     ← 동적 데이터 (app.html 연동용)
```

---

## 8. 신규 GitHub Secrets 등록 필요

| Secret 키 | 용도 | 비고 |
|-----------|------|------|
| `NAVER_CLIENT_ID` | Naver News API | developers.naver.com 앱 등록 필요 |
| `NAVER_CLIENT_SECRET` | Naver News API | 동일 |

**기존 시크릿 재사용 (추가 등록 불필요):**
`LLM_PROVIDER`, `GEMINI_API_KEY`, `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `RECIPIENT_EMAILS`, `SITE_BASE_URL`

---

## 9. MD 구조 파싱 설계 (build_stock_site.py용)

현재 뉴스 시스템과 동일한 패턴으로, stock MD에서 구조화 데이터 추출:

```python
# 온도계 파싱: "🔴 리스크오프" | "🟡 중립" | "🟢 리스크온"
temperature_m = re.search(r'시장 온도계.*?(🔴|🟡|🟢)\s*(\S+)', raw)

# 지수표 파싱
kospi_m = re.search(r'\| 코스피 \| ([\d,\.]+) \| ([+-]?[\d\.]+)%', raw)

# 키워드 파싱: ## 3. 핵심 키워드 TOP 5 → ### 각 키워드
keywords = re.findall(r'### (.+?)\n([\s\S]*?)(?=###|##|\Z)', analysis_block)
```

---

## 10. 구현 순서 (Phase 3 단계)

```
Phase 3-A: 데이터 수집 + MD 생성 (핵심 파이프라인)
  1. requirements.txt에 yfinance 추가
  2. core/stock_collector.py 구현
  3. config/stock_prompts.py 작성
  4. core/stock_analyzer.py 구현
  5. templates/stock_report.md 작성
  6. core/stock_report.py 구현
  7. scripts/stock_main.py 작성
  → 로컬 테스트: python scripts/stock_main.py

Phase 3-B: HTML 빌드 + 사이트 연동
  8. scripts/build_stock_site.py 구현
  9. themes/base.py에 render_stock_report/email 추가
  10. config/theme_config.py stock enabled: True
  → 로컬 테스트: python scripts/build_stock_site.py

Phase 3-C: GitHub Actions 자동화
  11. .github/workflows/stock.yml 작성
  12. GitHub Secrets에 NAVER_CLIENT_ID/SECRET 등록
  13. workflow_dispatch로 수동 테스트
  → 성공 확인 후 스케줄 활성화

Phase 3-D: Notion (별도, 수동 or MCP)
  - GitHub Actions 범위 밖
  - Claude Code 웹에서 수동 실행 유지
  - 또는 Notion API 직접 호출로 추후 자동화 검토
```

---

## 11. 기존 뉴스 시스템과의 차이점 요약

| 항목 | 뉴스 시스템 | 주식 시스템 |
|------|-----------|-----------|
| 데이터 수집 | feedparser (RSS) | yfinance + Naver News API |
| 분석 입력 | 기사 제목+요약 텍스트 | 수치 데이터 + 뉴스 헤드라인 |
| MD 템플릿 | templates/daily_report.md | templates/stock_report.md |
| 빌드 스크립트 | scripts/build_site.py | scripts/build_stock_site.py |
| 출력 경로 | reports/news_*.md / publish/*.html | reports/stock/stock_*.md / publish/stock/*.html |
| Actions 실행 시각 | UTC 02:00 (KST 11:00) | UTC 07:30 (KST 16:30, 장 마감 후) |
| 이메일 제목 | 📰 Daily News Brief — {date} | 📊 주식 시황 브리핑 — {date} ({요일}) |
| Notion 연동 | 없음 | 수동 MCP 유지 |

---

## 12. 미결 사항 (구현 전 확인 필요)

1. **Naver API 키**: developers.naver.com에서 앱 등록 후 `검색` API 권한 부여 필요  
   → 없을 경우 대안: `FinanceDataReader` 또는 Yahoo Finance news 사용

2. **yfinance 한국 지수 안정성**: `^KS11`(코스피), `^KQ11`(코스닥) 장 마감 후 15~30분 딜레이  
   → 오류 시 fallback: 전일 종가 사용 + 리포트에 명시

3. **이메일 제목 포맷**: `settings.py`의 `EMAIL_SUBJECT`는 뉴스용  
   → `STOCK_EMAIL_SUBJECT = "📊 주식 시황 브리핑 — {date} ({weekday})"` 별도 추가

4. **기존 reports/stock/ 파일**: 현재 `stock_2026-05-18.md` 1개 존재 (Claude 웹 루틴 생성)  
   → build_stock_site.py가 이 파일도 빌드 가능하도록 파서 설계 필요 (기존 형식 호환)
