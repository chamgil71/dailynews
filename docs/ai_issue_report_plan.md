# AI Issue Report — 구현 계획

> **작성일**: 2026-05-27 (v2 업데이트)  
> **목적**: 주간 AI 동향 전문 분석 서비스 (`ai-issue`) 추가 설계  
> **기조**: 기존 news/stock 패턴 최대 재사용, 새 코드 최소화

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 발행 주기 | **주 1회** — 일요일 KST 07:00 실행, **월요일 08:00 이전 완료** |
| 분석 범위 | 직전 월~일(7일)간 AI 관련 이슈 |
| 파일 식별자 | **`YYYY-MM-DD` (해당 주 일요일 날짜)** — 예: `2026-06-01` |
| 사이트 통합 | **app.html 탭 통합** (뉴스클리핑 \| AI이슈 \| 주식시황) |
| 출력 | 웹사이트(HTML) + 이메일 + Telegram + Markdown 보고서 |

---

## 2. 콘텐츠 구조 (확정)

### 2-1. 주간 보고서 전체 섹션

```
🤖 AI Issue Weekly — 2026.05.25 ~ 2026.05.31
│
├── [A] 🔝 이번 주 AI 이슈 TOP 10
│         순위 · 카테고리 · 중요도 ★★★★★ · 2줄 요약
│
├── [B] 🔍 주요 이슈 심층 분석 (TOP 3)          ← 확정 포함
│         각 이슈: 배경 / 핵심 내용 / 산업적 의미 / 파급효과 / 출처
│
├── [C] 🏢 AI 기업·서비스 동향
│         OpenAI / Anthropic / Google / Meta / MS / 국내 기업
│
├── [D] 💡 AI 실용 팁 (Weekly Tip)               ← 신규 추가
│         독자가 당장 활용 가능한 AI 도구/기능/프롬프트 2~3개
│         예: "Claude에서 이렇게 쓰면 더 좋아진다", "Gemini 새 기능 활용법"
│
├── [E] 📈 AI 투자·펀딩 동향                      ← 신규 추가
│         주간 AI 기업 VC 펀딩·M&A 소식
│         AI 관련 주요 종목 주간 등락 (NVDA, MSFT, GOOGL, META 등)
│         기존 주식 모듈 데이터 연계 가능
│
├── [F] 🔬 주목 논문 Pick (Research Radar)        ← 신규 추가
│         arXiv·HF Papers에서 주간 주목 논문 2~3편
│         한줄 요약 + 실무 적용 가능성 코멘트
│
├── [G] 📊 이슈 카테고리 분포
│         모델출시 / 서비스 / 연구 / 규제·정책 / 산업응용 / 인프라
│
└── [H] 🔮 차주 전망
          예정 이벤트 (컨퍼런스, 발표 예고 등)
          진행 중 이슈 모니터링 포인트
          시장·기술 방향성 예측
```

### 2-2. 섹션별 판단 근거

| 섹션 | 포함 이유 | 구현 난이도 |
|------|-----------|-------------|
| A. TOP 10 | 핵심 가치, 빠른 파악 | 중 |
| B. 심층 분석 | 차별화 포인트, 전문성 | 높음 |
| C. 기업 동향 | 독자 관심도 최상위 | 중 |
| D. 실용 팁 | 즉시 활용 가능 → 구독 유지율↑ | 낮음 |
| E. 투자 동향 | 주식 모듈과 시너지, 경제 독자층 확보 | 낮음 (재사용) |
| F. 논문 Pick | 기술 독자층 확보, 신뢰도↑ | 낮음 |
| G. 카테고리 분포 | 한눈에 이번 주 색깔 파악 | 낮음 |
| H. 차주 전망 | 연속성·재방문 동기 | 중 |

> **보류 섹션**: AI 도구 리뷰(조사 비용 높음), 국내 정책 단독 섹션(C에 통합), AI 인물 스포트라이트(격주 검토)

### 2-3. 이슈 카테고리

| 코드 | 설명 | 아이콘 |
|------|------|--------|
| `model` | 모델 출시·업데이트·벤치마크 | 🤖 |
| `service` | 서비스·제품·기능 출시 | 🚀 |
| `research` | 논문·연구·기술 성과 | 🔬 |
| `policy` | 규제·정책·윤리·안전 | ⚖️ |
| `industry` | 산업·비즈니스·파트너십 | 🏭 |
| `infra` | 인프라·칩·데이터센터·전력 | 🖥️ |
| `investment` | 투자·펀딩·M&A | 💰 |

---

## 3. 데이터 소스 (AI 전문 사이트 + RSS)

### 3-1. AI 기업 공식 블로그

| 소스 | RSS URL | 카테고리 |
|------|---------|---------|
| OpenAI Blog | `https://openai.com/news/rss` | model/service |
| Anthropic News | `https://www.anthropic.com/news/rss` | model/policy |
| Google DeepMind | `https://deepmind.google/blog/rss/` | model/research |
| Google AI Blog | `https://blog.google/technology/ai/rss` | model/service |
| Meta AI Blog | `https://ai.meta.com/blog/rss/` | model/research |
| Microsoft AI | `https://blogs.microsoft.com/ai/feed/` | service/industry |
| Mistral AI | `https://mistral.ai/news/rss` | model |
| Cohere Blog | `https://cohere.com/blog/rss` | model/service |
| Hugging Face Blog | `https://huggingface.co/blog/feed.xml` | model/research |

### 3-2. AI 전문 미디어

| 소스 | RSS URL | 특징 |
|------|---------|------|
| **The Decoder** | `https://the-decoder.com/feed/` | AI 전문, 깊이 있는 기술 분석 |
| **AI News** | `https://www.artificialintelligence-news.com/feed/` | AI 산업 뉴스 전문 |
| **Ars Technica AI** | `https://feeds.arstechnica.com/arstechnica/index` | 기술 심층 분석 |
| **404 Media** | `https://www.404media.co/rss/` | AI 이슈 심층 취재 |
| VentureBeat AI | `https://venturebeat.com/ai/feed/` | 서비스·비즈니스 |
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | 펀딩·스타트업 |
| The Verge AI | `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml` | 제품·소비자 |
| Wired AI | `https://www.wired.com/feed/tag/ai/latest/rss` | 사회·윤리 |
| MIT Tech Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed` | 연구·정책 |

### 3-3. 연구·논문

| 소스 | URL | 특징 |
|------|-----|------|
| **arXiv cs.AI** | `http://arxiv.org/rss/cs.AI` | AI 전반 |
| **arXiv cs.LG** | `http://arxiv.org/rss/cs.LG` | 머신러닝 |
| arXiv cs.CL | `http://arxiv.org/rss/cs.CL` | NLP/LLM |
| arXiv cs.CV | `http://arxiv.org/rss/cs.CV` | 컴퓨터 비전 |
| **HF Daily Papers** | `https://huggingface.co/papers/rss` | 커뮤니티 선별 주목 논문 |
| Papers With Code | `https://paperswithcode.com/latest/rss` | 코드 공개 논문 |

### 3-4. 국내 AI 미디어

| 소스 | RSS URL | 특징 |
|------|---------|------|
| **AI타임스** | `https://www.aitimes.com/rss/allArticle.xml` | AI 전문 국내 매체 |
| **전자신문** | `https://rss.etnews.com/Section901.xml` | IT/AI 산업 |
| ZDNet Korea | `https://zdnet.co.kr/rss/news.xml` | 기술 전반 |
| Bloter | `https://www.bloter.net/feed` | 스타트업·서비스 |

### 3-5. 투자·펀딩 (E섹션 전용)

| 소스 | 방식 | 데이터 |
|------|------|--------|
| Crunchbase | 웹 스크래핑 또는 API | AI 기업 펀딩 |
| TechCrunch (funding) | `https://techcrunch.com/tag/funding/feed/` | AI 투자 소식 |
| 기존 `yfinance` 모듈 | 코드 재사용 | NVDA/MSFT/GOOGL/META/AMD 주가 |

> **수집 전략**: AI 전용 RSS + 기존 일일 뉴스에서 AI 키워드 필터링 병행  
> **우선순위**: bold 표시 소스 우선 구현, 나머지 점진적 추가

---

## 4. 폴더 구조 (신규 추가 경로)

```
dailynews/
│
├── core/
│   └── ai_issue/                    ← 신규
│       ├── __init__.py
│       ├── collector.py             ← AI 소스 수집 + 기존 뉴스 AI 필터
│       ├── analyzer.py              ← 주간 분석, TOP 10, 섹션별 생성
│       └── report.py               ← MD + JSON 보고서 저장
│
├── config/
│   ├── ai_issue_prompts.py          ← 신규: 섹션별 프롬프트
│   └── ai_issue_sources.py         ← 신규: AI 전문 RSS 소스 목록
│
├── scripts/
│   ├── run_ai_issue.py             ← 신규: 주간 실행 진입점
│   ├── build_ai_issue_site.py      ← 신규: HTML 빌드
│   └── send_ai_issue_email.py      ← 신규: 이메일 발송
│
├── templates/
│   ├── ai_issue_report.md          ← 신규: 보고서 MD 템플릿
│   └── email_ai_issue.html         ← 신규: 이메일 템플릿
│
├── reports/
│   └── ai-issue/                   ← 신규
│       ├── ai_issue_2026-06-01.md  (일요일 날짜 기준)
│       └── ai_issue_2026-06-01.json
│
├── publish/
│   └── ai-issue/                   ← 신규 (gitignore + force-add)
│       ├── index.html              ← 최신 이슈 + 목록
│       ├── archive.html            ← 전체 아카이브
│       ├── ai-issue-data.json      ← 인덱스 메타데이터
│       ├── 2026-06-01.html         ← 날짜별 이슈 페이지
│       └── 2026-06-01.json         ← lazy-load 본문 데이터
│
└── .github/workflows/
    └── ai_issue.yml                ← 신규: 주간 워크플로우
```

---

## 5. 핵심 모듈 설계

### 5-1. `core/ai_issue/collector.py`

```python
# 역할: AI 전문 RSS 수집 + 기존 뉴스에서 AI 기사 필터링
# 수집 범위: 해당 주 월~일 (7일)
# 출력: List[dict] — title, url, source, date, category_hint, content_raw

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "Gemini", "인공지능", "머신러닝", ...]

def collect_weekly(start_date, end_date) -> List[dict]:
    articles = []
    # 1. AI 전문 RSS 피드 직접 수집 (ai_issue_sources.py 소스 목록)
    # 2. reports/news_YYYY-MM-DD.json에서 AI 키워드 필터링 (일일 뉴스 재활용)
    # 3. arXiv/HF Papers → 논문 전용 수집 (F섹션)
    # 4. yfinance → AI 관련 종목 주가 (E섹션)
    # 5. 중복 제거 (URL 해시 기준), 날짜 필터링
    return deduplicate(articles)
```

### 5-2. `core/ai_issue/analyzer.py`

```python
@dataclass
class IssueItem:
    rank: int
    title: str
    category: str          # model/service/research/policy/industry/infra/investment
    importance: int        # 1~5
    summary: str           # 2~3줄 요약
    detail: str            # 심층 분석 (TOP 3만)
    sources: List[str]

@dataclass
class PaperItem:
    title: str
    authors: str
    one_liner: str         # 한줄 요약
    practical_note: str    # 실무 적용 가능성
    url: str

@dataclass
class StockSnapshot:
    ticker: str
    name: str
    weekly_change_pct: float
    note: str              # 주간 특이 사항

@dataclass
class IssueReport:
    issue_date: str        # "2026-06-01" (일요일)
    period: str            # "2026-05-26 ~ 2026-06-01"
    top10: List[IssueItem]
    company_trends: str
    weekly_tip: str        # D섹션
    investment_summary: str    # E섹션
    stock_snapshots: List[StockSnapshot]
    paper_picks: List[PaperItem]    # F섹션
    category_stats: dict
    next_week_outlook: str
    generated_at: str
```

### 5-3. `config/ai_issue_prompts.py` (섹션별 분리)

```python
# A+B: TOP 10 + 심층 분석
MAIN_ANALYSIS_PROMPT = """..."""

# C: 기업 동향
COMPANY_TRENDS_PROMPT = """..."""

# D: 실용 팁
WEEKLY_TIP_PROMPT = """
이번 주 AI 뉴스를 바탕으로 독자가 당장 활용할 수 있는 실용 AI 팁 2~3개를 작성하세요.
각 팁: 제목 | 도구명 | 활용법 (3줄) | 난이도(초급/중급/고급)
..."""

# F: 논문 Pick
PAPER_PICK_PROMPT = """
arXiv/HF Papers에서 수집된 논문 목록에서 주목할 논문 2~3편을 선정하세요.
각 논문: 제목 | 한줄 요약 | 실무 적용 가능성 (있음/제한적/없음) | 이유
..."""

# H: 차주 전망
OUTLOOK_PROMPT = """..."""
```

---

## 6. 워크플로우 (`ai_issue.yml`)

```yaml
name: AI Issue Weekly Report

on:
  schedule:
    # UTC 토요일 22:00 = KST 일요일 07:00 실행 → 월요일 08:00 이전 완료
    - cron: '0 22 * * 6'
  workflow_dispatch:
    inputs:
      target_date:
        description: '발행 기준 일요일 날짜 (예: 2026-06-01). 미입력 시 자동'
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
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Python 설정
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: 패키지 설치
        run: pip install -r requirements.txt

      - name: AI 이슈 수집·분석·보고서 생성
        run: python scripts/run_ai_issue.py
        env:
          LLM_PROVIDER:        ${{ secrets.LLM_PROVIDER }}
          GEMINI_API_KEY:      ${{ secrets.GEMINI_API_KEY }}
          ANTHROPIC_API_KEY:   ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY:      ${{ secrets.OPENAI_API_KEY }}

      - name: HTML 빌드
        run: python scripts/build_ai_issue_site.py
        env:
          SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}

      - name: 통합 사이트 빌드 (app.html ai-issue 탭 반영)
        run: python scripts/build_site.py --from $(date +'%Y-%m-%d')
        env:
          SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}

      - name: 이메일 발송
        run: python scripts/send_ai_issue_email.py
        env:
          GMAIL_USER:         ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAILS:   ${{ secrets.RECIPIENT_EMAILS }}
          SITE_BASE_URL:      ${{ secrets.SITE_BASE_URL }}

      - name: Telegram 발송
        run: python -c "
          from core.shared.telegram import send_message
          # 요약 메시지 전송
        "
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID:   ${{ secrets.TELEGRAM_CHAT_ID }}

      - name: 커밋 + 푸시
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "actions@github.com"
          git add reports/ai-issue/
          ISSUE_DATE=$(TZ=Asia/Seoul date +'%Y-%m-%d')
          git add -f publish/ai-issue/${ISSUE_DATE}.html \
                     publish/ai-issue/${ISSUE_DATE}.json 2>/dev/null || true
          git add -f publish/ai-issue/index.html \
                     publish/ai-issue/archive.html \
                     publish/ai-issue/ai-issue-data.json 2>/dev/null || true
          git add -f publish/app.html publish/index.html 2>/dev/null || true
          git diff --staged --quiet || \
            git commit -m "🤖 AI Issue Weekly $(date +'%Y-%m-%d')"
          git pull --rebase --autostash origin main
          git push

      - name: GitHub Pages 배포
        uses: actions/upload-pages-artifact@v3
        with:
          path: publish/

      - name: Deploy to GitHub Pages
        id: deploy
        uses: actions/deploy-pages@v4
```

---

## 7. 사이트 통합 (`app.html` 탭 통합)

### 7-1. 네비게이션 탭

```
[ 뉴스클리핑 ]  [ 🤖 AI이슈 ]  [ 주식시황 ]
```

- `config/theme_config.py` NAV_ITEMS에 `ai-issue` 추가
- 섹션 테마: `SECTION_THEMES["ai-issue"] = "editorial"` (기본값)
- localStorage: `theme-ai-issue`

### 7-2. AI이슈 섹션 사이드바

```
┌──────────────────┐
│ 🤖 AI 이슈       │
│ 최신: 06-01      │
├──────────────────┤
│ 2026-06-01  ●   │  ← 이번 주 (일요일 날짜)
│ 2026-05-25      │
│ 2026-05-18      │
│ ...             │
└──────────────────┘
```

### 7-3. 메인 렌더링 컴포넌트 (JS)

```javascript
// 뉴스 날짜 클릭 → lazy-load (기존 패턴 동일)
async function selectAIIssueDate(dateStr) {
  if (!state.aiIssueCache[dateStr]) {
    const data = await fetch(`/ai-issue/${dateStr}.json`).then(r => r.json());
    state.aiIssueCache[dateStr] = data;
  }
  renderAIIssueReport(state.aiIssueCache[dateStr]);
}

// TOP 10 카드 렌더링
function renderIssueCard(issue) { ... }       // 순위뱃지 + 카테고리태그 + 별점

// 심층 분석 아코디언 (접기/펼치기)
function renderIssueDetail(issue) { ... }

// 실용 팁 카드
function renderWeeklyTip(tip) { ... }

// 투자·주가 스냅샷
function renderStockSnapshot(stocks) { ... } // 기존 주식 카드 스타일 재사용

// 논문 픽
function renderPaperPick(papers) { ... }

// 차주 전망
function renderOutlook(outlook) { ... }
```

---

## 8. 이메일 템플릿 (`email_ai_issue.html`)

```
Subject: 🤖 AI 위클리 — 2026.05.26 ~ 2026.06.01

┌────────────────────────────────┐
│  🤖 AI Issue Weekly            │
│  2026.05.26 ~ 2026.06.01       │
└────────────────────────────────┘

[섹션 1] 이번 주 TOP 3 이슈 (카드 3개)
         제목 / 카테고리 / 중요도 / 2줄 요약

[섹션 2] 이번 주 이슈 목록 (4~10위 심플 리스트)

[섹션 3] 💡 이번 주 AI 팁 (1개 하이라이트)

[섹션 4] 📈 AI 주요 종목 주간 등락 (심플 테이블)

[섹션 5] 🔮 차주 전망 (3줄 요약)

[푸터] 전체 보고서 보기 → 링크 | 구독취소
```

---

## 9. `.gitignore` 추가

```gitignore
# AI Issue — 날짜별 발행 파일 (force-add로 관리)
publish/ai-issue/20??-??-??.html
publish/ai-issue/20??-??-??.json
```

---

## 10. 구현 단계 (Phase)

| Phase | 작업 | 산출물 | 예상 |
|-------|------|--------|------|
| **1** | RSS 소스 정의 | `config/ai_issue_sources.py` | 1h |
| **2** | 수집 모듈 | `core/ai_issue/collector.py` | 2h |
| **3** | 프롬프트 + 분석 모듈 | `config/ai_issue_prompts.py`, `analyzer.py` | 3h |
| **4** | 보고서 생성 + 템플릿 | `report.py`, `ai_issue_report.md` | 1h |
| **5** | HTML 빌드 + 퍼블리시 | `build_ai_issue_site.py`, `publish/ai-issue/` | 3h |
| **6** | app.html 탭·사이드바·JS | `app.html` 통합 | 2h |
| **7** | 이메일 템플릿·발송 | `email_ai_issue.html`, `send_ai_issue_email.py` | 1h |
| **8** | 워크플로우 | `ai_issue.yml` | 1h |
| **9** | 테스트·수동 실행 | 첫 발행 검증 | 1h |
| **전체** | | | **약 15h** |

---

## 11. 기존 코드 재사용 계획

| 기존 모듈 | 재사용 방식 |
|-----------|-------------|
| `core/shared/mailer.py` | 이메일 발송 그대로 |
| `core/shared/telegram.py` | Telegram 발송 그대로 |
| `core/news/collector.py` | RSS 수집 로직 참고 |
| `scripts/build_site.py` | HTML 빌드 패턴 동일 |
| `themes/*.py` | 동일 테마 시스템 |
| `config/theme_config.py` | `SECTION_THEMES["ai-issue"]` 추가 |
| `publish/app.html` | 탭·렌더 함수·lazy-load 패턴 재사용 |
| `yfinance` (stock 모듈) | AI 종목 주가 데이터 (E섹션) |
| `reports/news_*.json` | AI 키워드 필터 재활용 (수집 보완) |

---

*v2 — 2026-05-27: 소스 목록 확정, 발행 일정 확정(일요일 07:00), 파일 식별자 날짜형 확정, 탭 통합 확정, 실용팁/투자동향/논문Pick 섹션 추가*
