# AI News Brief — 시스템 아키텍처

> README의 L1·L2 다이어그램에서 이어지는 심화 문서입니다.

---

## 1. 핵심 설계 원칙

```
구조(Structure)   templates/*.html    HTML 골격, 레이아웃
테마(Theme)       themes/{name}.py    색상, 폰트 CSS 토큰
콘텐츠(Content)   reports/*.md        수집 데이터 + AI 분석 텍스트

→ 세 요소 완전 분리: 테마만 바꿔도 전체 디자인 변경
→ config/ 에서 중앙 제어 (하드코딩 금지)
```

---

## 2. 테마 시스템

### 2-1. 테마 종류

```mermaid
graph LR
    subgraph LAYOUTS["themes/layouts/ — 독립 HTML 생성"]
        ED["editorial.py\n신문 마스트헤드\nNoto Serif KR · 현재 기본"]
        TM["terminal.py\nBloomberg 다크\nJetBrains Mono"]
        MI["minimal.py\n넓은 여백\n오렌지 accent"]
    end

    subgraph SKINS["themes/skins/ — TOKENS 색상·폰트만 제공"]
        CL["classic.py\n남색 카드"]
        IN["ink.py\n붉은 accent"]
        FO["forest.py\n에메랄드"]
    end

    BASE["themes/base.py\nJinja2 렌더링 엔진\nweb_*.html 템플릿 사용"]

    SKINS --> BASE
    LAYOUTS -.->|render_*() 직접 생성| HTML["최종 HTML"]
    BASE --> HTML
```

### 2-2. 테마 로드 순서

```python
# themes/__init__.py::load_theme()
# 탐색 순서: layouts.{name} → skins.{name} → skins.classic(폴백)
theme = load_theme("editorial")   # layouts/editorial.py
theme = load_theme("classic")     # skins/classic.py
theme = load_theme("unknown")     # → skins/classic 폴백
```

### 2-3. 섹션별 테마 독립 설정

```python
# config/theme_config.py
SITE_THEME = "editorial"   # 전체 기본

SECTION_THEMES = {
    "news":     os.getenv("THEME_NEWS",     SITE_THEME),
    "stock":    os.getenv("THEME_STOCK",    SITE_THEME),
    "ai-issue": os.getenv("THEME_AI_ISSUE", SITE_THEME),
    "email":    os.getenv("THEME_EMAIL",    "classic"),  # 이메일은 classic 고정
}
```

---

## 3. 렌더링 경로

### 3-1. 웹 HTML 생성

```mermaid
flowchart TD
    MD["reports/*.md + *.json"] --> CTX["build_*.py\ncontext 조립"]
    CTX --> DISPATCH{"active_theme?"}

    DISPATCH -->|editorial / terminal / minimal| LAYOUT["layouts/{name}.py\nrender_report() 직접 HTML"]
    DISPATCH -->|classic / ink / forest| SKIN["skins/{name}.py\nTOKENS 로드"]

    SKIN --> BASE["base.py\nJinja2 렌더링"]
    BASE --> TPL["templates/web_news.html\nweb_stock.html 등"]

    LAYOUT & TPL --> HTML["publish/YYYY-MM-DD.html"]

    note1["editorial 뉴스: layouts/editorial.py 단독 생성\neditorial 주식: editorial.py → base.py 위임\nclassic/*: base.py + templates/web_*.html"]
```

### 3-2. 이메일 HTML 생성

```mermaid
flowchart TD
    MD["reports/*.md"] --> PARSE["mailer.py\n_parse_md_for_email()\n분석·키워드·통계 추출"]
    PARSE --> THEME["themes.skins.{email_theme}\nTOKENS 로드\n색상 c.navy, c.blue 등"]

    THEME --> JINJA["Jinja2 렌더링"]

    JINJA -->|뉴스| EN["templates/email_news.html\n2단 컬럼 (해외·국내 분석)\n키워드 섹션"]
    JINJA -->|주식| ES["templates/email_stock.html\n온도계 · 핵심요약\n키워드 · 섹터 · 리스크"]
    JINJA -->|AI이슈| EA["templates/email_ai_issue.html"]

    EN & ES & EA --> SMTP["Gmail SMTP 발송\n구독자 개별 발송\n(Supabase 채널별 조회)"]

    note["웹: CSS 변수 var(--color-navy)\n이메일: 인라인 스타일 c.navy = '#0f172a'\n→ 이메일 클라이언트 CSS 변수 미지원 대응"]
```

---

## 4. 구독 시스템

```mermaid
flowchart LR
    subgraph FLOW["구독 흐름"]
        A["사용자 /subscribe"] --> B["api/subscribe.py\nSupabase subscribers 테이블 INSERT\nstatus=pending"]
        B --> C["확인 이메일 발송\n/api/confirm?token=..."]
        C --> D["api/confirm.py\nstatus=active 업데이트"]
    end

    subgraph UNSUB["구독 취소"]
        E["이메일 푸터\n구독 취소 링크\n/api/unsubscribe?email=...&token=..."] --> F["api/unsubscribe.py\nHMAC 토큰 검증\nstatus=unsubscribed"]
    end

    subgraph DB["Supabase DB"]
        G["subscribers 테이블\nemail, channels JSONB\nstatus, is_admin"]
    end

    subgraph SEND["발송 시"]
        H["mailer.py::_get_recipients(channel)\n'news'·'stock'·'ai_issue' 채널 필터\nactivesubscribers만 조회"]
        I["폴백: RECIPIENT_EMAILS\n(Supabase 장애 시)"]
    end

    D --> G
    G --> H
```

---

## 5. 배포 구조

```mermaid
flowchart TD
    GIT["git commit + push\npublish/ 파일"] --> VERCEL["Vercel\n(Git Integration)\ngit push 감지 → 자동 배포"]

    subgraph ACTIONS["GitHub Actions"]
        WF["워크플로우 실행"] --> BUILD["빌드 스크립트\nHTML 생성"]
        BUILD --> COMMIT["git add + commit + push\n(git add -f 날짜별 HTML 포함)"]
        COMMIT --> ART["upload-pages-artifact\npublish/ 전체 업로드"]
        ART --> PAGES["actions/deploy-pages\nGitHub Pages 배포"]
    end

    COMMIT --> VERCEL
    PAGES --> GP["github.io/dailynews\n(백업)"]
    VERCEL --> MS["ms-dailynews.vercel.app\n(메인)"]

    note1["Vercel: git 커밋된 파일만 서비스\n→ git add -f로 날짜별 HTML 강제 추적 필수"]
    note2["GitHub Pages: Actions 아티팩트 전체 서비스\n→ publish/ 전체 자동 포함"]
```

### 파일별 git add 전략

| 파일 유형 | 방법 | 이유 |
|-----------|------|------|
| `publish/news/YYYY-MM-DD.html` | `git add -f` | `.gitignore`로 추적 제외, Vercel 배포용 강제 추가 |
| `publish/app.html`, `index.html` | `git add -f` | 항상 최신 상태 유지 필요 |
| `publish/search-index.json` | `git add -f` | Vercel 검색 기능용 |
| `publish/news/data.json` | `git add -f` | app.html SPA 데이터 소스 |
| `reports/*.md` | `git add` | 소스 파일, 정상 추적 |

---

## 6. 카드뉴스 파이프라인

```mermaid
flowchart LR
    subgraph BUILD["빌드 (build_cardnews.py)"]
        THEME_JSON["config/cardnews_themes.json\n채널별 accent·topbar·label·hashtags"] --> CSS["CSS 커스텀 변수 주입\n:root { --accent: #3b82f6; }"]
        CSS_FILE["templates/cardnews_card.css\n공통 카드 스타일"] --> CSS
        DATA["reports/*.json\ntop3 이슈 제목·요약"] --> HTML_CARD["publish/cardnews/{type}/\nYYYY-MM-DD.html"]
        CSS --> HTML_CARD
    end

    subgraph GEN["이미지 생성 (generate_cardnews_images.py)"]
        HTML_CARD --> PW["Playwright\n헤드리스 브라우저 캡처\n1080×1080 PNG"]
        PW --> PNG["YYYY-MM-DD-1.png\nYYYY-MM-DD-2.png\n..."]
    end

    subgraph POST["SNS 발송 (post_cardnews.py)"]
        PNG --> GH_RAW["GitHub Raw CDN\nhttps://raw.githubusercontent.com/\n.../publish/cardnews/{type}/{date}-{N}.png"]
        GH_RAW --> IG["Instagram 카루셀\n(Graph API v21.0)"]
        GH_RAW --> TH["Threads 카루셀\n(graph.threads.net v1.0)"]
        GH_RAW --> FB["Facebook 멀티사진\n(graph.facebook.com v21.0)"]
        PNG --> TG["Telegram 미디어그룹\n+ 인라인 버튼"]
    end

    note["캡션 링크: 채널별 콘텐츠 페이지\nnews → / , ai-issue → /ai-issue/ , stock → /stock/"]
```

---

## 7. 파이프라인 모니터링

```mermaid
flowchart LR
    subgraph WF["각 워크플로우 마지막 스텝\n(if: always())"]
        JOB["job.status\n(success|failure|cancelled)"]
    end

    JOB --> NP["scripts/notify_pipeline.py\n--type news|stock|ai-issue\n--status success|failure\n--date YYYY-MM-DD"]

    subgraph SUCCESS["성공 메시지"]
        NS["뉴스: 기사 수·AI 분석·키워드·TOP3 이슈"]
        SS["주식: 시장 온도계·핵심 요약 3줄"]
        AS["AI이슈: period·TOP3·카테고리 통계"]
    end

    subgraph FAIL["실패 메시지"]
        FF["채널명 + 날짜시각\n+ GitHub Actions 링크"]
    end

    NP --> SUCCESS & FAIL
    SUCCESS & FAIL --> CHAN["TELEGRAM_CHAT_ID_MONITOR\n별도 모니터링 채널"]

    note["미설정 시 워크플로우 영향 없이 조용히 건너뜀\n(sys.exit(0))"]
```

---

## 8. 설정 파일 맵

| 변경 목적 | 수정 파일 |
|----------|----------|
| 전체 테마 변경 | `config/theme_config.py` → `SITE_THEME` |
| 채널별 테마 독립 설정 | `config/theme_config.py` → `SECTION_THEMES` |
| 색상·폰트 수정 | `themes/skins/{name}.py` → `TOKENS` |
| 뉴스 이메일 레이아웃 | `templates/email_news.html` |
| 주식 이메일 레이아웃 | `templates/email_stock.html` |
| 뉴스 웹 레이아웃 (skins) | `templates/web_news.html` |
| editorial 레이아웃 | `themes/layouts/editorial.py` → `render_*()` |
| RSS 소스 추가·제거 | `config/sources/en_news.py`, `ko_news.py` |
| 주식 감시 종목 | `config/watchlist.yaml` |
| 카드뉴스 색상·해시태그 | `config/cardnews_themes.json` |
| 사이트 제목·URL | `config/theme_config.py` → `SITE_TITLE`, `SITE_BASE_URL` |
| 워크플로우 스케줄 | `.github/workflows/news.yml`, `ai_issue.yml` |
| 구독 API 라우팅 | `vercel.json` |
