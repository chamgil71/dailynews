# AI News Brief — 전체 아키텍처

> 중앙 설정(config) → 콘텐츠(MD) → 템플릿 → 테마 → 배포  
> 하드코딩 없이 config 한 곳에서 전체 제어

---

## 1. 핵심 설계 원칙

```
개별 하드코딩 금지
    ↓
config/ 에서 중앙 제어
    ↓
template  : 구조·레이아웃 (HTML 골격)
theme     : 색상·폰트 (시각 스타일)
content   : 수집된 뉴스·주식 데이터 (MD)
    ↓
이 세 가지를 분리하면
테마만 바꿔도 전체 디자인 변경
템플릿만 바꿔도 레이아웃 변경
콘텐츠는 디자인에 무관하게 독립 생성
```

---

## 2. 전체 서비스 구조

```
┌──────────────────────────────────────────────────────────────────────┐
│                         3개 서비스                                    │
│                                                                      │
│  📰 데일리 뉴스        📊 주식시황           🤖 AI이슈 주간          │
│  GitHub Actions       Claude Code 루틴      GitHub Actions           │
│  KST 03:15 매일       KST 21:25 (주)        KST 07:00 매주 일요일    │
│  Gemini 분석          Claude 분석           Gemini 분석              │
│  이메일+텔레그램       이메일(익일 08:00)     이메일+텔레그램+Notion   │
│                                                                      │
│                  ↓ 공통 파이프라인 ↓                                  │
│       MD 파일 → HTML 빌드 → git push → Vercel 배포                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. 공통 파이프라인: MD → HTML → 배포

두 서비스 모두 MD 생성 이후는 **동일한 4단계**를 따른다.

```
[1] MD 생성
    reports/news_YYYY-MM-DD.md
    reports/stock/stock_YYYY-MM-DD.md

        ↓

[2] 빌드 스크립트 (MD → HTML)
    scripts/build_site.py        (뉴스)
    scripts/build_stock_site.py  (주식)
        ↓
    ctx(context) 빌드
        - display_date, stats, site_url 등 메타
        - md_html: markdown2로 변환한 본문 HTML
        - data: 구조화 데이터 (JSON sidecar)

        ↓

[3] 테마 렌더러 호출
    themes/{name}.py::render_report(ctx)
    themes/{name}.py::render_stock_report(ctx)
        ↓
    테마가 template + TOKENS(색상/폰트)를 합쳐 최종 HTML 생성

        ↓

[4] 배포
    publish/YYYY-MM-DD.html        → GitHub Pages + Vercel
    publish/stock/YYYY-MM-DD.html  → GitHub Pages + Vercel
    git add -f → commit → push
    actions/upload-pages-artifact  → GitHub Pages
```

---

## 4. 두 서비스의 차이점

### 서비스별 비교

| 항목 | 📰 데일리 뉴스 | 📊 주식시황 | 🤖 AI이슈 |
|------|--------------|-----------|---------|
| 실행 주체 | GitHub Actions | Claude Code 루틴 (주) + Actions (백업) | GitHub Actions |
| 스케줄 | 매일 KST 03:15 | 루틴 KST 21:25 / 빌드 즉시 / 발송 08:00 | 매주 일요일 KST 07:00 |
| AI 모델 | Gemini (기본) | Claude (루틴) / Gemini (백업) | Gemini (기본) |
| MD 위치 | `reports/news_YYYY-MM-DD.md` | `reports/stock/stock_YYYY-MM-DD.md` | `reports/ai-issue/ai_issue_YYYY-MM-DD.md` |
| 빌드 스크립트 | `build_site.py` | `build_stock_site.py` | `build_ai_issue_site.py` |
| 출력 경로 | `publish/news/` | `publish/stock/` | `publish/ai-issue/` |
| 이메일 발송 | `send_email.py --type news` (즉시) | `send_email.py --type stock` (익일 08:00) | `send_email.py --type ai-issue` (동일 워크플로우) |
| 텔레그램 | ✓ (`send_telegram.py --type news`) | ✓ (`send_telegram.py --type stock`, `@msstockbrief`) | ✓ (`send_telegram.py --type ai-issue`) |
| Notion 동기화 | ✓ (news.yml) | ✓ (stock_send.yml) | ✓ (ai_issue.yml) |

---

## 5. 테마 시스템 (중앙 통제)

### 설정 위치: `config/theme_config.py`

```python
SITE_THEME = os.getenv("SITE_THEME", "editorial")   # ← 전체 기본 테마

SECTION_THEMES = {
    "news":  os.getenv("THEME_NEWS",  SITE_THEME),   # 뉴스 웹
    "stock": os.getenv("THEME_STOCK", SITE_THEME),   # 주식 웹
    "email": os.getenv("THEME_EMAIL", "classic"),    # 이메일 (classic 고정)
}
```

**테마 변경 방법**: `SITE_THEME` 기본값 한 줄만 수정 → 웹 전체 반영  
**섹션별 독립 제어**: `THEME_NEWS`, `THEME_STOCK`, `THEME_EMAIL` 개별 설정 가능

### 테마 파일: `themes/{name}.py`

```
themes/
  classic.py    — 남색 헤더 / 카드 레이아웃
  editorial.py  — 신문 마스트헤드 / Noto Serif KR  ← 현재 기본
  minimal.py    — 넓은 여백 / 오렌지 accent
  ink.py        — 붉은 accent / 신문 느낌
  forest.py     — 에메랄드 accent / 핀테크
  terminal.py   — 다크 모노스페이스 / Bloomberg
```

각 테마는 `TOKENS` (색상, 폰트) + `render_*()` 함수를 가진다.

---

## 6. 웹 서비스 vs 메일링 — 렌더링 방식 차이

### 웹 (HTML 파일 생성)

```
themes/{name}.py::render_report(ctx)
    │
    ├─ [editorial, 뉴스]  editorial.py::render_report() — 직접 HTML 생성
    │   → CSS가 Python 코드 안에 inline 포함
    │   → web_news.html 미사용
    │
    ├─ [editorial, 주식]  editorial.py::render_stock_report() → base.py 위임
    │   → base.py::render_stock_report() + templates/web_stock.html (Jinja2)
    │   → _COMMON_CSS 공유 블록 주입 (css_common 변수)
    │
    └─ [classic/ink/forest]  base.py → Jinja2 렌더링
        → css_root_vars(TOKENS) → :root { --color-navy: #xxx; }
        → templates/web_news.html 에서 var(--color-navy) 사용
        → CSS 커스텀 변수 방식 (웹 브라우저가 해석)
```

### 이메일 (SMTP 발송)

```
mailer.py::send_email()
    │
    ├─ SECTION_THEMES["email"] → theme 로드 → c, t 객체
    │
    ├─ [뉴스 메일]  templates/email_news.html  (Jinja2)
    │   → {{ c.navy }}, {{ c.blue }} ... 인라인 스타일로 직접 주입
    │   → 이메일 클라이언트는 CSS 변수 미지원 → inline style 필수
    │
    └─ [주식 메일]  templates/email_stock.html  (Jinja2)
        → {{ c.navy }}, {{ c.blue }} ... 동일 방식
```

**웹 vs 이메일 색상 적용 방식 차이**

| | 웹 | 이메일 |
|---|---|---|
| 색상 적용 | CSS 변수 `var(--color-navy)` | 인라인 스타일 `{{ c.navy }}` |
| 이유 | 브라우저가 CSS 변수 지원 | 이메일 클라이언트 CSS 변수 미지원 |
| 테마 적용 | `:root` 변수 교체 | Jinja2가 렌더링 시 직접 삽입 |

---

## 7. 배포 흐름 — GitHub Pages vs Vercel

```
GitHub Actions 워크플로우 실행
    │
    ├─ [1] build_site.py / build_stock_site.py
    │       → publish/ 디렉토리에 HTML 파일 생성 (워크스페이스)
    │
    ├─ [2] git commit + push
    │       git add -f publish/YYYY-MM-DD.html      (날짜 HTML, gitignore 우회)
    │       git add -f publish/stock/YYYY-MM-DD.html
    │       git add -f publish/index.html 등 정적 파일
    │       → Vercel은 이 커밋된 파일을 서비스
    │
    └─ [3] actions/upload-pages-artifact (path: publish/)
            → 워크스페이스 전체 publish/ 업로드
            → GitHub Pages는 이 아티팩트를 서비스
```

**두 배포 플랫폼 차이**

| | GitHub Pages | Vercel |
|---|---|---|
| 소스 | Actions 아티팩트 | git 커밋된 파일 |
| 날짜별 HTML | 아티팩트에 포함 ✓ | git add -f 로 강제 커밋 필요 |
| 빌드 필요 | 없음 (정적 파일 업로드) | 없음 (정적 파일 서비스) |
| 라우팅 | 파일 경로 그대로 | `vercel.json` routes 정의 |

---

## 8. 설정 파일 맵 (어디서 무엇을 바꾸나)

| 변경 목적 | 수정 파일 |
|----------|----------|
| 전체 테마 변경 | `config/theme_config.py` → `SITE_THEME` |
| 이메일 테마 변경 | `config/theme_config.py` → `THEME_EMAIL` |
| 색상/폰트 수정 | `themes/{name}.py` → `TOKENS` |
| 뉴스 이메일 레이아웃 | `templates/email_news.html` |
| 주식 이메일 레이아웃 | `templates/email_stock.html` |
| 뉴스 웹 레이아웃 (classic) | `templates/web_news.html` |
| 주식 웹 레이아웃 (classic) | `templates/web_stock.html` |
| editorial 웹 레이아웃 | `themes/editorial.py` → `render_*()` |
| RSS 소스 추가/제거 | `config/sources/en_news.py`, `config/sources/ko_news.py` |
| 주식 감시 종목 | `config/watchlist.yaml` |
| 사이트 제목/URL | `config/theme_config.py` → `SITE_TITLE`, `SITE_BASE_URL` |
| 워크플로우 스케줄 | `.github/workflows/news.yml`, `stock_build.yml` |

---

## 9. 디렉토리 구조

```
dailynews/
│
├── config/                    # 중앙 설정
│   ├── theme_config.py        # 테마·사이트 설정 (핵심)
│   ├── settings.py            # 환경변수 로드
│   ├── watchlist.yaml         # 주식 감시 종목
│   └── sources/               # RSS 소스 목록
│
├── themes/                    # 테마 (색상·폰트·레이아웃)
│   ├── editorial.py           # 현재 기본 테마
│   ├── classic.py
│   ├── base.py                # 표준 테마 렌더링 엔진
│   └── __init__.py            # load_theme()
│
├── templates/                 # HTML 골격
│   ├── email_news.html        # 뉴스 이메일
│   ├── email_stock.html       # 주식 이메일
│   ├── web_news.html          # 뉴스 웹 (classic용)
│   ├── web_stock.html         # 주식 웹 (classic용)
│   ├── daily_report.md        # MD 리포트 골격
│   └── stock_report.md        # 주식 MD 골격
│
├── core/                      # 비즈니스 로직
│   ├── news/                  # 뉴스 수집·분석·리포트
│   ├── stock/                 # 주식 수집·분석·리포트
│   ├── ai_issue/              # AI이슈 수집·분석
│   └── shared/                # mailer, telegram, alerts 공통
│
├── scripts/
│   ├── build_site.py          # 뉴스 MD → HTML + archive.html
│   ├── build_stock_site.py    # 주식 MD → HTML
│   ├── build_ai_issue_site.py # AI이슈 MD → HTML
│   ├── build_cardnews.py      # 카드뉴스 HTML 생성 (--type news|ai-issue|stock|all)
│   ├── generate_cardnews_images.py # HTML → 1080×1080 PNG
│   ├── post_cardnews.py       # 카드뉴스 SNS 발송
│   ├── send_email.py          # 통합 이메일 발송 (--type news|stock|ai-issue)
│   ├── send_telegram.py       # 통합 텔레그램 발송 (--type news|stock|ai-issue)
│   └── sync_notion.py         # Notion 동기화 (3채널 공통)
│
├── reports/
│   ├── news_YYYY-MM-DD.md
│   ├── stock/stock_YYYY-MM-DD.md
│   └── ai-issue/ai_issue_YYYY-MM-DD.md
│
├── publish/                   # 배포 대상
│   ├── index.html             # SPA 메인 (app.html 컴파일)
│   ├── archive.html           # 3탭 아카이브 (뉴스·주식·AI이슈)
│   ├── reports-data.json
│   ├── news/YYYY-MM-DD.html
│   ├── stock/
│   │   ├── index.html / archive.html / stock-data.json
│   │   └── YYYY-MM-DD.html
│   ├── ai-issue/
│   │   ├── index.html / archive.html / ai-issue-data.json
│   │   └── YYYY-MM-DD.html
│   └── cardnews/              # 카드뉴스 빌드 산출물
│       ├── news/YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
│       ├── ai-issue/YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
│       └── stock/YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
│
├── .github/workflows/
│   ├── news.yml               # 뉴스 자동화 (매일 KST 03:15)
│   ├── stock_build.yml        # 주식 빌드 (stock MD push 트리거 + KST 23:00 백업)
│   ├── stock_send.yml         # 주식 발송 (익일 KST 08:00)
│   ├── ai_issue.yml           # AI이슈 주간 (일요일 KST 07:00)
│   └── cardnews.yml           # 카드뉴스 빌드+SNS 발송 (3개 채널 트리거)
│
└── vercel.json                # Vercel 라우팅 설정
```
