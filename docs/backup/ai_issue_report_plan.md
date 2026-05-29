# AI Issue Report — 구현 계획

> **작성일**: 2026-05-27 (v3 업데이트)  
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
│         (수집 ~30개 후보 → AI가 최종 10개 선별)
│
├── [B] 🔍 주요 이슈 심층 분석 (TOP 3)
│         각 이슈: 배경 / 핵심 내용 / 산업적 의미 / 파급효과 / 출처
│
├── [C] 🏢 AI 기업·서비스 동향
│         OpenAI / Anthropic / Google / Meta / MS / 국내 기업
│
├── [D] 💡 AI 실용 팁 (Weekly Tip)
│         독자가 당장 활용 가능한 AI 도구/기능/프롬프트 2~3개
│         예: "Claude에서 이렇게 쓰면 더 좋아진다", "Gemini 새 기능 활용법"
│
├── [E] 📈 AI 투자·펀딩 동향
│         주간 AI 기업 VC 펀딩·M&A 소식 (RSS 수집)
│         AI 관련 주요 종목 주간 등락 (NVDA, MSFT, GOOGL, META 등)
│         기존 yfinance 모듈 연계
│
├── [F] 🔬 주목 논문 Pick (Research Radar)
│         arXiv/HF Papers에서 ~30개 후보 수집 → AI가 2~3편 최종 선별
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

### Phase 0 — RSS URL 유효성 검증 (구현 전 필수)

모든 RSS URL은 구현 시작 전 feedparser로 실 접속 확인.  
응답 없거나 항목 수 0인 소스는 대체 소스로 교체 후 `ai_issue_sources.py`에 반영.

```python
# scripts/validate_ai_issue_sources.py (Phase 0 일회성 스크립트)
import feedparser
for name, url in SOURCES.items():
    feed = feedparser.parse(url)
    print(f"{name}: {len(feed.entries)} entries — {url}")
```

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
| VentureBeat AI | `https://venturebeat.com/ai/feed/` | service/industry |
| TechCrunch AI | `https://techcrunch.com/category/artificial-intelligence/feed/` | 펀딩·스타트업 |
| The Verge AI | `https://www.theverge.com/ai-artificial-intelligence/rss/index.xml` | 제품·소비자 |
| Wired AI | `https://www.wired.com/feed/tag/ai/latest/rss` | 사회·윤리 |
| MIT Tech Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed` | 연구·정책 |

### 3-3. 연구·논문 (arXiv 수집 전략)

주간 arXiv cs.AI 피드는 300~500편 수준이므로 **전체 처리 금지**.  
수집 → 1차 필터(제목+초록 키워드) → **~30개 후보** → AI 최종 선별(2~3편).

| 소스 | URL | 특징 |
|------|-----|------|
| **arXiv cs.AI** | `http://arxiv.org/rss/cs.AI` | AI 전반 |
| **arXiv cs.LG** | `http://arxiv.org/rss/cs.LG` | 머신러닝 |
| arXiv cs.CL | `http://arxiv.org/rss/cs.CL` | NLP/LLM |
| arXiv cs.CV | `http://arxiv.org/rss/cs.CV` | 컴퓨터 비전 |
| **HF Daily Papers** | `https://huggingface.co/papers/rss` | 커뮤니티 선별 주목 논문 |
| Papers With Code | `https://paperswithcode.com/latest/rss` | 코드 공개 논문 |

```python
# collector.py 논문 수집 흐름
raw_papers = fetch_rss(ARXIV_SOURCES, days=7)     # 전체 수집
candidates = keyword_filter(raw_papers, top_n=30) # 1차 필터
final_picks = llm_select_papers(candidates, n=3)  # AI 최종 선별
```

### 3-4. 국내 AI 미디어

| 소스 | RSS URL | 특징 |
|------|---------|------|
| **AI타임스** | `https://www.aitimes.com/rss/allArticle.xml` | AI 전문 국내 매체 |
| **전자신문** | `https://rss.etnews.com/Section901.xml` | IT/AI 산업 |
| ZDNet Korea | `https://zdnet.co.kr/rss/news.xml` | 기술 전반 |
| Bloter | `https://www.bloter.net/feed` | 스타트업·서비스 |

### 3-5. 투자·펀딩 (E섹션 전용)

> **Crunchbase 제외**: 스크래핑 금지 정책 + API 유료화. 아래 RSS 대안으로 대체.

| 소스 | RSS URL | 데이터 |
|------|---------|--------|
| TechCrunch Fundings | `https://techcrunch.com/tag/funding/feed/` | AI 투자 소식 |
| VentureBeat Funding | `https://venturebeat.com/category/deals/feed/` | VC 딜 정보 |
| The Information AI | *(유료, 향후 검토)* | 심층 펀딩 분석 |
| 기존 `yfinance` 모듈 | 코드 재사용 | NVDA/MSFT/GOOGL/META/AMD 주가 |

> **수집 전략**: AI 전용 RSS + 기존 일일 뉴스에서 AI 키워드 필터링 병행  
> **우선순위**: bold 표시 소스 우선 구현, 나머지 점진적 추가

---

## 4. 폴더 구조 (신규 추가 경로)

기존 `core/news/`, `core/stock/` 과 동일한 계층 구조를 `core/ai_issue/` 에 적용.  
`core/shared/` (mailer, telegram, notion, db) 는 그대로 재사용.

```
dailynews/
│
├── core/
│   ├── news/          ← 기존 (참고 패턴)
│   ├── stock/         ← 기존 (참고 패턴)
│   └── ai_issue/      ← 신규 (domain 로직만)
│       ├── __init__.py
│       ├── collector.py    ← AI 소스 수집 + 기존 뉴스 AI 필터
│       ├── analyzer.py     ← 주간 분석, TOP 10 선별, 섹션별 생성
│       └── report.py       ← MD + JSON 보고서 저장
│
├── core/shared/       ← 기존 그대로 (cross-cutting)
│   ├── mailer.py      ← 이메일 발송
│   ├── telegram.py    ← Telegram 발송
│   ├── notion.py      ← Notion 동기화 (sync_ai_issue_to_notion 추가)
│   └── db.py
│
├── config/
│   ├── ai_issue_prompts.py   ← 신규: 섹션별 프롬프트
│   └── ai_issue_sources.py   ← 신규: AI 전문 RSS 소스 목록
│
├── scripts/
│   ├── run_ai_issue.py          ← 신규: 주간 실행 진입점
│   ├── validate_ai_issue_sources.py  ← 신규: Phase 0 RSS 검증 (일회성)
│   ├── build_ai_issue_site.py   ← 신규: HTML 빌드
│   ├── send_ai_issue_email.py   ← 신규: 이메일 발송
│   └── sync_notion.py           ← 기존: --type ai-issue 추가됨
│   # Telegram 발송: 별도 스크립트 없음 — core/shared/telegram.send_ai_issue_telegram() 직접 호출
│
├── templates/
│   ├── ai_issue_report.md       ← 신규: 보고서 MD 템플릿
│   └── email_ai_issue.html      ← 신규: 이메일 템플릿 (모바일 반응형 포함)
│
├── reports/
│   └── ai-issue/                ← 신규 (git 추적)
│       ├── ai_issue_2026-06-01.md
│       └── ai_issue_2026-06-01.json
│
├── publish/
│   └── ai-issue/                ← 신규
│       ├── index.html            ← git 추적 (최신 이슈 + 목록)
│       ├── archive.html          ← git track
│       ├── ai-issue-data.json    ← git 추적 (인덱스·요약 메타, app.html 시드)
│       ├── 2026-06-01.html       ← gitignore + Actions force-add
│       └── 2026-06-01.json       ← gitignore + Actions force-add
│
└── .github/workflows/
    └── ai_issue.yml              ← 신규: 주간 워크플로우
```

---

## 5. JSON 파일 구조 (news/stock 패턴 동일 적용)

### 5-1. `publish/ai-issue/ai-issue-data.json` — 요약 인덱스 (git 추적)

app.html 초기 로딩 시드. 날짜 목록 + 각 주의 메타 요약만 포함.

```json
{
  "updated": "2026-06-01",
  "issues": [
    {
      "date": "2026-06-01",
      "period": "2026-05-26 ~ 2026-06-01",
      "top3": ["GPT-5 출시", "EU AI Act 시행", "Apple AI 통합"],
      "category_counts": {"model": 3, "service": 2, "policy": 2, "research": 2, "investment": 1}
    }
  ]
}
```

### 5-2. `publish/ai-issue/YYYY-MM-DD.json` — 날짜별 본문 (gitignore)

사용자가 날짜 클릭 시 lazy-load. 전체 섹션 데이터 포함.

```json
{
  "date": "2026-06-01",
  "period": "2026-05-26 ~ 2026-06-01",
  "top10": [
    {
      "rank": 1,
      "title": "GPT-5 출시 및 주요 기능 분석",
      "category": "model",
      "importance": 5,
      "summary": "...",
      "detail": "..."
    }
  ],
  "company_trends": "...",
  "weekly_tip": "...",
  "investment_summary": "...",
  "stock_snapshots": [{"ticker": "NVDA", "weekly_change_pct": 3.2, "note": "..."}],
  "paper_picks": [{"title": "...", "one_liner": "...", "practical_note": "...", "url": "..."}],
  "category_stats": {"model": 3, "service": 2},
  "next_week_outlook": "..."
}
```

> **gitignore 정책**: 날짜별 파일(`20??-??-??.html`, `20??-??-??.json`)은 로컬 실행 시 잘못된 publish 방지를 위해 gitignore 처리. GitHub Actions만 force-add로 관리. `ai-issue-data.json`, `index.html`, `archive.html`은 git 추적 대상.

---

## 6. 핵심 모듈 설계

### 6-1. `core/ai_issue/collector.py`

```python
# 역할: AI 전문 RSS 수집 + 기존 뉴스에서 AI 기사 필터링
# 수집 범위: 해당 주 월~일 (7일)
# 출력: List[dict] — title, url, source, date, category_hint, content_raw

AI_KEYWORDS = ["AI", "LLM", "GPT", "Claude", "Gemini", "인공지능", "머신러닝", ...]

def collect_weekly(start_date, end_date) -> List[dict]:
    articles = []
    # 1. AI 전문 RSS 피드 직접 수집 (ai_issue_sources.py 소스 목록)
    # 2. reports/news_YYYY-MM-DD.json에서 AI 키워드 필터링 (일일 뉴스 재활용)
    # 3. arXiv/HF Papers → 키워드 필터 후 ~30개 후보 추출 (F섹션)
    # 4. yfinance → AI 관련 종목 주가 (E섹션)
    # 5. 중복 제거 (URL 해시 기준), 날짜 필터링
    return deduplicate(articles)

def collect_paper_candidates(start_date, end_date, top_n=30) -> List[dict]:
    """arXiv/HF 전체 수집 → 키워드 1차 필터 → 상위 N개 반환"""
    raw = fetch_rss(ARXIV_SOURCES, days=7)
    return keyword_filter(raw, top_n=top_n)
```

### 6-2. `core/ai_issue/analyzer.py`

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
    one_liner: str
    practical_note: str
    url: str

@dataclass
class StockSnapshot:
    ticker: str
    name: str
    weekly_change_pct: float
    note: str

@dataclass
class IssueReport:
    issue_date: str        # "2026-06-01" (일요일)
    period: str            # "2026-05-26 ~ 2026-06-01"
    top10: List[IssueItem]
    company_trends: str
    weekly_tip: str
    investment_summary: str
    stock_snapshots: List[StockSnapshot]
    paper_picks: List[PaperItem]
    category_stats: dict
    next_week_outlook: str
    generated_at: str

def analyze(articles, paper_candidates) -> IssueReport:
    # 1. 기사 ~30개 후보 → LLM TOP 10 선별 + 심층 분석
    # 2. 논문 후보 ~30개 → LLM 최종 2~3편 선별
    # 3. 각 섹션별 프롬프트 호출 (config/ai_issue_prompts.py)
    ...
```

### 6-3. `config/ai_issue_prompts.py` (섹션별 분리)

```python
# A+B: TOP 10 + 심층 분석
# 입력: 수집 기사 요약 목록 (최대 30개), 분석 기간
MAIN_ANALYSIS_PROMPT = """..."""

# C: 기업 동향
COMPANY_TRENDS_PROMPT = """..."""

# D: 실용 팁
WEEKLY_TIP_PROMPT = """
이번 주 AI 뉴스를 바탕으로 독자가 당장 활용할 수 있는 실용 AI 팁 2~3개를 작성하세요.
각 팁: 제목 | 도구명 | 활용법 (3줄) | 난이도(초급/중급/고급)
..."""

# F: 논문 Pick — 후보 30개 → 최종 2~3편 선별
PAPER_PICK_PROMPT = """
아래 논문 후보 목록에서 이번 주 가장 주목할 논문 2~3편을 선정하세요.
선정 기준: 실무 임팩트 + 커뮤니티 관심도 + 기술 참신성
각 논문: 제목 | 한줄 요약 | 실무 적용 가능성 (있음/제한적/없음) | 이유
..."""

# H: 차주 전망
OUTLOOK_PROMPT = """..."""
```

---

## 7. 워크플로우 (`ai_issue.yml`)

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

      - name: Notion AI이슈 동기화
        run: python scripts/sync_notion.py --type ai-issue --date $(TZ=Asia/Seoul date +'%Y-%m-%d')
        env:
          NOTION_API_KEY:                ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID_AI_ISSUE:   ${{ secrets.NOTION_DATABASE_ID_AI_ISSUE }}

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
        run: |
          python -c "
import json, sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, '.')
from core.shared.telegram import send_ai_issue_telegram
date_str = datetime.now().strftime('%Y-%m-%d')
data = json.loads((Path('reports/ai-issue') / f'ai_issue_{date_str}.json').read_text(encoding='utf-8'))
send_ai_issue_telegram(data, date_str)
"
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID:   ${{ secrets.TELEGRAM_CHAT_ID }}

      - name: 커밋 + 푸시
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "actions@github.com"
          git add reports/ai-issue/
          # 날짜별 파일 — 와일드카드로 타임존 롤오버 버그 방지
          git add -f publish/ai-issue/20??-??-??.html \
                     publish/ai-issue/20??-??-??.json 2>/dev/null || true
          # 인덱스·요약 파일 (항상 최신 상태)
          git add -f publish/ai-issue/index.html \
                     publish/ai-issue/archive.html \
                     publish/ai-issue/ai-issue-data.json 2>/dev/null || true
          git add -f publish/app.html publish/index.html 2>/dev/null || true
          git diff --staged --quiet || \
            git commit -m "🤖 AI Issue Weekly $(TZ=Asia/Seoul date +'%Y-%m-%d')"
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

## 8. 사이트 통합 (`app.html` 탭 통합)

### 9-1. 네비게이션 탭

```
[ 뉴스클리핑 ]  [ 🤖 AI이슈 ]  [ 주식시황 ]
```

- `config/theme_config.py` NAV_ITEMS에 `ai-issue` 추가
- 섹션 테마: `SECTION_THEMES["ai-issue"] = "editorial"` (기본값)
- localStorage: `theme-ai-issue`

### 9-2. AI이슈 섹션 사이드바

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

### 9-3. 메인 렌더링 컴포넌트 (JS)

```javascript
// 뉴스 날짜 클릭 → lazy-load (기존 패턴 동일)
async function selectAIIssueDate(dateStr) {
  if (!state.aiIssueCache[dateStr]) {
    const data = await fetch(`/ai-issue/${dateStr}.json`).then(r => r.json());
    state.aiIssueCache[dateStr] = data;
  }
  renderAIIssueReport(state.aiIssueCache[dateStr]);
}
```

### 9-4. Vercel 라우팅 (`vercel.json`)

stock 변경 구조를 참고하여 `/ai-issue/` URL 라우팅 추가.

```json
{
  "rewrites": [
    { "source": "/ai-issue/:date.html", "destination": "/ai-issue/:date.html" },
    { "source": "/ai-issue/:date.json", "destination": "/ai-issue/:date.json" },
    { "source": "/ai-issue",            "destination": "/ai-issue/index.html" },
    { "source": "/ai-issue/archive",    "destination": "/ai-issue/archive.html" }
  ]
}
```

---

## 9. 이메일 템플릿 (`email_ai_issue.html`)

**모바일 반응형 필수** — `email_news.html` 동일 방식 적용 (`@media` + `display:block`).

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

## 10. `.gitignore` 추가

```gitignore
# AI Issue — 날짜별 발행 파일 (Actions force-add로 관리)
publish/ai-issue/20??-??-??.html
publish/ai-issue/20??-??-??.json
```

> `ai-issue-data.json`, `index.html`, `archive.html`은 gitignore 제외 (git 추적).

---

## 11. Notion 데이터베이스 연동

> **현황**: 뉴스 DB와 주식 DB는 각각 다른 등록 방식으로 운영 중. AI Issue DB는 **미생성 (TBD)**.  
> `sync_notion.py --type ai-issue` 호출부와 `core/shared/notion.py` 함수는 미리 구현.  
> Notion DB 생성 후 `NOTION_DATABASE_ID_AI_ISSUE` 시크릿 등록으로 활성화.

### 12-1. 환경변수 추가 필요 (DB 생성 후)

```
NOTION_DATABASE_ID_AI_ISSUE   ← 신규 시크릿 (GitHub Actions Secrets에 추가)
```

### 12-2. Notion DB 권장 스키마

| 컬럼명 | 타입 | 내용 |
|--------|------|------|
| 제목 | title | `[순위] 이슈 제목` |
| 날짜 | date | 해당 주 일요일 날짜 |
| 기간 | rich_text | `2026-05-26 ~ 2026-06-01` |
| 카테고리 | select | model/service/research/policy/industry/infra/investment |
| 순위 | number | 1~10 |
| 요약 | rich_text | 이슈 2~3줄 요약 |
| 차주전망 | rich_text | 1순위 이슈에 차주 전망 첨부 |

---

## 12. 기존 코드 재사용 계획

| 기존 모듈 | 재사용 방식 |
|-----------|-------------|
| `core/shared/mailer.py` | 이메일 발송 그대로 |
| `core/shared/telegram.py` | `send_ai_issue_telegram()` 함수 추가 (기존 `send_telegram_cardnews`와 동일 파일) |
| `core/shared/notion.py` | `sync_ai_issue_to_notion()` 추가 |
| `core/news/collector.py` | RSS 수집 로직 참고 |
| `scripts/sync_notion.py` | `--type ai-issue` 케이스 추가 |
| `scripts/build_site.py` | HTML 빌드 패턴 동일 |
| `templates/email_news.html` | 반응형 구조 참고 |
| `config/theme_config.py` | `SECTION_THEMES["ai-issue"]` 추가 |
| `publish/app.html` | 탭·렌더 함수·lazy-load 패턴 재사용 |
| `yfinance` (stock 모듈) | AI 종목 주가 데이터 (E섹션) |
| `reports/news_*.json` | AI 키워드 필터 재활용 (수집 보완) |

---

## 13. 구현 단계 (Phase)

| Phase | 작업 | 산출물 | 예상 |
|-------|------|--------|------|
| **0** | RSS URL 유효성 검증 | `scripts/validate_ai_issue_sources.py` | 0.5h |
| **1** | RSS 소스 정의 | `config/ai_issue_sources.py` | 0.5h |
| **2** | 수집 모듈 | `core/ai_issue/collector.py` | 2h |
| **3** | 프롬프트 + 분석 모듈 | `config/ai_issue_prompts.py`, `analyzer.py` | 3h |
| **4** | 보고서 생성 + 템플릿 | `report.py`, `ai_issue_report.md` | 1h |
| **5** | HTML 빌드 + 퍼블리시 | `build_ai_issue_site.py`, `publish/ai-issue/` | 3h |
| **6** | app.html 탭·사이드바·JS + vercel.json | `app.html` 통합 | 2h |
| **7** | 이메일·Telegram 템플릿·발송 | `email_ai_issue.html`, `send_*.py` | 1.5h |
| **8** | Notion 연동 | `core/shared/notion.py`, `sync_notion.py` | 1h |
| **9** | 워크플로우 | `ai_issue.yml` | 0.5h |
| **10** | 테스트·수동 실행 | 첫 발행 검증 | 1h |
| **전체** | | | **약 16h** |

---

*v3 — 2026-05-28: 아키텍처 명확화(core/ai_issue + core/shared 분리), arXiv 수집 전략(30개 후보→AI선별), Crunchbase 제거·RSS 대안, JSON 파일 성격 명확화(요약 json 추적/날짜 json gitignore), Telegram 실 스크립트, wildcard commit, Phase 0 RSS 검증, vercel.json 라우팅, 이메일 반응형 명시, Notion TBD 표기*
