# AI Issue Report — 구현 계획 및 완료 보고서

> **최종 수정일**: 2026-05-29 (v4 완료 최종 업데이트)  
> **목적**: 주간 AI 동향 전문 분석 서비스 (`ai-issue`) 최종 아키텍처 및 구현 스펙 문서화  
> **기조**: 기존 news/stock 패턴 최대 재사용, 무결한 자동화 및 다채널 연동 완료

---

## 1. 개요

| 항목 | 내용 |
|------|------|
| 발행 주기 | **주 1회** — 일요일 KST 07:00 실행, **월요일 08:00 이전 완료** |
| 분석 범위 | 직전 월~일(7일)간 AI 관련 이슈 |
| 파일 식별자 | **`YYYY-MM-DD` (해당 주 일요일 날짜)** — 예: `2026-06-01` |
| 사이트 통합 | **app.html 탭 통합** (뉴스클리핑 \| AI이슈 \| 주식시황) |
| 출력 | 웹사이트(HTML) + 이메일 + Telegram + Markdown 보고서 + Notion DB |

---

## 2. 콘텐츠 구조 (확정 및 구현 완료)

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

| 섹션 | 포함 이유 | 구현 완료 상세 |
|------|-----------|-------------|
| A. TOP 10 | 핵심 가치, 빠른 파악 | 1차 키워드 필터링 및 2차 LLM 선별 파이프라인 탑재 |
| B. 심층 분석 | 차별화 포인트, 전문성 | TOP 3 개별 심층 가이드 자동 생성 |
| C. 기업 동향 | 독자 관심도 최상위 | 주요 빅테크 및 국내 동향 분리 요약 |
| D. 실용 팁 | 즉시 활용 가능 → 구독 유지율↑ | 프롬프트 팁 및 신기능 가이드 생성 |
| E. 투자 동향 | 주식 모듈과 시너지, 경제 독자층 확보 | `yfinance` 주간 등락 자동 연동 및 예외 처리 완비 |
| F. 논문 Pick | 기술 독자층 확보, 신뢰도↑ | cs.AI 키워드 가중치 기반 Top 30 후보 필터링 후 3편 선별 |
| G. 카테고리 분포 | 한눈에 이번 주 색깔 파악 | 7대 카테고리 자동 통계 및 분배 시각화 |
| H. 차주 전망 | 연속성·재방문 동기 | 🔮 차주 주요 모니터링 포인트 도출 |

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

### 3-1. AI 기업 공식 블로그 (검증 완료된 16개 RSS 소스 유지)

* OpenAI Blog: `https://openai.com/news/rss`
* Anthropic News: `https://www.anthropic.com/news/rss`
* Google DeepMind: `https://deepmind.google/blog/rss/`
* Google AI Blog: `https://blog.google/technology/ai/rss`
* Meta AI Blog: `https://ai.meta.com/blog/rss/`
* Microsoft AI: `https://blogs.microsoft.com/ai/feed/`
* Hugging Face Blog: `https://huggingface.co/blog/feed.xml`

### 3-2. AI 전문 미디어

* **The Decoder**: `https://the-decoder.com/feed/`
* **AI News**: `https://www.artificialintelligence-news.com/feed/`
* VentureBeat AI: `https://venturebeat.com/ai/feed/`
* TechCrunch AI: `https://techcrunch.com/category/artificial-intelligence/feed/`
* Wired AI: `https://www.wired.com/feed/tag/ai/latest/rss`

### 3-3. 연구·논문 (arXiv 수집 전략)

* **arXiv cs.AI**: `http://arxiv.org/rss/cs.AI`
* **arXiv cs.LG**: `http://arxiv.org/rss/cs.LG`
* **HF Daily Papers**: `https://huggingface.co/papers/rss`

### 3-4. 국내 AI 미디어

* **AI타임스**: `https://www.aitimes.com/rss/allArticle.xml`

---

## 4. 폴더 구조 (신규 추가 경로)

기존 `core/news/`, `core/stock/` 과 동일한 계층 구조를 `core/ai_issue/` 에 적용.  
`core/shared/` (mailer, telegram, notion, db) 는 그대로 재사용.

```
dailynews/
│
├── core/
│   ├── news/          ← 기존
│   ├── stock/         ← 기존
│   └── ai_issue/      ← 신규 (domain 로직)
│       ├── __init__.py
│       ├── collector.py    ← AI 소스 수집 + cs.AI 후보군 및 yfinance 주가 수집
│       ├── analyzer.py     ← LLM 연쇄 종합 분석 (Strategy 패턴)
│       └── report.py       ← Jinja2 마크다운 및 구조화 JSON 저장
│
├── core/shared/       ← 기존 연동 모듈 확장
│   ├── mailer.py      ← 이메일 발송
│   ├── telegram.py    ← Telegram 발송 (주간 AI이슈 알림 함수 추가 완료)
│   ├── notion.py      ← Notion 동기화 (상세 본문 자동 적재를 위한 Markdown Parser 탑재 완료)
│   └── db.py
│
├── config/
│   ├── ai_issue_prompts.py   ← 신규: LLM 분석 전용 다단계 고밀도 프롬프트
│   └── ai_issue_sources.py   ← 신규: 검증 완료된 16개 RSS 소스
│
├── scripts/
│   ├── run_ai_issue.py          ← 신규: 주간 실행 진입점
│   ├── validate_ai_issue_sources.py  ← 신규: RSS 연결성 및 SSL 예외 처리 검증 스크립트
│   ├── build_ai_issue_site.py   ← 신규: 주간 AI이슈 독립 페이지 빌드
│   ├── send_ai_issue_email.py   ← 신규: 80KB 이하 모바일 클리핑 방지 이메일 발송기
│   ├── send_ai_issue_telegram.py← 신규: 텔레그램 카드뉴스식 요약 알림 전송기
│   └── sync_notion.py           ← 기존: --type ai-issue 유형 연동 완료
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
│       ├── index.html            ← git 추적 (최신 이슈 자동 포워딩)
│       ├── archive.html          ← git 추적 (주간 아카이브 목록)
│       ├── ai-issue-data.json    ← git 추적 (app.html 탭 시드 데이터)
│       ├── 2026-06-01.html       ← gitignore + Actions force-add
│       └── 2026-06-01.json       ← gitignore + Actions force-add
│
└── .github/workflows/
    └── ai_issue.yml              ← 신규: 주간 워크플로우 (KST 타임존 동기화 완료)
```

---

## 5. JSON 파일 구조

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

---

## 6. Notion 데이터베이스 연동 및 완성 스키마

**Notion DB 연동이 성공적으로 활성화되었습니다.** 기존 TBD 설정을 완전히 제거하고 구현에 맞추어 완비되었습니다. 
Notion 페이지 속성(Properties) 영역 동적 매핑 뿐만 아니라, **페이지 내부 본문(Page Body)에 마크다운 분석 세부 내역이 단락별 블록(`heading_2`, `heading_3`, `bulleted_list_item`, `paragraph`)으로 완벽히 변환되어 적재**됩니다.

### 6-1. 환경변수 추가 필요

```
NOTION_DATABASE_ID_AI_ISSUE   ← 신규 생성한 Notion DB 고유 ID값 (GitHub Secrets에 등록)
```

> [!IMPORTANT]
> **API 연결 필수**  
> 노션 데이터베이스 생성 후, Notion 통합 연동(Connection)을 반드시 해당 DB 페이지에 **[초대/연결]** 해주셔야 API가 정상 접근할 수 있습니다.

### 6-2. Notion DB 권장 스키마 구조

| 컬럼명 | 노션 타입 | 입력 값 형태 / 예시 |
|--------|------|------|
| **제목** (기본컬럼) | `title` | `[순위] 이슈 제목` (예: `[1] GPT-5 출시 예고 및 기술적 영향`) |
| **날짜** | `date` | 발행 기준 일요일 날짜 (예: `2026-06-01`) |
| **기간** | `rich_text` | 주간 수집 범위 (예: `2026-05-26 ~ 2026-06-01`) |
| **카테고리** | `select` | `model`, `service`, `research`, `policy`, `industry`, `infra`, `investment`, `etc` |
| **순위** | `number` | `1` ~ `10` |
| **요약** | `rich_text` | 이슈 핵심 2~3줄 요약 문장 |
| **차주전망** | `rich_text` | 🔮 차주 모니터링 포인트 (1순위 이슈 행에만 첨부) |

---

## 7. 워크플로우 (`ai_issue.yml`)

KST 기준 일요일 오전 7시에 정상 수집 및 배포가 개시되도록 설정되었습니다. 글로벌 가상머신 내 `TZ: Asia/Seoul` 글로벌 주입을 통해 날짜 밀림 에러가 완전히 방지되었습니다.

```yaml
name: AI Issue Weekly Report

on:
  schedule:
    # UTC 토요일 22:00 = KST 일요일 07:00 실행 (월요일 오전 발행 완료 대비)
    - cron: '0 22 * * 6'
  workflow_dispatch:
    inputs:
      target_date:
        description: '발행 기준 일요일 날짜 (예: 2026-06-01). 미입력 시 KST 당일 자동 연산'
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
    
    env:
      TZ: Asia/Seoul

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
        run: |
          if [ -n "${{ github.event.inputs.target_date }}" ]; then
            python scripts/run_ai_issue.py --date ${{ github.event.inputs.target_date }}
          else
            python scripts/run_ai_issue.py
          fi
        env:
          LLM_PROVIDER:        ${{ secrets.LLM_PROVIDER }}
          GEMINI_API_KEY:      ${{ secrets.GEMINI_API_KEY }}
          ANTHROPIC_API_KEY:   ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY:      ${{ secrets.OPENAI_API_KEY }}

      - name: Notion AI이슈 동기화
        run: |
          TARGET_DATE=$(date +'%Y-%m-%d')
          if [ -n "${{ github.event.inputs.target_date }}" ]; then
            TARGET_DATE="${{ github.event.inputs.target_date }}"
          fi
          python scripts/sync_notion.py --type ai-issue --date ${TARGET_DATE}
        env:
          NOTION_API_KEY:                ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID_AI_ISSUE:   ${{ secrets.NOTION_DATABASE_ID_AI_ISSUE }}

      - name: HTML 빌드 (ai-issue 전용)
        run: python scripts/build_ai_issue_site.py
        env:
          SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}

      - name: 통합 사이트 빌드 (app.html AI이슈 탭 반영 컴파일)
        run: python scripts/build_site.py --from $(date +'%Y-%m-%d')
        env:
          SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}

      - name: 이메일 발송
        run: |
          TARGET_DATE=$(date +'%Y-%m-%d')
          if [ -n "${{ github.event.inputs.target_date }}" ]; then
            TARGET_DATE="${{ github.event.inputs.target_date }}"
          fi
          python scripts/send_ai_issue_email.py --date ${TARGET_DATE}
        env:
          GMAIL_USER:         ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAILS:   ${{ secrets.RECIPIENT_EMAILS }}
          SITE_BASE_URL:      ${{ secrets.SITE_BASE_URL }}

      - name: Telegram 발송
        run: |
          TARGET_DATE=$(date +'%Y-%m-%d')
          if [ -n "${{ github.event.inputs.target_date }}" ]; then
            TARGET_DATE="${{ github.event.inputs.target_date }}"
          fi
          python scripts/send_ai_issue_telegram.py --date ${TARGET_DATE}
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID:   ${{ secrets.TELEGRAM_CHAT_ID }}
          SITE_BASE_URL:      ${{ secrets.SITE_BASE_URL }}
        continue-on-error: true # 텔레그램 미등록 시 전체 프로세스 성공 보장용

      - name: 커밋 + 푸시
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "actions@github.com"
          git add reports/ai-issue/
          git add -f publish/ai-issue/20??-??-??.html \
                     publish/ai-issue/20??-??-??.json 2>/dev/null || true
          git add -f publish/ai-issue/index.html \
                     publish/ai-issue/archive.html \
                     publish/ai-issue/ai-issue-data.json 2>/dev/null || true
          git add -f publish/app.html publish/index.html 2>/dev/null || true
          git diff --staged --quiet || \
            git commit -m "🤖 AI Issue Weekly $(date +'%Y-%m-%d')"
          git pull --rebase --autostash origin main
          git push

      - name: GitHub Pages 배포 아티팩트 업로드
        uses: actions/upload-pages-artifact@v3
        with:
          path: publish/

      - name: Deploy to GitHub Pages
        id: deploy
        uses: actions/deploy-pages@v4
```

---

## 8. 기존 코드 재사용 및 안정성 성과

1. **mailer 연계**: 이메일 템플릿 크기를 **80KB 미만**으로 하드 캡 제한하여, 메일 본문이 잘리거나 숨겨지는 Gmail 클리핑 이슈를 철저하게 방지하였습니다.
2. **사이드 탭 레이아웃**: `app.html` 웹사이트 왼편에 `🤖 AI이슈` 탭을 배치하여 주간 요약 아카이브가 부드럽게 네비게이션되도록 lazy-load 프론트엔드 연동을 마쳤습니다.
3. **yfinance 등락 예외 보완**: 휴장일이 겹치는 주말에도 yfinance 조회 시 에러가 터지지 않고 직전 종가 데이터를 백업으로 참조하도록 예외 안전 장치를 삽입했습니다.
4. **Notion 마크다운 완벽 동기화**: `Heading 2`, `Heading 3`, `Bulleted List`, `Paragraph`를 지원하는 전용 파서를 탑재하여 노션 웹페이지에서도 미려한 양식의 콘텐츠 분석 결과를 손쉽게 조회할 수 있게 되었습니다.

---
*v4 — 2026-05-29: 노션 상세 본문 블록 파서 파이프라인 설명 및 최종 테이블 스펙 확정, 텔레그램 발송 모듈 스크립트화 반영 완료*
