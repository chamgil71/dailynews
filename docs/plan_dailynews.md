# 데일리 뉴스 브리핑 — 구현계획서

> 작성일: 2026-05-18 / 최종 갱신: 2026-05-20  
> 상태: **Phase 1 완료 + UI 개선 + JSON 구조화 파이프라인 완료**  
> 목적: 현재 구현 상태 기록 및 Phase 2 계획 정의

---

## 1. 시스템 목표

매일 오전 8시 KST 국내외 주요 뉴스를 자동 수집·분석하여  
이메일 브리핑과 웹사이트를 자동 배포한다.

**핵심 원칙:** 설정(config) - 코드(themes/core) - 콘텐츠(reports/publish) 분리

---

## 2. 현재 구현 상태 (Phase 1 완료)

### 2-1. 파이프라인

```
GitHub Actions cron (매일 08:00 KST)
  │
  ▼
core/collector.py    ← RSS 수집 (영어 4 + 한국어 2 카테고리)
  │                     중복 제거(전일 캐시) + 감시 키워드 분리
  │
  ▼
core/analyzer.py     ← AI 분석 (언어별 2회 호출)
  │                     전략 패턴: Gemini / Claude / GPT 환경변수 교체
  │
  ▼
core/report.py       ← Jinja2 렌더링 → reports/news_YYYY-MM-DD.md
  │
  ├─→ core/mailer.py       ← Gmail SMTP 이메일 (수신자별 개별 발송)
  │
  ├─→ scripts/build_site.py ← MD → HTML (publish/)
  │       parse_md_for_json() → issues/keywords 구조화 추출
  │
  └─→ GitHub Pages 자동 배포
```

### 2-2. 수집

| 항목 | 구현 내용 |
|------|----------|
| RSS 소스 | 영어 4카테고리(technology, ai_ml 등) + 한국어 2카테고리 |
| 피드당 수집 | 최대 8건 |
| AI 전송 | 최대 40건 (EN 60 : KO 40 비율) |
| 중복 제거 | 세션 내 set + 전일 캐시(TTL 23h) |
| 감시 키워드 | `config/keywords.py` — NIPA, 과기정통부 등 |

### 2-3. AI 분석

| 항목 | 구현 내용 |
|------|----------|
| 프롬프트 구조 | `### N. [이슈 제목]` h3 헤더 + 빈줄 분리 → 제목·설명 시각적 구분 |
| JSON 모드 | `PROMPT_TEMPLATE_JSON` — 항상 활성화; issues/trends/category_stats 구조 출력 |
| URL 포함 | title_block에 기사 URL 포함 → AI가 `🔗 주요 출처: [제목](URL)` 작성 |
| JSON 사이드카 | 분석 완료 시 `reports/news_YYYY-MM-DD.json` 자동 저장 |
| 폴백 | API 실패 시 원문 제목 15건 삽입; JSON 파싱 실패 시 텍스트 fallback |

### 2-4. 사이트

| 항목 | 구현 내용 |
|------|----------|
| 출력 경로 | `publish/` (GitHub Pages 서빙) |
| 파일 | index.html, archive.html, app.html, YYYY-MM-DD.html |
| 데이터 파일 | reports.json, reports-data.json (이슈/키워드 구조화) |
| 테마 | classic / minimal / ink / forest / **editorial** / **terminal** |
| 분석 레이아웃 | 해외/국내 2-column CSS Grid; 키워드 섹션 분리 카드 |
| JSON rich UI | editorial: Top Stories 카드 + 카테고리 바 / terminal: Bloomberg 2-column |
| Vercel 배포 | vercel.json 라우팅 완비 (`/`, `/stock`, `/(날짜)` 등) |

### 2-5. 이메일

| 항목 | 구현 내용 |
|------|----------|
| 발송 방식 | Gmail SMTP |
| 수신자 | RECIPIENT_EMAILS (쉼표 구분, 개별 발송) |
| 템플릿 | `templates/email_news.html` (Jinja2) |
| 레이아웃 | 해외/국내 2단 컬럼, 키워드 섹션, 통계 바, 웹 버전 바로가기 |
| 구독취소 | 제거됨 |
| subject_override | 주식시황 등 다른 제목 사용 가능 |

---

## 3. 기술 스택

| 구분 | 기술 |
|------|------|
| 런타임 | Python 3.10+ |
| 뉴스 수집 | feedparser |
| AI | google-genai (Gemini 기본), anthropic, openai |
| 마크다운 | markdown2 |
| 템플릿 | Jinja2 |
| 이메일 | smtplib (Gmail SMTP) |
| 자동화 | GitHub Actions |
| 호스팅 | GitHub Pages |

---

## 4. 설계 원칙 (현재 적용 중)

### 4-1. 설정-코드-콘텐츠 분리

| 레이어 | 파일 | 역할 |
|--------|------|------|
| 설정 | config/ | RSS 소스, 프롬프트, 테마 토큰, 키워드 |
| 코드 | core/, themes/, scripts/ | 수집·분석·렌더링 로직 |
| 콘텐츠 | reports/, publish/ | 실제 생성 파일 (git 관리) |

### 4-2. 테마 시스템

- CSS 디자인 토큰: `config/theme_config.py`
- 렌더러: `themes/base.py` (공통) + 각 테마 모듈
- 전환: `SITE_THEME` 환경변수만 변경

### 4-3. LLM 전략 패턴

- `BaseAnalyzer` 상속 → `GeminiAnalyzer`, `ClaudeAnalyzer`, `GPTAnalyzer`
- `get_analyzer()` → `LLM_PROVIDER` 환경변수 기준 자동 선택
- 나머지 코드 변경 없이 LLM 교체 가능

---

## 5. Phase 2 계획 (미시행)

### 5-1. 카드뉴스 생성

**목표:** `reports-data.json`의 `issues_*`, `keywords_*` 데이터를 활용해 슬라이드형 카드뉴스 HTML 자동 생성

**준비 완료:**
- `_parse_issues()`, `_parse_keywords()` 파서 구현 완료
- `reports-data.json`에 구조화 데이터 저장 중

**필요 작업:**
- `scripts/build_site.py`에 `generate_card_section_html()` 추가
- `templates/card_news.html` 템플릿 작성
- `publish/cardnews/YYYY-MM-DD.html` 출력
- 상세 계획: `docs/plan_cardnews.md` 참조

### 5-2. 주간 트렌드 요약

매주 월요일 오전, 주간 키워드 트렌드를 요약하는 리포트 생성.

### 5-3. 검색·필터 개선

`app.html`의 전문 검색 기능 강화 (키워드 하이라이트, 날짜 필터 UI 개선).

---

## 6. GitHub Actions 워크플로우

```yaml
# .github/workflows/news.yml
on:
  schedule:
    - cron: '0 23 * * *'   # UTC 23:00 = KST 08:00
  workflow_dispatch:

jobs:
  build:
    steps:
      - python main.py
      - python scripts/build_site.py
      - git commit + push (reports/ publish/ storage/)
      - actions/upload-pages-artifact (publish/)
      - actions/deploy-pages
```

---

## 7. 비용

| 항목 | 월 비용 |
|------|---------|
| GitHub Actions | $0 (2,000분/월 무료) |
| Gemini API | $0 (무료 티어, 1일 1회) |
| Gmail SMTP | $0 |
| GitHub Pages | $0 |
| 합계 | $0 |

---

## 8. 환경변수 목록

| 변수 | 필수 | 설명 |
|------|------|------|
| `LLM_PROVIDER` | 선택 | gemini / claude / gpt (기본: gemini) |
| `GEMINI_API_KEY` | Gemini 시 | AIza... |
| `ANTHROPIC_API_KEY` | Claude 시 | sk-ant-... |
| `OPENAI_API_KEY` | GPT 시 | sk-... |
| `GMAIL_USER` | 필수 | Gmail 주소 |
| `GMAIL_APP_PASSWORD` | 필수 | 앱 비밀번호 (16자리) |
| `RECIPIENT_EMAILS` | 필수 | 수신자 목록 (쉼표 구분) |
| `SITE_BASE_URL` | 선택 | GitHub Pages URL |
| `SITE_THEME` | 선택 | classic / minimal / ink / forest |
| `SITE_TITLE` | 선택 | 사이트 제목 |
| `SUBSCRIBE_URL` | 선택 | 구독 URL |
