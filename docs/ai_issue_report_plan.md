# AI Issue Report — 구현 계획 초안

> **작성일**: 2026-05-27  
> **목적**: 주간 AI 동향 전문 분석 서비스 (`ai-issue`) 추가 설계  
> **기조**: 기존 news/stock 패턴을 최대한 재사용, 새 코드 최소화

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 발행 주기 | **주 1회** (매주 월요일 KST 07:00) |
| 분석 범위 | 직전 7일간 AI 관련 이슈 |
| 주요 콘텐츠 | 이번 주 이슈 TOP 10, 심층 설명, 차주 전망, AI 기업 동향 |
| 출력 | 웹사이트(HTML) + 이메일 + Telegram + Markdown 보고서 |
| 파일 식별자 | `YYYY-WNN` 형식 (예: `2026-W22`) |

---

## 2. 콘텐츠 구조

### 2-1. 주간 보고서 섹션 구성

```
📰 AI Issue Weekly — 2026년 22주차 (05.25 ~ 05.31)
├── 🔝 이번 주 AI 이슈 TOP 10
│   ├── 1. 이슈명 | 카테고리 | 중요도 ★★★★★
│   ├── 2. ...
│   └── 10. ...
│
├── 🔍 주요 이슈 심층 분석 (TOP 3)
│   ├── Issue #1: 상세 배경 / 내용 / 의미 / 파급효과
│   ├── Issue #2: ...
│   └── Issue #3: ...
│
├── 🏢 AI 기업·서비스 동향 요약
│   ├── OpenAI / Anthropic / Google / Meta / MS
│   └── 국내 기업 동향
│
├── 📊 이슈 카테고리 분포
│   └── 모델출시 / 서비스 / 연구 / 규제·정책 / 산업응용
│
└── 🔮 차주 전망
    ├── 주목해야 할 예정 이벤트
    ├── 진행 중 이슈 추이
    └── 전문가 시각 요약
```

### 2-2. 이슈 카테고리

| 코드 | 설명 | 아이콘 |
|------|------|--------|
| `model` | 모델 출시·업데이트 | 🤖 |
| `service` | 서비스·제품 출시 | 🚀 |
| `research` | 논문·연구 성과 | 🔬 |
| `policy` | 규제·정책·윤리 | ⚖️ |
| `industry` | 산업·비즈니스 적용 | 🏭 |
| `infra` | 인프라·칩·데이터센터 | 🖥️ |

---

## 3. 폴더 구조 (신규 추가 경로)

```
dailynews/
│
├── core/
│   └── ai_issue/                    ← 신규
│       ├── __init__.py
│       ├── collector.py             ← AI 전문 소스 수집
│       ├── analyzer.py              ← 주간 분석, TOP 10 선정
│       └── report.py               ← 보고서 생성 (MD + JSON)
│
├── config/
│   ├── ai_issue_prompts.py          ← 신규: AI 이슈 분석 프롬프트
│   └── ai_issue_sources.py         ← 신규: AI 전문 RSS 소스 목록
│
├── scripts/
│   ├── run_ai_issue.py             ← 신규: 주간 실행 진입점
│   ├── build_ai_issue_site.py      ← 신규: HTML 빌드
│   └── send_ai_issue_email.py      ← 신규: 이메일 발송
│
├── templates/
│   ├── ai_issue_report.md          ← 신규: 보고서 MD 템플릿
│   ├── email_ai_issue.html         ← 신규: 이메일 템플릿
│   └── web_ai_issue.html           ← 신규: 웹 렌더 템플릿 (선택)
│
├── reports/
│   └── ai-issue/                   ← 신규
│       ├── ai_issue_2026-W22.md
│       └── ai_issue_2026-W22.json
│
├── publish/
│   └── ai-issue/                   ← 신규 (gitignore + force-add)
│       ├── index.html              ← 최신 이슈 + 목록
│       ├── archive.html            ← 전체 아카이브
│       ├── ai-issue-data.json      ← 인덱스 (메타데이터)
│       ├── 2026-W22.html
│       └── 2026-W22.json          ← lazy-load 용 본문 데이터
│
└── .github/workflows/
    └── ai_issue.yml                ← 신규: 주간 워크플로우
```

---

## 4. 데이터 소스 (AI 전문 RSS)

기존 `config/rss_sources.py`에서 AI 카테고리 분리·보강:

| 소스 | URL | 분류 |
|------|-----|------|
| OpenAI Blog | https://openai.com/news/rss | model/service |
| Anthropic News | https://www.anthropic.com/news/rss | model/policy |
| Google AI Blog | https://blog.google/technology/ai/rss | model/research |
| Hugging Face Blog | https://huggingface.co/blog/feed.xml | research/model |
| arXiv cs.AI | http://arxiv.org/rss/cs.AI | research |
| arXiv cs.LG | http://arxiv.org/rss/cs.LG | research |
| MIT Tech Review AI | https://www.technologyreview.com/feed/ | industry/policy |
| VentureBeat AI | https://venturebeat.com/ai/feed/ | service/industry |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed | service/industry |
| The Verge AI | https://www.theverge.com/ai-artificial-intelligence/rss/index.xml | service |
| 테크크런치 Korea | (필요시) | 국내 |
| AI타임스 | https://www.aitimes.com/rss/allArticle.xml | 국내 |

---

## 5. 핵심 모듈 설계

### 5-1. `core/ai_issue/collector.py`

```python
# 역할: AI 전문 RSS 수집 + 기존 뉴스에서 AI 기사 필터링
# 수집 범위: 직전 7일 (월~일)
# 출력: List[dict] — title, url, source, date, category_hint, summary_raw

def collect_weekly(start_date, end_date) -> List[dict]:
    # 1. AI 전문 RSS 피드 수집
    # 2. 기존 수집된 뉴스에서 AI 키워드 필터링 (중복 활용)
    # 3. 중복 제거 (URL 기준)
    # 4. 날짜 필터링 (start_date ~ end_date)
    ...
```

### 5-2. `core/ai_issue/analyzer.py`

```python
# 역할: 수집된 기사들 → AI로 주간 분석
# 프롬프트: config/ai_issue_prompts.py 참조
# 출력: IssueReport (dataclass)

@dataclass
class IssueItem:
    rank: int
    title: str
    category: str          # model/service/research/policy/industry/infra
    importance: int        # 1~5
    summary: str           # 2~3줄 요약
    detail: str            # 심층 분석 (TOP 3만)
    sources: List[str]     # 관련 기사 URL

@dataclass
class IssueReport:
    week_id: str           # "2026-W22"
    period: str            # "2026-05-25 ~ 2026-05-31"
    top10: List[IssueItem]
    company_trends: str    # 기업별 동향 (마크다운)
    next_week_outlook: str # 차주 전망 (마크다운)
    category_stats: dict   # 카테고리별 이슈 수
    generated_at: str
```

### 5-3. `core/ai_issue/report.py`

```python
# 역할: IssueReport → MD 파일 + JSON 파일 저장
# MD: reports/ai-issue/ai_issue_YYYY-WNN.md
# JSON: reports/ai-issue/ai_issue_YYYY-WNN.json

def generate(report: IssueReport):
    # Jinja2 템플릿(ai_issue_report.md) 렌더링
    # JSON 저장 (구조화 데이터)
    ...
```

---

## 6. 프롬프트 설계 (`config/ai_issue_prompts.py`)

```python
ISSUE_ANALYSIS_PROMPT = """
당신은 AI 산업 전문 애널리스트입니다.

아래는 {start_date}부터 {end_date}까지 수집된 AI 관련 뉴스 {count}건입니다.

[수집 뉴스]
{news_list}

다음 형식으로 주간 AI 이슈 보고서를 작성하세요:

1. **이번 주 AI 이슈 TOP 10**
   각 이슈: 순위 | 제목 | 카테고리(model/service/research/policy/industry/infra) | 중요도(1-5) | 2줄 요약

2. **주요 이슈 심층 분석** (TOP 3)
   각 이슈: 배경, 핵심 내용, 산업적 의미, 파급효과

3. **AI 기업·서비스 동향** (OpenAI, Anthropic, Google, Meta, MS, 국내 기업 순)

4. **차주 전망**
   - 주목 이벤트 (예정된 발표, 컨퍼런스 등)
   - 진행 중 이슈 모니터링 포인트
   - 시장/기술 방향성 예측

출력은 한국어로, 전문가 리포트 톤으로 작성하세요.
"""
```

---

## 7. 워크플로우 (`ai_issue.yml`)

```yaml
name: AI Issue Weekly Report

on:
  schedule:
    - cron: '0 22 * * 0'   # UTC 22:00 일요일 = KST 월요일 07:00
  workflow_dispatch:
    inputs:
      week:
        description: '대상 주 (예: 2026-W22). 미입력 시 자동 계산'
        required: false

concurrency:
  group: pages-deploy
  cancel-in-progress: false

permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  ai_issue:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Python 설정 (3.11)
      - 패키지 설치
      - AI 이슈 수집·분석·보고서 생성
          run: python scripts/run_ai_issue.py
      - HTML 빌드
          run: python scripts/build_ai_issue_site.py
      - 뉴스 사이트도 함께 빌드 (app.html ai-issue 탭 반영)
          run: python scripts/build_site.py --from $(date +'%Y-%m-%d')
      - 이메일 발송
          run: python scripts/send_ai_issue_email.py
      - 커밋 + 푸시
      - GitHub Pages 배포
```

---

## 8. 사이트 통합 (`app.html`)

### 8-1. 네비게이션 탭 추가

```
[뉴스클리핑] [AI이슈] [주식시황]
```

- 기존 `.hnav-tab` 구조에 `ai-issue` 섹션 탭 추가
- `config/theme_config.py` NAV_ITEMS에 `ai-issue` 항목 추가

### 8-2. 사이드바

```
┌─────────────────┐
│ AI 이슈         │
│ 최신: 2026-W22  │
├─────────────────┤
│ 2026-W22 ●     │
│ 2026-W21       │
│ 2026-W20       │
│ ...            │
└─────────────────┘
```

- 왼쪽 사이드바: 주차별 목록 (날짜 목록 대신)
- 오른쪽 메인: 선택 주차 보고서 렌더링

### 8-3. 보고서 렌더링 컴포넌트 (JS)

```javascript
// TOP 10 카드 (순위 뱃지 + 카테고리 태그 + 중요도 별점)
function renderIssueCard(issue) { ... }

// 심층 분석 아코디언 (접기/펼치기)
function renderIssueDetail(issue) { ... }

// 기업 동향 섹션
function renderCompanyTrends(trends) { ... }

// 차주 전망 섹션
function renderOutlook(outlook) { ... }
```

---

## 9. 이메일 템플릿 (`email_ai_issue.html`)

```
Subject: 🤖 AI 위클리 이슈 — 2026년 22주차

[헤더] AI Issue Weekly
[부제] 2026.05.25 ~ 2026.05.31

[섹션 1] 이번 주 TOP 3 이슈 (카드 형태)
[섹션 2] 이번 주 이슈 목록 (4~10위, 심플 리스트)
[섹션 3] 차주 전망 한 줄 요약
[푸터] 전체 보고서 보기 링크 | 구독취소
```

- 기존 `email_news.html` 구조 재사용
- 웹메일 호환: 인라인 스타일 유지

---

## 10. `.gitignore` 추가

```
publish/ai-issue/20??-W??.html
publish/ai-issue/20??-W??.json
```

force-add 패턴 (워크플로우):
```yaml
git add -f publish/ai-issue/$(python -c "import datetime; d=datetime.date.today(); print(f'{d.year}-W{d.isocalendar()[1]:02d}')").html
```

---

## 11. 구현 단계 (Phase)

| Phase | 작업 | 예상 시간 | 우선순위 |
|-------|------|-----------|---------|
| **Phase 1** | RSS 소스 정의 + collector.py | 2h | ⭐⭐⭐ |
| **Phase 2** | analyzer.py + 프롬프트 설계 | 3h | ⭐⭐⭐ |
| **Phase 3** | report.py + 템플릿(MD/JSON) | 1h | ⭐⭐⭐ |
| **Phase 4** | build_ai_issue_site.py + HTML | 3h | ⭐⭐⭐ |
| **Phase 5** | app.html 탭·사이드바 통합 | 2h | ⭐⭐ |
| **Phase 6** | 이메일 템플릿 + 발송 스크립트 | 1h | ⭐⭐ |
| **Phase 7** | ai_issue.yml 워크플로우 | 1h | ⭐⭐⭐ |
| **Phase 8** | Telegram 발송 통합 | 0.5h | ⭐ |
| **전체** | | **약 13~14h** | |

---

## 12. 미결 결정 사항

작업 시작 전 확인이 필요한 항목:

| # | 항목 | 옵션 A | 옵션 B |
|---|------|--------|--------|
| 1 | **파일 식별자** | `YYYY-WNN` (ISO 주차) | `YYYY-MM-DD` (월요일 날짜) |
| 2 | **사이트 통합 방식** | app.html 탭에 통합 | `/ai-issue/index.html` 별도 페이지 |
| 3 | **수집 방식** | AI 전용 RSS + 기존 뉴스 AI 필터 | AI 전용 RSS만 |
| 4 | **언어** | 한국어만 | 영문 소스 → 한국어 요약 |
| 5 | **심층 분석 깊이** | TOP 3 상세 | TOP 5 중간 수준 |
| 6 | **첫 발행 시점** | 즉시 (수동 트리거) | 다음 주 월요일 |

---

## 13. 기존 코드 재사용 계획

| 기존 모듈 | 재사용 방식 |
|-----------|-------------|
| `core/shared/mailer.py` | 이메일 발송 그대로 사용 |
| `core/shared/telegram.py` | Telegram 발송 그대로 사용 |
| `core/news/collector.py` | RSS 수집 로직 참고 (상속/복사) |
| `scripts/build_site.py` | HTML 빌드 패턴 동일하게 적용 |
| `themes/*.py` | 동일 테마 시스템 적용 |
| `config/theme_config.py` | SECTION_THEMES에 `"ai-issue"` 추가 |
| `publish/app.html` | 탭 + 렌더 함수 패턴 재사용 |

---

*이 문서는 구현 전 검토용 초안입니다. Phase 진행 전 미결 결정 사항 확인 후 착수 권장.*
