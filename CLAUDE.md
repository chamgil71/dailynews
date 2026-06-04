# CLAUDE.md — AI News Brief 프로젝트 컨텍스트

> 세션 시작 시 이 파일을 읽고 현재 상태에서 이어서 작업합니다.
> 세션 종료 전 "CLAUDE.md 업데이트해줘" 로 항상 갱신하세요.

---

## 프로젝트 개요

**레포**: `chamgil71/dailynews`  
**배포**: Vercel (메인) + GitHub Pages (백업)  
**목적**: RSS 뉴스 자동 수집 → AI 분석 → 웹사이트 + 이메일 + 텔레그램 발송

### 3채널 구조
| 채널 | 수집 | 빌드/배포 | 발송 |
|------|------|----------|------|
| 뉴스 | `news.yml` KST 03:15 | 동일 워크플로우 | 배포 완료 후 즉시 |
| 주식 | Claude Code 루틴 09:25 | `stock_build.yml` 23:00 | `stock_send.yml` 익일 08:00 |
| AI이슈 | `ai_issue.yml` 일 07:00 | 동일 워크플로우 | 배포 완료 후 즉시 |

### 핵심 파일 구조
```
core/shared/mailer.py      ← 이메일 발송 로직 (모든 채널 공통)
core/shared/telegram.py    ← 텔레그램 발송 로직 (모든 채널 공통)
scripts/send_email.py      ← 통합 이메일 발송 (--type news|stock|ai-issue)
scripts/send_telegram.py   ← 통합 텔레그램 발송 (--type news|stock|ai-issue)
scripts/run_news.py        ← 뉴스 수집·분석·MD저장 (발송 없음)
scripts/build_site.py      ← 뉴스 HTML 빌드
scripts/build_stock_site.py← 주식 HTML 빌드
scripts/build_ai_issue_site.py ← AI이슈 HTML 빌드
.github/workflows/
  news.yml                 ← 뉴스 전체 파이프라인
  stock_build.yml          ← 주식 빌드·배포
  stock_send.yml           ← 주식 발송 (이메일·Notion·텔레그램)
  ai_issue.yml             ← AI이슈 전체 파이프라인
```

---

## 작업 브랜치 규칙

- **`main`**: 완성·검증된 것만 병합
- Claude Code 웹은 세션마다 브랜치를 자동 생성함 (삭제 가능 — CLAUDE.md가 공유 기억)
- 작업 완료 → main 머지/cherry-pick → 세션 브랜치 삭제 (GitHub UI: /branches)
- 세션 종료 전 반드시 "CLAUDE.md 업데이트해줘" 로 상태 기록

---

## 현재 상태 (2026-06-04)

### 완료된 작업 (main 반영 완료)
- [x] 3채널 파이프라인 발송 순서 통일 (수집→빌드→배포→이메일→텔레그램)
- [x] `send_email.py` / `send_telegram.py` 통합 스크립트 생성 (6개→2개)
- [x] 주식 텔레그램 발송 구현 (`@msstockbrief`, `TELEGRAM_CHAT_ID_STOCK`)
- [x] **PR #18** (`claude/pipeline-fix-clean` → `main`) 병합 완료 (2026-06-03)
- [x] Gemini JSON 파싱 버그 / 주식 이메일 발송 체크 버그 / 주식 섹션 파싱 버그 수정 (2026-06-04)
- [x] **사이트 UI 통합 · 검색 고도화** (2026-06-04) — 세션 4차
  - `SITE_LOGO_HTML` 변수화, 로고명 "AI News Brief" 통일
  - `publish/nav.js` 신설 — 공유 nav 모듈 (URL 깊이 자동 계산)
  - AI이슈 탭 전 페이지 추가 (`NAV_SECTIONS`, `editorial.py`, `nav.js`)
  - SPA 아카이브 탭 → `archive.html` 직접 링크 분리 (내장 섹션 주석)
  - `build_search_index()` 3채널 확장 (뉴스·AI이슈·주식, `type` 필드)
  - `index.html` 사이드바 검색 → 전체 기간 통합 검색 (체크박스 필터)
  - `archive.html` 검색도 동일하게 통합 검색 업그레이드
  - AI이슈 탭 상단 카드뉴스 슬라이더 추가 (top10 → 슬라이드 카드)
  - `archive.html` 검색창 위치 제목 옆으로 이동 (flex row 레이아웃)
  - 서브페이지 4개 nav 탭 인디케이터 통일 (SPA와 동일한 하단 컬러 바)

### 검증 필요 (다음 실행 시 확인)
- [ ] `news.yml` 자동 실행 — Gemini JSON 파싱 성공 여부 (`analysis_ok=true` 확인)
- [ ] `stock_send.yml` workflow_dispatch 수동 실행 → @msstockbrief 채널 수신 확인
- [ ] `ai_issue.yml` 자동 실행 시 deploy-pages 스텝 이후 이메일·텔레그램 실행 확인
- [ ] 통합 검색 Vercel 배포 후 동작 확인 (`search-index.json` fetch 정상 여부) — Vercel 배포 완료 확인됨, 브라우저 강력새로고침(Ctrl+Shift+R) 필요

### 다음 개발 (우선순위 순)
- [ ] 구독 시스템 구현 — Supabase + Vercel API (`docs/plan/roadmap.md` Phase 2 참고)
- [ ] 카드뉴스 SNS 내보내기 — html2canvas, 인스타용 1080×1080 PNG
- [ ] 탭별 색상 테마 (뉴스=파랑, AI이슈=보라, 주식=초록) — 동일 구조 색상만 변경

### 주요 아키텍처 메모
- `publish/archive.html`은 **`themes/editorial.py::render_archive()`** 에서 직접 생성 (Jinja2 미사용)
- `templates/web_archive.html`은 editorial 외 테마(classic/ink 등)용
- `publish/search-index.json`: `build_site.py` 빌드 시 자동 갱신 (뉴스 전체 + AI이슈 + 주식)
- 서브페이지 nav는 `nav.js` 런타임 주입 — 탭 변경 시 `nav.js`만 수정하면 전체 반영

---

## 환경변수 (GitHub Secrets)

| Secret | 용도 |
|--------|------|
| `TELEGRAM_BOT_TOKEN` | @chamgil_news_bot 토큰 |
| `TELEGRAM_CHAT_ID` | 뉴스·AI이슈 채널 ID |
| `TELEGRAM_CHAT_ID_STOCK` | @msstockbrief 채널 ID |
| `GEMINI_API_KEY` | LLM (기본) |
| `GMAIL_USER` / `GMAIL_APP_PASSWORD` | 이메일 발송 |
| `RECIPIENT_EMAILS` | 수신자 목록 |
| `SITE_BASE_URL` | https://ms-dailynews.vercel.app |
| `NOTION_API_KEY` | Notion 동기화 |

---

## 자주 쓰는 명령

```bash
# 현재 브랜치 상태 확인
git status && git log --oneline -5

# main 최신화 후 새 작업 브랜치 생성
git checkout main && git pull && git checkout -b claude/작업명

# 작업 완료 후 push
git add -p && git commit -m "feat: ..." && git push -u origin HEAD
```
