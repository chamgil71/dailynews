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
|------|------|----------|---------|
| 뉴스 | `news.yml` KST 03:15 | 동일 워크플로우 | 배포 완료 후 즉시 |
| 주식 | Claude Code 루틴 21:25 | `stock_build.yml` 23:00 | `stock_send.yml` 익일 08:00 |
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
scripts/build_cardnews.py  ← 카드뉴스 HTML 생성 (--type news|ai-issue|stock|all)
scripts/generate_cardnews_images.py ← HTML → 1080×1080 PNG (Playwright/Pillow)
scripts/post_cardnews.py   ← 카드뉴스 SNS 발송 (--type, --platform instagram|telegram|twitter)
scripts/post_instagram.py  ← Instagram Graph API v21.0 카루셀
.github/workflows/
  news.yml                 ← 뉴스 전체 파이프라인
  stock_build.yml          ← 주식 빌드·배포
  stock_send.yml           ← 주식 발송 (이메일·Notion·텔레그램)
  ai_issue.yml             ← AI이슈 전체 파이프라인
  cardnews.yml             ← 카드뉴스 빌드+SNS 발송 (3개 채널 트리거)
```

### 카드뉴스 출력 구조
```
publish/cardnews/
  news/      YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
  ai-issue/  YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
  stock/     YYYY-MM-DD.html + YYYY-MM-DD-{N}.png + data.json
```

---

## 작업 브랜치 규칙

- **`main`**: 완성·검증된 것만 병합
- Claude Code 웹은 세션마다 브랜치를 자동 생성함 (삭제 가능 — CLAUDE.md가 공유 기억)
- 작업 완료 → main 머지/cherry-pick → 세션 브랜치 삭제 (GitHub UI: /branches)
- 세션 종료 전 반드시 "CLAUDE.md 업데이트해줘" 로 상태 기록

## 주식 루틴 Step 6 — main 직접 push (중요)

Claude Code 웹 환경은 세션 브랜치 제약으로 `git push origin main`이 불가.
**반드시 `mcp__github__push_files` MCP 도구를 사용해 main 브랜치에 직접 커밋한다.**

```
도구: mcp__github__push_files
파라미터:
  owner: chamgil71
  repo: dailynews
  branch: main
  message: "📊 주식 시황 YYYY-MM-DD"
  files: [{ path: "reports/stock/stock_YYYY-MM-DD.md", content: <MD 전체 내용> }]
```

- git add/commit/push 명령어 사용 금지 (세션 브랜치로 푸시되어 PR 생성됨)
- push 성공 시 stock_build.yml이 즉시 트리거 → 빌드·배포·이메일·텔레그램 자동 처리

---

## 현재 상태 (2026-06-10)

### 완료된 작업 (main 반영 완료)
- [x] 3채널 파이프라인 발송 순서 통일 (수집→빌드→배포→이메일→텔레그램)
- [x] `send_email.py` / `send_telegram.py` 통합 스크립트 생성 (6개→2개)
- [x] 주식 텔레그램 발송 구현 (`@msstockbrief`, `TELEGRAM_CHAT_ID_STOCK`)
- [x] **PR #18** (`claude/pipeline-fix-clean` → `main`) 병합 완료 (2026-06-03)
- [x] Gemini JSON 파싱 버그 / 주식 이메일 발송 체크 버그 / 주식 섹션 파싱 버그 수정 (2026-06-04)
- [x] **사이트 UI 통합 · 검색 고도화** (2026-06-04) — 세션 4차
- [x] **PR #19** — 카드뉴스 3채널 SNS 자동 배포 병합 (2026-06-06)
- [x] **PR #20** — `stock_build.yml` analysis_ok 필드 체크 병합 후 추가 수정 (2026-06-06)
- [x] `stock_send.yml` 스케줄 수정 — `0-4` → `0-5` (토요일 아침 금요일 데이터 발송)
- [x] **주식 파이프라인 버그 3종 수정** (2026-06-08) — 세션 7차
  - `api/requirements.txt` 생성 — Vercel Python 함수 의존성 최소화 (requests만), 빌드 실패 수정
  - `stock_build.yml` YAML 구문 오류 수정 — Python 멀티라인을 한 줄로 변경 (모든 stock_build 실패 원인)
  - `stock_2026-06-05.md` 재생성 — 정상 분석 포함 (금 -5.54% 급락 기록)
  - `send_email.py` 요일 레이블 버그 수정 — `now.weekday()` → `report_date.weekday()` (발송일 기준 → 리포트 날짜 기준)
  - `telegram.py` `send_stock_telegram()` — 요일 레이블 추가 (예: "2026-06-08 (월)")
- [x] **Gemini API 과부하 대응을 위한 백업 모델 폴백 구현** (2026-06-09)
  - `config/settings.py`에 `GEMINI_MODEL_FALLBACK` 환경변수 옵션 정의 (기본값 `gemini-2.5-flash`).
  - `core/news/analyzer.py` 및 `core/stock/analyzer.py`에 재시도 로직 강화 (`gemini-3.5-flash` 3회 실패 시 백업 모델로 3회 자동 추가 시도).
- [x] **6/8 주식/6/7 AI이슈 발송 누락 및 미수신 건 분석 완료** (2026-06-09)
  - 6/8 주식: 09:45에 뒤늦게 리포트가 머지되어 08:00에 실행된 `stock_send.yml`이 리포트를 감지하지 못하고 스킵함.
  - 6/7 AI이슈: Actions 로그상 이메일/텔레그램이 정상 송신 완료(250 OK) 되었으므로, 수신자의 스팸함/프로모션 탭 검토 필요.
- [x] **카드뉴스 이미지 구현 및 플랫폼 연동 현황 분석 완료** (2026-06-09)
  - `build_cardnews.py` (HTML), `generate_cardnews_images.py` (Playwright/Pillow 렌더러), `post_cardnews.py` (멀티 SNS 전송) 구현 상태 및 Instagram/Twitter API 토큰 설정 미비 등 확인 완료.
- [x] **주식 루틴 Step 6 push 방식 변경** (2026-06-10)
  - 세션 브랜치 제약으로 `git push origin main` 대신 `mcp__github__push_files`로 main 직접 커밋
  - CLAUDE.md에 "주식 루틴 Step 6" 섹션 추가 (반드시 MCP 도구 사용)
- [x] **이메일 섹션 누락 버그 수정** (2026-06-10)
  - `mailer.py` `_parse_md_for_stock_email()` — 주목 섹터(4), 리스크 요인(5) 파싱 추가; 정규식 룩어헤드 `^\n##` → `\n## ` 수정; 🔵 침체 온도계 색상 파란색 추가
  - `email_stock.html` — 📌 주목 섹터, ⚠️ 리스크 요인 카드 섹션 추가 (핵심 키워드 뒤, 장기투자 앞)
- [x] **이메일 본문 날짜 버그 수정** (2026-06-10) — 세션 8차
  - `mailer.py` `_render_email_template()` / `_render_stock_email_template()` / `send_email()`에 `report_date` 파라미터 추가
  - `send_email.py` `_send_stock()`에서 `report_date=date_str` 전달
  - 원인: `datetime.now()` 사용으로 실행일(발송일)이 리포트 날짜 대신 본문에 표시됨
  - 주의: 원격 커밋 `26f7586`이 `mailer.py`를 덮어써 두 번 적용 필요했음
- [x] **AI이슈 06-07 JSON 블록 렌더링 버그 수정** (2026-06-10) — 세션 8차
  - `core/ai_issue/analyzer.py` — `company_trends_md` / `outlook_md` 파싱 시 Gemini가 `{"summary":"..."}` JSON으로 반환한 경우 summary 필드 자동 추출
  - `reports/ai-issue/ai_issue_2026-06-07.md` — JSON 블록 2개(주요 기업 동향·차주 전망) → 정상 마크다운 변환
  - `publish/ai-issue/2026-06-07.html` — HTML 재빌드
- [x] **Vercel ↔ GitHub Pages 날짜 불일치 원인 수정** (2026-06-10) — 세션 8차
  - 원인: GitHub Pages는 `publish/` 전체 업로드, Vercel은 `news.yml` git add 목록만 배포
  - `news.yml` git add에 `publish/search-index.json`, `publish/news/data.json` 누락 → Vercel에 낡은 인덱스 배포
  - `.github/workflows/news.yml` git add 목록에 두 파일 추가
- [x] **환경변수 전수 조사 및 .env/.env.example 정리** (2026-06-10) — 세션 9차
  - `.env.example`에 `GEMINI_MODEL_FULL/MINI/FALLBACK` 추가, 미사용 `THEME_CARDNEWS` 제거
  - `.env` 중복 `NOTION_API_KEY` 제거, 누락 항목(`TELEGRAM_CHAT_ID_STOCK`, `NOTION_DATABASE_ID_STOCK/AI_ISSUE`, `NAVER_CLIENT_ID/SECRET`, Instagram/Twitter) 플레이스홀더로 추가
  - `NAVER_CLIENT_ID/SECRET` 사용처: `core/stock/collector.py::collect_news_ko()` (주식 국내뉴스 보완, 미설정 시 건너뜀)
  - Instagram/Twitter 키: `post_cardnews.py` / `post_instagram.py`에서 필수값으로 읽음 (미설정 시 `EnvironmentError`)
- [x] **빌드 스크립트 인터페이스 통일 및 카드뉴스 구조 리팩터** (2026-06-10) — 세션 9차
  - `build_ai_issue_site.py`에 `build()` 래퍼 추가 → `build_all.py` 오케스트레이터 인터페이스 통일 (build_site/build_stock 과 일관성)
  - `build_all.py` 내 `build_ai.main()` → `build_ai.build()` 변경
  - `build_cardnews.py` 리팩터: 110줄 하드코딩 CSS → `templates/cardnews_card.css` 분리, `TYPE_ACCENT/TOPBAR/LABEL` → `config/cardnews_themes.json` `channels` 섹션으로 이동
  - CSS Jinja2 `{{ accent }}` → CSS 커스텀 프로퍼티 `var(--accent)` 방식으로 변경 (VS Code CSS 린터 오류 해소)
  - `templates/*.html`의 CSS 린터 오류는 Jinja2 `{{ }}` 변수를 VS Code CSS 파서가 오인한 것 — 런타임 정상, 무시 가능
- [x] **Supabase 구독 시스템 구현** (2026-06-10) — 세션 10차
  - DB: `subscribers` (email, channels JSONB, status, is_admin) + `subscription_tokens` (confirm/manage/unsubscribe)
  - RLS 활성화 — anon 키 차단, service_role만 접근 가능
  - API: `api/subscribe.py` / `api/confirm.py` / `api/unsubscribe.py`(재작성) / `api/manage.py`
  - 공통 헬퍼: `api/_supabase.py` / `api/_smtp.py`
  - 구독 페이지: `publish/subscribe.html` (`/subscribe` 라우팅)
  - `mailer.py` `_get_recipients(channel)` → Supabase 조회, `send_admin_alert()` 추가
  - `send_email.py` 3채널 모두 `channel=` 인자 전달
  - `core/shared/mailer_resend.py` — Resend Batch API 구현 주석 보존
  - `scripts/migrate_subscribers.py` — 기존 RECIPIENT_EMAILS → Supabase 일괄 삽입
  - `vercel.json` 4개 API 라우팅 + `/subscribe` 추가
  - GitHub Secret `SUPABASE_SERVICE_KEY` 등록 완료
- [x] **Supabase 구독자 초기 데이터 등록** (2026-06-10) — 세션 10차
  - `chamgil@gmail.com` / `msshin@nipa.kr` → 3채널 + **is_admin=true** (관리자)
  - `chamg@hanmail.net` → 3채널 + is_admin=false (일반 구독자)
  - RECIPIENT_EMAILS는 Supabase 장애 시 비상 폴백으로만 유지
- [x] **상단 네비게이션 바 구조 통일** (2026-06-10) — 세션 10차
  - 문제: index.html(`.hnav-tab`, 3px, gap:2px)과 stock/news 서브페이지(`header nav a`, 2px, margin-left)가 달랐음
  - 4개 템플릿(`web_stock/news/archive/stock_archive.html`) 헤더 CSS → `index.html` 기준으로 통일
  - `.hnav-tab` 셀렉터, `flex:1` on `.header-nav`, `3px` 하단선, `gap:2px` 탭 간격으로 표준화
  - 전체 페이지 재빌드 완료
- [x] **`.claude/settings.local.json` git 추적 제거** (2026-06-10) — 세션 10차
  - 로컬 Claude Code 퍼미션 파일 — `.gitignore`의 `.claude/` 규칙에 따라 추적 제외

### 주식 파이프라인 완성된 흐름
```
Claude Code 루틴 (21:25 KST, 평일):
  데이터 수집(MCP) → Claude 분석 → MD 저장 → mcp__github__push_files (main 직접)
  → stock_build.yml push 트리거 → HTML 빌드·Pages 배포

stock_build.yml 23:00 스케줄 (백업, 월~금):
  TODAY MD 없음?                → stock_main.py 실행
  TODAY MD 있는데 핵심 요약 비어있음? → stock_main.py 실행 + 텔레그램/이메일 알림
  TODAY MD 있고 내용 정상?       → 건너뜀

stock_send.yml 익일 KST 08:00 (UTC 23:00, 월~토):
  이메일 + Notion + 텔레그램(@msstockbrief) 발송
  (최근 MD ≤3일 이내만 발송)
```

### 검증 필요 (다음 실행 시 확인)
- [x] 6/8(월) 루틴 실행 → `stock_2026-06-08.md` 생성 확인
- [x] 6/9(화) KST 08:00 `stock_send.yml` 실행 및 발송 누락 원인 규명 (요일 레이블 정상 작동 확인)
- [x] 6/10(수) KST 08:00 `stock_send.yml` — 6/9 리포트 재발송 시 본문 날짜 정상 표시 확인 (report_date 버그 수정)
- [ ] `news.yml` 다음 자동 실행 — Vercel search-index 업데이트 포함 여부 확인 (news.yml git add 수정 반영 검증)
- [ ] `ai_issue.yml` 자동 실행 시 deploy-pages 이후 이메일·텔레그램 실행 확인
- [ ] `cardnews.yml` workflow_dispatch 수동 실행 → 텔레그램 수신 확인 (--type news)
- [ ] AI이슈 다음 실행 시 Gemini JSON 응답 감지 로직 정상 작동 확인 (analyzer.py 수정 반영)

### 검증 필요 (구독 시스템)
- [ ] Vercel 배포 후 `/subscribe` 페이지 접속 확인
- [ ] 구독 신청 → 확인 이메일 수신 → confirm 링크 클릭 → Supabase status=active 확인
- [ ] 이메일 발송 시 Supabase 구독자 조회 정상 작동 확인 (RECIPIENT_EMAILS 폴백 아닌 Supabase 조회)
- [ ] 채널 관리(`/api/manage`) 정상 작동 확인
- [ ] `TELEGRAM_CHAT_ID_STOCK` GitHub Secret 등록 필요 (현재 미등록)
- [ ] `NOTION_DATABASE_ID_STOCK` / `NOTION_DATABASE_ID_AI_ISSUE` 실제 값으로 교체 필요

### 다음 개발 (우선순위 순)
- [ ] SNS 카드뉴스 자동 발송 기능 활성화 (`INSTAGRAM_ACCESS_TOKEN`, `TWITTER_API_KEY` 등 Secrets 등록 및 검증)
- [ ] 탭별 색상 테마 (뉴스=파랑, AI이슈=보라, 주식=초록) — 동일 구조 색상만 변경
- [ ] `cardnews.yml` 텔레그램 발송 수동 검증 → 정상 수신 확인
- [ ] 구독 알림 이메일 템플릿 개선 (현재 인라인 HTML → `templates/email_confirm.html` 분리)

### 주요 아키텍처 메모
- `publish/archive.html`은 **`themes/editorial.py::render_archive()`** 에서 직접 생성 (Jinja2 미사용)
- `templates/web_archive.html`은 editorial 외 테마(classic/ink 등)용
- `publish/search-index.json`: `build_site.py` 빌드 시 자동 갱신 (뉴스 전체 + AI이슈 + 주식)
- 서브페이지 nav는 `nav.js` 런타임 주입 — 탭 변경 시 `nav.js`만 수정하면 전체 반영
- 카드뉴스 `data.json`: 채널별 서브디렉터리에 위치 (`publish/cardnews/{type}/data.json`)
- 카드뉴스 GitHub raw URL: `https://raw.githubusercontent.com/chamgil71/dailynews/main/publish/cardnews/{type}/{date}-{n}.png`
- **주식 품질 게이트**: `run_stock.py`의 `_is_analysis_complete()` — summary + temperature_reason 둘 다 있어야 통과
- **백업 분析 판단**: `stock_build.yml` check_md — MD의 `## ■ 핵심 요약` 섹션 내용 파싱 (stock-data.json 미사용)
- **Vercel vs GitHub Pages 배포 차이**: GitHub Pages는 `publish/` 전체 업로드, Vercel은 `news.yml` git add 목록만 배포 → `search-index.json`, `news/data.json` 반드시 git add에 포함 필요
- **Gemini 비정형 응답**: markdown 요청에 `{"summary":"..."}` JSON으로 반환하는 경우 있음 — `analyzer.py`에서 `_parse_json_block()` 후 summary 필드 추출로 대응
- **카드뉴스 구조**: `templates/cardnews_card.css` (CSS, CSS var() 사용) + `config/cardnews_themes.json` (채널별 accent/topbar/label/hashtags) → `build_cardnews.py`가 로드하여 `_render_css()`로 `:root { --accent: ...; }` 주입
- **카드뉴스 텔레그램 발송**: `post_cardnews.py::post_telegram()` — PNG `sendMediaGroup` + 인라인 버튼 `sendMessage` 후속 전송
- **빌드 스크립트 인터페이스**: `build_site.build()` / `build_stock_site.build()` / `build_ai_issue_site.build()` 모두 `build()` 함수 통일 → `build_all.py` 오케스트레이터에서 동일 방식 호출
- **`templates/*.html` CSS 린터 오류**: Jinja2 `{{ }}` 변수를 VS Code CSS 파서가 오인한 것, 런타임 정상 동작 — 무시 가능
- **Supabase 구독 시스템**: `api/_supabase.py` + service_role 키로 서버에서만 접근. RLS 활성화, anon 키 차단. 구독자 채널별 선택: `channels JSONB {"news","stock","ai_issue"}`. 관리자: `is_admin=true`
- **관리자 vs 구독자**: is_admin=true → `send_admin_alert()` 시스템 알림 수신. 일반 구독자 → 채널별 브리핑만 수신. RECIPIENT_EMAILS는 Supabase 조회 실패 시 폴백
- **헤더 CSS 통일**: `templates/web_*.html` 4개 모두 `.hnav-tab` + `flex:1` + `3px border` 구조로 통일. `index.html`(editorial SPA)이 기준
- **`CLAUDE.md` 위치**: 프로젝트 루트가 표준 위치. Claude Code가 세션 시작 시 자동 로드하는 프로젝트 컨텍스트 파일. `.claude/`(디렉터리)와 다름 — `.gitignore`의 `.claude/`는 디렉터리만 차단

---

## 환경변수 (GitHub Secrets)

| Secret | 용도 | 상태 |
|--------|------|------|
| `GEMINI_API_KEY` | LLM (기본) | ✅ |
| `GMAIL_USER` / `GMAIL_APP_PASSWORD` | 이메일 발송 | ✅ |
| `RECIPIENT_EMAILS` | Supabase 장애 시 비상 폴백 | ✅ |
| `SITE_BASE_URL` | https://ms-dailynews.vercel.app | ✅ |
| `UNSUBSCRIBE_SECRET` | 레거시 HMAC 구독취소 링크 호환 | ✅ |
| `SUPABASE_SERVICE_KEY` | Supabase 구독 시스템 (service_role) | ✅ |
| `TELEGRAM_BOT_TOKEN` | @chamgil_news_bot 토큰 | ✅ |
| `TELEGRAM_CHAT_ID` | 뉴스·AI이슈 채널 ID | ✅ |
| `TELEGRAM_CHAT_ID_STOCK` | @msstockbrief 채널 ID | ⚠️ **미등록** |
| `NOTION_API_KEY` | Notion 동기화 | ✅ |
| `NOTION_DATABASE_ID_NEWS` | Notion 뉴스 DB | ✅ |
| `NOTION_DATABASE_ID_STOCK` | Notion 주식 DB | ⚠️ **미등록** |
| `NOTION_DATABASE_ID_AI_ISSUE` | Notion AI이슈 DB | ⚠️ **미등록** |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | 주식 국내뉴스 수집 | ⚠️ **미등록** |
| `GH_CONTENTS_TOKEN` | GitHub Contents API | ✅ |
| `INSTAGRAM_ACCESS_TOKEN` | Meta Graph API (60일 만료 주의) | ❌ 미설정 |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business ID | ❌ 미설정 |
| `TWITTER_API_KEY` / `TWITTER_API_SECRET` | Twitter Developer App | ❌ 미설정 |
| `TWITTER_ACCESS_TOKEN` / `TWITTER_ACCESS_TOKEN_SECRET` | Twitter OAuth 1.0a | ❌ 미설정 |

---

## 자주 쓰는 명령

```bash
# 현재 브랜치 상태 확인
git status && git log --oneline -5

# main 최신화 후 새 작업 브랜치 생성
git checkout main && git pull && git checkout -b claude/작업명

# 작업 완료 후 push
git add -p && git commit -m "feat: ..." && git push -u origin HEAD

# 카드뉴스 수동 빌드 테스트
python scripts/build_cardnews.py --type news
python scripts/generate_cardnews_images.py --type news
python scripts/post_cardnews.py --type news --platform telegram
```
