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
scripts/migrations/        ← 일회성 마이그레이션 스크립트 (init_db, migrate_*)
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

## 현재 상태 (2026-06-19)

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
  - Instagram/Twitter 키: `post_cardnews.py`에서 필수값으로 읽음 (미설정 시 `EnvironmentError`)
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
- [x] **SNS 카드뉴스 Threads + Facebook 발송 구현** (2026-06-10) — 세션 11차
  - `post_cardnews.py::post_threads()` — Threads 카루셀 (graph.threads.net v1.0)
  - `post_cardnews.py::post_facebook()` — Facebook Page 멀티 사진 (graph.facebook.com v21.0)
  - `post_cardnews.py::post_telegram()` — 채널 분기 추가 (stock→`TELEGRAM_CHAT_ID_STOCK`, 그 외→`TELEGRAM_CHAT_ID`)
  - `cardnews.yml` 기본 플랫폼: `instagram,threads,facebook,telegram`
  - GitHub Secrets 전체 등록 완료: Instagram/Facebook/Threads/Naver/TelegramStock
  - `.env`·`.env.example` 전체 정비 (Facebook·Threads 키 활성화)
  - `docs/sns_design_guide.md` 신규 — 5개 플랫폼 발송 방식·캡션·환경변수 명세
- [x] **docs/ 현행화 정리** (2026-06-10) — 세션 11차
  - backup/ 이동: `analysis_2026-06-09`, `chat_history_analysis`, `stock_briefing_routine_v4`, `worklog`
  - plan/ 이동: `ai_issue_report_plan` → `plan/plan_ai_issue.md`
  - 파일명 통일: `meta-sns-setup` → `sns_meta_setup`, `stock_routine_prompt_v5` → `stock_routine`
  - 신규: `docs/scripts_guide.md` — 21개 스크립트 역할·사용법·워크플로우 매핑
  - `docs/env_spec.md` 전면 재작성 — 현황 반영, Facebook/Threads 추가
  - `plan/plan_subscription_system.md` — 구현 완료 현황 표 추가
- [x] **MS News Design System 패치 P0–P4 전체 적용** (2026-06-11) — 세션 12차
  - **P0**: `email_stock.html` 섹션 헤더 색상 navy 통일, `email_news.html` ko-col 링크 blue, `terminal.py` 버그 수정(잘못된 theme 이름 참조) + 이모지 제거
  - **P1**: `themes/base.py` `_COMMON_CSS` 전면 교체 (~125줄→~230줄) — `.hnav-tab`/`.header-nav`/`.section-abbr`/`.tag-row`/`.temp-indicator` 신규, `--color-up/down` CSS 변수 별칭 추가, `web_stock.html` 37줄로 리라이트 (css_common 주입)
  - **P2**: `header.html` 이모지 제거 + SVG 테마 버튼, `web_news.html` 리라이트 (analysis-grid 2단, section-kicker, details 뉴스목록), `web_archive.html` 리라이트, `editorial.py`/`minimal.py` 이모지 전수 제거
  - **P3**: `publish/nav.js` 전면 재작성 — 탭별 active border 색상 분기(뉴스=파랑/AI이슈=보라/주식=초록), `id="site-nav"` legacy 경로와 `.header-nav` 경로 이중 처리, `_COMMON_CSS` per-tab CSS 규칙 추가
  - **P4**: `web_news.html` `.tag-row` span→a태그 전환 (날짜→`../archive.html`, KO/EN→`#앵커`), `details` id 추가, `_COMMON_CSS` `a.tag` hover(navy) + `::after` 44px 터치 타깃 확장
- [x] **구독/구독취소 링크 전체 연결** (2026-06-11) — 세션 12차 (계속)
  - `config/theme_config.py`: `SUBSCRIBE_URL` 기본값 → `SITE_BASE_URL + "/subscribe"` 자동 연동 (Google Forms placeholder 제거)
  - `templates/header.html`: 헤더 우상단 `.btn-subscribe` 구독 버튼 추가 (classic/ink/forest/editorial-stock 적용)
  - `themes/editorial.py`: masthead nav에 구독 버튼 추가 (뉴스·AI이슈·아카이브 editorial 페이지 전체 적용)
  - `themes/base.py`: `render_report`/`render_stock_report`에 `subscribe_url` 전달, `SUBSCRIBE_URL` import, `.btn-subscribe` CSS
  - `core/shared/mailer.py`: `unsubscribe_url` = HMAC 토큰 기반 실제 링크 (`/api/unsubscribe?email=...&token=...`)로 수정 (2곳)
  - `templates/email_news.html`: 푸터에 "구독 취소" 링크 추가
  - `templates/email_stock.html`: 주석 처리된 구독취소 링크 활성화 + 레이아웃 정리
  - `docs/chat_history/clauderoutine_v5`: Step4 핵심 키워드 설명(1~2문장) 복원, MD 템플릿 형식 수정 (v5 업데이트 시 축약된 부분)
- [x] **Vercel 배포 지연 원인 수정 및 앱 UI 정비** (2026-06-12) — 세션 13차
  - 원인: 모든 워크플로우 커밋 메시지에 `[skip ci]` → Vercel Git Integration도 스킵 (GitHub Actions와 동일하게 적용됨)
  - `news.yml` / `ai_issue.yml` / `cardnews.yml`: 커밋 메시지에서 `[skip ci]` 제거
  - `stock_build.yml`: `[skip ci]` 제거 + `if: github.actor != 'github-actions[bot]'` 루프 방지 (stock MD push → build → stock MD 커밋 순환 차단)
  - `publish/app.html`: 이모지 제거, 구독 버튼 + SUBSCRIBE_URL_PLACEHOLDER 추가, 날짜 리스트 7개 스크롤 제한
  - `scripts/build_site.py`: SUBSCRIBE_URL_PLACEHOLDER → 실제 URL 치환 로직 추가
  - `api/_supabase.py`: `SUPABASE_SERVICE_KEY` 누락 시 "Vercel 대시보드에서 등록 필요" 명확한 에러 메시지 추가
  - `publish/privacy.html` 신규 — 개인정보처리방침 (수집항목·목적·제3자·Supabase·Gmail 명시)
  - `publish/ads.txt` 신규 — `google.com, pub-3073080552425149, DIRECT, f08c47fec0942fa0`
  - `vercel.json`: `/ads.txt`, `/privacy` 라우팅 추가
  - `publish/subscribe.html`: 개인정보처리방침 링크 추가
  - `.env` / `.env.example`: 각 키 획득처 주석 상세화
  - `docs/env_spec.md` 전면 재작성 — GitHub Secrets vs Vercel 환경변수 구분, 키별 획득 단계 명시
- [x] **Google AdSense 삽입 (dailynews)** (2026-06-12) — 세션 13차
  - `publish/app.html`: AdSense 스크립트(`ca-pub-3073080552425149`) + 사이드바 하단 광고 `.ad-card` (228×200)
  - 메인 상단 배너 광고는 UX 저해로 제거 → 사이드바만 유지
- [x] **4개 UI 이슈 수정 + 날짜 하루 뒤처짐 근본 수정** (2026-06-12) — 세션 14차 — **PR #27 머지 완료**
  - **상단 nav 이모지 불일치**: `templates/header.html` + `publish/nav.js` + `themes/base.py` 모바일 CSS — 모든 페이지 이모지(📰🤖📈📚) 통일
  - **메인 광고 영역 제거**: `publish/index.html` 재빌드 (`app.html` 광고 없는 버전 기준)
  - **주식 키워드 설명 누락**: `scripts/build_stock_site.py` `_parse_keywords()` v6 포맷(`① 제목: 설명`) 파싱 추가 — `data.json` 21건 재생성
  - **날짜 항상 하루 뒤처짐 근본 수정**: `stock_build.yml` git add 구조 변경
    - 원인: `git add -f publish/stock/data.json 2>/dev/null || true` 한 줄 다중파일 처리 → 앞 파일 에러 시 뒤 파일 누락, 에러 숨겨짐
    - 수정: `data.json`, `index.html`, `archive.html` 각각 단독 `git add` 라인으로 분리 (no -f, no 2>/dev/null)
    - 이 패턴으로 edeed23 이후 모든 stock_build.yml 자동 실행이 data.json 업데이트 실패
  - **Facebook `META_PAGE_ACCESS_TOKEN` 만료**: 2026-06-10 PDT 만료 → Facebook Developers에서 재발급 필요
  - **cardnews.yml CDN 체크 버그**: `ls ... | sort | head -1` (가장 오래된 파일) → `sort | tail -1` (최신 파일) 수정 (PR #27 이전에 main 직접 push 완료)
- [x] **SPA·이메일·텔레그램 버그 5종 수정** (2026-06-14) — 세션 15차 — **PR #30 머지 완료**
  - **구독 버튼 아이콘 통일**: SPA `app.html` "구독" 텍스트 → SVG 메일 아이콘 (editorial/stock과 동일)
  - **헤더 높이 통일**: `editorial.py` `.site-header { height:52px }` → `58px` (SPA/stock과 통일)
  - **AI이슈 분석 실패 텔레그램 알림**: `scripts/run_ai_issue.py` — `top10` 공란 및 LLM 예외 시 `_telegram_alert()` 추가
  - **이메일 text/plain 폴백**: `core/shared/mailer.py` — `_html_to_plain()` 추가, `multipart/alternative` 구조에서 `text/plain` 먼저 첨부 (Outlook/기업 메일 호환)
  - **이메일 배지 보라색**: `templates/email_ai_issue.html` — `.badge` CSS 클래스 → 인라인 `style` 직접 지정 (Gmail CSS 스트리핑 대응)
  - **ai_issue.yml git add 경합 수정**: 다중파일 `2>/dev/null || true` 패턴 → 파일별 단독 `git add` (data.json 누락 방지)
  - **텔레그램 next_week_outlook JSON 파싱**: `core/shared/telegram.py` — LLM이 `{"points":[...]}` JSON으로 반환한 경우 `points[].point` 추출
  - **AI이슈 06-14 데이터 복구**: `reports/ai-issue/ai_issue_2026-06-14.json` 재체크아웃 (top10:10 정상 버전) + HTML 재빌드
  - **SPA 탭 경합 방지 (두개디자인 버그)** (2026-06-14):
    - 원인: SPA AI이슈/주식 탭의 `href="ai-issue/"` / `href="stock/"` 링크가 모바일에서 JS 핸들러보다 탭이 빠를 때 editorial 서브페이지로 이탈
    - 수정: `publish/index.html` — 비-archive 탭 `href` → `href="#"` (이탈 원천 차단)
    - 수정: `scripts/build_site.py` — NAV_INJECT 후 SPA 맥락 href 치환 (빌드 영구 반영) + `SECTION_DEFAULTS["ai-issue"]` 추가
- [x] **scripts 정리 — build_cardnews 중복 제거 + migrations 폴더 + post_instagram 삭제** (2026-06-14) — 세션 17차 — **PR #33 머지 완료**
  - `build_cardnews.py`: `_chg_color`/`_stat_row`/`_stat_section` 헬퍼 추출로 중복 제거 (682→648줄)
  - `scripts/migrations/` 신규 폴더: `init_db.py`, `migrate_json_sidecars.py`, `migrate_subscribers.py` 이동
  - `post_instagram.py` 삭제: `post_cardnews.py::post_instagram()`에 완전 흡수, 워크플로우 미참조
  - scripts 파일 수 22 → 18개 (migrations/ 제외)
- [x] **텔레그램 미리보기 날짜 고착 + SPA 헤더 배경색 + Instagram ImportError + cardnews 에러 알림** (2026-06-19) — 세션 19차 — **PR #37 머지 완료**
  - `notify_pipeline.py`: `disable_web_page_preview: true` 추가 — 매일 같은 URL 발송 시 텔레그램이 과거 OG 미리보기를 재캐시하는 문제 (06-16 내용인데 06-12로 표시됨)
  - `publish/app.html` / `publish/index.html`: `<header data-section="news">` + 섹션별 CSS gradient(`switchSection()` 업데이트) — 탭 전환 시 헤더 전체 배경이 뉴스(#0f2a52)/AI이슈(#2e1f57)/주식(#103a26)으로 변경
  - `scripts/post_cardnews.py`: PR #33에서 `post_instagram.py` 삭제 후 남은 dead import(`from scripts.post_instagram import ...`) 제거 → Instagram 카루셀 로직 인라인 (`_ig_post`, `_ig_get`, `_ig_wait_container` 헬퍼 추가)
  - `cardnews.yml`: SNS발송 스텝에 `id: sns` 부여 → `steps.sns.outcome == 'failure'` 조건 알림 스텝 추가 (`if: always()`)
  - `notify_pipeline.py`: `--type cardnews` 지원 추가 (`_msg_cardnews_success()` + `_msg_failure()` 레이블 "카드뉴스 SNS")
  - **Threads 18/19 누락 원인**: 06-19 Actions 로그 확인 → Threads 성공(`id: 18008775413920537`), Instagram ImportError가 `sys.exit(1)` + `continue-on-error:true`로 에러 알림 없이 묻혔던 것. Instagram 버그 수정으로 다음 실행부터 정상화
- [x] **클로드 루틴 요일 오판 방지 + 파이프라인 모니터링 알림 폴백** (2026-06-16) — 세션 18차 — **PR #34·#35 머지 완료**
  - **PR #34**: 클로드 루틴 Step 0 추가 — `stock_routine_v6.md` / `clauderoutine_v5`에 `python3 datetime.date.today().weekday()` 강제 확인 명령 삽입 (내부 계산 금지 경고 포함)
    - 원인: 2026-06-15(월요일)을 Claude AI가 "일요일"로 오판 → 루틴 조기 종료 → `stock_2026-06-15.md` 미생성 (백업 워크플로우가 복구)
  - **PR #35**: 4개 워크플로우(news/stock_build/ai_issue/weekly_build) notify 스텝 env에 `TELEGRAM_CHAT_ID` 폴백 추가
    - 원인: `TELEGRAM_CHAT_ID_MONITOR` 등록 여부에 상관없이 `TELEGRAM_CHAT_ID` 폴백이 전달되지 않아 알림 경로 누락 가능성
    - `TELEGRAM_CHAT_ID_MONITOR` Secret 등록 확인됨 → GitHub Actions 알림은 해당 채널로 정상 발송
    - 클로드 루틴 조기 종료는 GitHub Actions 외부이므로 어떤 채널로도 자동 알림 불가 (설계 한계)
  - `stock_2026-06-15.md` 수동 복구: 사용자가 v6 루틴으로 재생성 (코스피 8,545 +5.2%, 미·이란 종전합의)
    - 백업 `stock_build.yml` 스케줄이 UTC 14:00에 자동 발동 → 먼저 복구됐으나 사용자 v6 버전으로 덮어씀
- [x] **archive 탭 두개디자인 버그 근본 수정 + 6-13 오염 파일 삭제** (2026-06-14) — 세션 17차 — **PR #32 머지 완료**
  - **원인 1**: `archive.html` nav의 ai-issue/stock 탭 href가 editorial 서브페이지(`ai-issue/`, `stock/`)를 가리켜 다른 디자인으로 이탈
  - **원인 2**: 토요일 잘못 생성된 `stock_2026-06-13.md` / `2026-06-13.html/json` 오염 파일
  - `themes/layouts/editorial.py::_layout()` — `nav_hrefs` 파라미터 추가 (탭별 href 개별 재정의)
  - `themes/layouts/editorial.py::render_archive()` — ai-issue/stock 탭을 `index.html#ai-issue`, `index.html#stock`으로 재정의
  - `publish/app.html` + `publish/index.html` (SPA) — 초기화 시 `location.hash` 감지, `#ai-issue`/`#stock`이면 해당 탭 자동 활성화 후 hash 제거
  - `reports/stock/stock_2026-06-13.md` / `publish/stock/2026-06-13.html/json` 삭제
  - stock/news 사이트 재빌드
- [x] **주식 주말 실행 차단 + 루틴 날짜 규칙 명확화 + 파이프라인 점검 문서** (2026-06-14) — 세션 16차 — **PR #31 머지 완료**
  - `run_stock.py` 주말(토·일) 감지 시 경고만 출력 → `return`으로 즉시 종료 (오염 파일 생성 차단)
  - `docs/stock_routine.md` Step 5/6: 파일명·제목의 날짜는 **거래일(trading_date)** 기준 명시 (⚠️ 실행일 아님)
  - `docs/pipeline_audit.md` 신규 — 3채널 파일 생성 루틴 전체 점검: 흐름·날짜 규칙·버그 이력·재발 방지 체크리스트
  - 카드뉴스 제목: `config/cardnews_themes.json` "Stock Brief" → "AI Stock Brief", `keyword` 필드 추가(News/Issue/Stock)
  - `build_cardnews.py::_render_label()` 추가 — 채널 keyword를 accent 색으로 강조
  - `notify_pipeline.py` weekly-stock 타입 추가 — `weekly_{date}.md` 읽어 주간 총평·지수·테마 텔레그램 발송
  - `weekly_build.yml` `--type stock` → `--type weekly-stock` 변경
  - `cardnews.yml` workflow_run에 `"Weekly Stock Build"` 트리거 추가
  - **Threads 텍스트 모드**: `post_threads()`를 text/carousel 이중 모드로 분리
    - `cardnews_themes.json` 채널별 `threads_mode: "text"` 설정 추가 (설정으로 제어)
    - `_get_threads_mode(channel)` — config에서 모드 로드
    - `_post_threads_text()` — TEXT media_type 텍스트 단독 게시 (기본)
    - `_post_threads_carousel()` — 기존 카루셀 로직 함수 분리 (mode="carousel"로 전환 가능)
    - 주석: Instagram은 텍스트 단독 포스트 불가, Threads는 가능
  - **`news.yml` stock git add 수정**: 다중 파일 한 줄 → 파일별 단독 라인, `publish/stock/data.json` 누락 추가
    - 원인: Vercel에서 stock 데이터가 갱신 안 된 근본 원인 (data.json이 git add 목록에 없었음)
- [x] **Notion 주식시황 동기화 버그 수정** (2026-06-12) — 세션 13차
  - **Summary 파싱 버그**: `_parse_stock_md()`가 `- ` 리스트만 파싱 → 핵심요약(단락) 스킵 → 리스크 섹션 내용이 Summary로 기록됨
  - `scripts/sync_notion.py`: Summary를 `## 3. 핵심 키워드 TOP 5` 섹션에서 파싱으로 변경
    - 형식 A `① 키워드: 설명` → `[키워드] 설명` / 형식 B `#태그` → `[태그]` 양방향 처리
  - **시장온도 누락**: `notion.py`에 `시장온도` 컬럼 처리 자체 없었음 → 추가
    - `_parse_stock_md()`: `## 시장 온도계: 🟠 상승` 파싱 추가
    - `notion.py::sync_stock_to_notion()`: `temperature` 파라미터 + `시장온도` 컬럼 매핑 추가
  - **제목 형식 통일**: `주식 시황 YYYY-MM-DD` → `📊 주식 시황 브리핑 — YYYY-MM-DD` (MD 파일 H1과 동일)
  - 참고: 초기 레코드 형식 불일치는 v4 루틴이 Claude MCP로 직접 Notion에 썼던 것. v5부터 stock_send.yml이 담당
- [x] **카드뉴스 발송 순서 + Threads 캡션 내용 누락 수정** (2026-06-17) — 세션 20차
  - **발송 순서 버그**: `stock_build.yml` 완료 → `cardnews.yml` 트리거로 카드뉴스가 밤에 먼저 발송, 텍스트 요약은 익일 08:00으로 순서가 뒤집혀 있었음
  - `cardnews.yml` `workflow_run` 트리거: `"Stock Briefing Build"` → **`"Stock Briefing Send"`** 로 변경 (텍스트 먼저→카드뉴스 나중 순서 정렬)
  - **Threads 캡션 빈 이유**: `cardnews/{channel}/data.json`에 `issue_titles`/`summary` 필드가 없어 `_build_caption()`이 날짜+링크+해시태그만 출력 (3채널 모두 해당, 기존 버그)
  - `build_cardnews.py::_update_index()`: `extra_data: dict[str,dict]` 파라미터 추가 + 기존 index 로드→merge (이전 빌드의 extra 필드 보존)
  - `build_cardnews.py::build_stock()`: `all_entries`에서 `summary`/`keywords`/`temperature`를 `extra_data`로 수집 → `_update_index()` 전달
  - `build_cardnews.py::build_news()`: `publish/news/data.json`의 `structured.ko.issues[].title` → `issue_titles` extra_data로 저장
  - `build_cardnews.py::build_ai_issue()`: `top10[].title` → `issue_titles` extra_data로 저장
  - `post_cardnews.py::_build_caption()`: stock 채널 분기 추가 — 🌡 시장온도 / 📌 핵심요약(2줄) / 🔑 키워드(3개) 포함 캡션 생성
- [x] **반복 버그(날짜·중간생성누락·채널별 로직 불일치) 구조적 점검 및 1차 수정** (2026-06-16) — 세션 19차
  - **점검 방법**: 3개 영역(날짜 처리, 워크플로우 git add/중간생성 누락, 채널별 로직 일관성)을 서브에이전트로 병렬 조사
  - **핵심 진단**: `mailer.py`/`telegram.py`는 일찍이 통합됐지만, 실행 진입점(`run_*.py`)의 실패 알림·날짜 계산·워크플로우 git add·품질 게이트는 채널마다 복붙 후 변형되어 한쪽을 고쳐도 다른 채널엔 반영이 안 되는 게 반복 버그의 근본 원인으로 확인됨
  - **문서-코드 불일치 발견**: "PR #27에서 git add 단독 라인 분리 완료"로 기록돼 있었으나 실제로는 `ai_issue.yml`만 고쳐지고 `news.yml`/`stock_build.yml`/`weekly_build.yml`은 3파일 결합 라인이 그대로 남아있었음 — **문서의 "수정 완료" 기록을 그대로 믿지 말 것** (아래 패턴 9 참조)
  - **수정 1**: `news.yml`/`stock_build.yml`/`weekly_build.yml`의 `git add -f app.html index.html archive.html 2>/dev/null || true`(3파일 결합) → 파일별 단독 라인 분리. 죽은 코드(`reports.json`/`reports-data.json`) 제거
  - **수정 2**: `core/shared/alert.py` 신설 — `run_news.py`/`run_stock.py`/`run_ai_issue.py`가 각자 구현하던 SMTP/텔레그램 알림 함수 3종을 `send_pipeline_alert(channel, date_str, reason)` 하나로 통합. 기존 `mailer.send_admin_alert()` 재사용
  - **수정 3**: `core/shared/report_date.py` 신설 — `kst_today()`로 KST 날짜 계산을 환경변수(TZ) 의존 없이 통일. `mailer.py`/`telegram.py`의 `now()` 무음 폴백 제거(텔레그램은 `date_str` 필수 파라미터화, 메일은 폴백 시 경고 로그 추가)
  - **수정 3 부수 발견**: `run_stock.py`의 `send_email()` 호출에 `channel="stock"`이 빠져 있어 주식 이메일이 뉴스 구독자 채널로 갈 뻔한 버그, `_send_news`(`send_email.py`)의 `report_date` 누락 버그 — 둘 다 수정
  - **수정 4**: 뉴스 파이프라인 품질 게이트 추가 — 이메일·텔레그램은 이미 `analysis_ok` 플래그로 발송을 막고 있었는데 **사이트 빌드·Notion 동기화만 이 체크가 없어** 분석 실패해도 깨진 콘텐츠가 배포되는 빈틈 발견 → `news.yml`에 `분석 결과 확인` 스텝 추가해 동일 기준으로 차단
  - **검증 범위**: `actionlint`(GitHub Actions 공식 정적분석기) 전체 워크플로우 통과, `py_compile`+모듈 import 전체 통과, 신규 셸 로직 3케이스 로컬 재현 — **단, 실제 GitHub Actions 자동 실행으로의 확인은 아직 안 됨** (검증 필요 표 참조)
  - 상세 내역: `docs/pipeline_audit.md` 7번 섹션

- [x] **AI이슈 JSON-in-string 렌더링 버그 종결 + Threads 일시적 오류 재시도** (2026-06-21) — 세션 22차 — **PR #39 머지 완료**
  - **근본 원인 확정**: `_extract_md_field()`가 `{"summary":"..."}` 패턴만 처리 → Gemini가 `{"report":"..."}` / `{"title":"...","points":[...]}` 패턴으로 반환 시 raw JSON이 HTML에 그대로 출력
  - `scripts/build_ai_issue_site.py::_extract_md_field()` — `report` 키 + `title+points` 구조 처리 추가
  - `core/ai_issue/analyzer.py::_unwrap_md_response()` — LLM 응답 파싱 시 3가지 JSON 래퍼 패턴 모두 처리 (생성 단계 방어)
  - `publish/app.html::extractMdField()` — JS 함수를 Python과 동일하게 확장 (`report`, `points` 패턴 추가)
  - `core/shared/telegram.py` — `next_week_outlook` JSON 파싱에 `summary`/`report` 폴백 추가
  - `reports/ai-issue/ai_issue_2026-06-21.json/md` — raw JSON 블록 → 정상 마크다운으로 교정
  - `publish/ai-issue/2026-06-21.html/json` + 구버전 HTML(05-31/06-07/06-14) 재빌드
  - `scripts/post_cardnews.py::_post_threads_text()` — `is_transient` 에러 시 최대 3회 재시도(10s/20s 대기) 추가
  - **중요**: `render_ai_issue_report()`는 MD 파일 전체를 markdown2로 변환한 `ctx['md_html']`을 본문으로 사용 → JSON 사이드카만 수정해도 MD 파일 자체도 반드시 교정 필요
  - **이메일 경로는 안전**: `email_ai_issue.html`은 `top10`/`weekly_tips`/`stock_snapshots`만 사용, `company_trends`/`next_week_outlook` 미사용

- [x] **구독취소 링크 에러 근본 수정** (2026-06-18) — 세션 21차
  - 이메일 구독취소(HMAC) 요청 시 DB 조회를 건너뛰고 HMAC 검증을 우선 수행하도록 로직을 분리하여 Vercel 환경에서 환경변수(`SUPABASE_SERVICE_KEY`) 누락 시 발생하는 500 에러를 원천 차단함
  - 구독관리 페이지 하단의 "전체 구독취소" 시 넘어오는 `action="manage"` 토큰도 유효한 토큰으로 수용하도록 `api/unsubscribe.py` 내 토큰 액션 검증 로직 완화
  - ISO 날짜 만료 파싱 시 파이썬 버전별 호환성을 보장하도록 `'Z'` -> `"+00:00"` 전처리 보완
  - 워크스페이스 행동 규칙(`.agents/AGENTS.md`)을 생성하여 **Git 커밋/푸시 전 문서 최신화** 규칙 강제화

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
- [x] 6/14(일) AI이슈 발행 — 이메일 배지 보라색, 텔레그램 차주전망 정상 텍스트 확인 (PR #30 머지 후)
- [x] 6/14(일) SPA AI이슈 탭 — 항상 카드 뷰만 나오는지 확인 (두개디자인 버그 수정 검증)
- [x] PR #30 → main 머지 완료
- [x] PR #31 → main 머지 완료 (주말 차단 + Threads 텍스트 + news.yml data.json)
- [x] PR #32 → main 머지 완료 (archive 두개디자인 + 6-13 오염 파일)
- [x] `stock_2026-06-13.md` 및 `publish/stock/2026-06-13.html/json` 삭제 완료 (PR #32)
- [x] PR #34 → main 머지 완료 (클로드 루틴 Step 0 요일 확인)
- [x] PR #35 → main 머지 완료 (파이프라인 모니터링 알림 TELEGRAM_CHAT_ID 폴백)
- [x] `stock_2026-06-15.md` 수동 복구 완료 (6/16 KST 08:00 stock_send.yml 발송 대상)
- [x] 6/16(화) `stock_send.yml` KST 08:00 — `stock_2026-06-15.md` 발송 확인 (완료 추정)
- [x] PR #37 → main 머지 완료 (텔레그램 미리보기 캐시 + SPA 헤더 배경 + Instagram ImportError + cardnews 에러 알림)
- [x] PR #39 → main 머지 완료 (AI이슈 JSON-in-string 종결 + Threads is_transient 재시도)
- [x] 6/21(일) AI이슈 자동 실행 — 실행됨 (단, 자동 생성 버전에 JSON 버그 잔류 → PR #39로 교정 파일 덮어씀)
- [ ] 6/19(목) 이후 `cardnews.yml` 실행 → Instagram 정상 발송 확인 (ImportError 수정 반영)
- [ ] 6/19(목) 이후 `cardnews.yml` 실패 시 텔레그램 에러 알림 수신 확인 (새 notification step)
- [ ] SPA(`/`) 탭 전환 시 헤더 전체 배경이 섹션별로 바뀌는지 실제 브라우저 확인
- [ ] 텔레그램 파이프라인 알림에서 날짜 카드 미리보기가 더 이상 고착되지 않는지 확인
- [ ] `cardnews.yml` 다음 stock 실행 — `stock_send.yml` 완료 후 트리거되는지 확인 (카드뉴스 발송 순서)
- [ ] Threads stock 캡션에 🌡 시장온도·📌 요약·🔑 키워드 포함되는지 확인
- [ ] news/ai-issue Threads 캡션에 issue_titles(제목 3개) 포함되는지 확인
- [ ] 6/28(일) 다음 AI이슈 자동 실행 — `_unwrap_md_response()` 적용으로 JSON 래퍼 버그 없이 생성되는지 확인
- [ ] 주간 주식 루틴 (`stock_build.yml`) → `data.json`에 최신 날짜 포함 확인
- [ ] `stock_send.yml` — Notion Summary `[키워드] 설명` 형식 + 시장온도 기록 확인
- [ ] `Facebook META_PAGE_ACCESS_TOKEN` 재발급 필요 (2026-06-10 PDT 만료) — Facebook Developers → Graph API Explorer
- [ ] `news.yml` 다음 자동 실행 — Vercel 배포 포함 확인 (`[skip ci]` 제거 반영)
- [ ] `ai_issue.yml` 자동 실행 시 deploy-pages 이후 이메일·텔레그램 실행 확인
- [ ] `/privacy` 페이지 Vercel 배포 확인 (vercel.json 라우팅 추가됨)
- [ ] AdSense 사이트 심사 승인 후 실제 슬롯 ID로 `data-ad-slot="AUTO"` 교체 필요
- [ ] `SUPABASE_SERVICE_KEY` Vercel 환경변수 등록 확인 → `/api/unsubscribe` 401 에러 해결
- [ ] Vercel 배포 후 `/subscribe` 페이지 접속 + 구독 버튼 노출 확인
- [ ] 구독 신청 → 확인 이메일 수신 → confirm 링크 클릭 → Supabase status=active 확인
- [ ] `cardnews.yml` 수동 실행 → Instagram/Threads(텍스트)/Facebook/Telegram 정상 발송 확인
- [ ] `NOTION_DATABASE_ID_STOCK` / `NOTION_DATABASE_ID_AI_ISSUE` 실제 값으로 교체 필요
- [ ] `news.yml` 다음 자동 실행 → `publish/stock/data.json` Vercel 반영 확인 (PR #31 수정)
- [ ] `weekly_build.yml` 다음 실행 → 텔레그램 "주간 주식시황 빌드 완료" 메시지에 기간·총평·지수 포함 확인
- [ ] `news.yml` 다음 자동 실행 — `분석 결과 확인`(`check_analysis`) 스텝이 `ok=true/false`를 의도대로 출력하는지 Actions 로그 확인 (세션 19차, 정적 검증만 완료·실행 미확인)
- [ ] `news.yml`/`stock_build.yml`/`weekly_build.yml` 다음 실행 — 단독 라인 분리한 git add가 실제 커밋에 `app.html`/`index.html`/`archive.html` 모두 포함되는지 확인 (세션 19차)
- [ ] 분석 실패 재현 시 `core/shared/alert.py::send_pipeline_alert()`가 텔레그램+이메일 둘 다 정상 발송하는지 확인 (세션 19차, 로컬 import만 확인했고 실제 발송 테스트 안 함)
- [ ] 주식 백업 경로(`run_stock.py` 직접 이메일 발송 분기) 다음 실행 시 `channel="stock"` 수정분이 실제로 stock 구독자에게만 가는지 확인 (세션 19차)
### 다음 개발 (우선순위 순)
- [ ] **테마 chip 그룹 분리** — `build_site.py` 테마 패널에서 `skins/` (색상 변형: classic/ink/forest)와 `layouts/` (레이아웃 변형: editorial/minimal/terminal)를 헤더로 구분
- [ ] **editorial 페이지 테마 버튼 추가** — `editorial.py::_layout()`에 `id="themeBtn"` 추가 (현재 editorial 서브페이지에서 테마 버튼이 사라짐)
- [ ] **구독 알림 이메일 템플릿 개선** — 인라인 HTML → `templates/email_confirm.html` 분리
- [ ] **SNS 카드뉴스 실제 테스트** — Instagram/Threads/Facebook/Telegram 채널별 발송 검증
- [ ] **Twitter/X 카드뉴스** — Basic 티어 결제 후 활성화
- [ ] **레거시 GitHub Secrets 정리** — `RECIPIENT_EMAIL`(단수), `RESEND_API_KEY` 삭제 권장

### 주요 아키텍처 메모
- `publish/archive.html`은 **`themes/editorial.py::render_archive()`** 에서 직접 생성 (Jinja2 미사용)
- **archive → SPA 탭 이동**: `archive.html`의 ai-issue/stock 탭은 `index.html#ai-issue`, `index.html#stock`으로 링크. SPA 초기화 시 `location.hash` 감지 → 해당 탭 활성화 → `history.replaceState`로 hash 제거. `editorial.py::_layout(nav_hrefs=...)` 파라미터로 탭별 href 재정의
- **SPA ↔ editorial 서브페이지 독립 설계 주의**: archive에서 탭 이동 시 SPA로 돌아오도록 설계. editorial sub-page에서는 SPA JS가 없으므로 탭 href가 직접 이동경로가 됨
- `templates/web_archive.html`은 editorial 외 테마(classic/ink 등)용
- `publish/search-index.json`: `build_site.py` 빌드 시 자동 갱신 (뉴스 전체 + AI이슈 + 주식)
- 서브페이지 nav는 `nav.js` 런타임 주입 — 탭 변경 시 `nav.js`만 수정하면 전체 반영
- 카드뉴스 `data.json`: 채널별 서브디렉터리에 위치 (`publish/cardnews/{type}/data.json`)
- 카드뉴스 GitHub raw URL: `https://raw.githubusercontent.com/chamgil71/dailynews/main/publish/cardnews/{type}/{date}-{n}.png`
- **주식 품질 게이트**: `run_stock.py`의 `_is_analysis_complete()` — summary + temperature_reason 둘 다 있어야 통과
- **백업 분析 판단**: `stock_build.yml` check_md — MD의 `## ■ 핵심 요약` 섹션 내용 파싱 (stock-data.json 미사용)
- **stock_build.yml check_md TODAY**: `TZ=Asia/Seoul date +%Y-%m-%d` 사용 → KST 기준 날짜. push 트리거 시 KST 익일이면 TODAY != push된 파일 날짜. 단, 백업 스텝은 `schedule/workflow_dispatch`에서만 실행되므로 push 이벤트에서 오발동 없음
- **GitHub Actions 스케줄 지연**: `cron: '0 14 * * 1-5'` (UTC 14:00)가 최대 4시간 이상 지연 실행될 수 있음 (GitHub 트래픽 영향). 백업 의존 시 실제 실행 시각이 크게 달라질 수 있음
- **클로드 루틴 날짜→요일 계산**: Claude AI 모델이 날짜→요일 변환을 내부 추론으로 오판 가능 (2026-06-15 월요일 → "일요일" 사례). `stock_routine_v6.md` Step 0에서 `python3 datetime.date.today().weekday()` Bash 명령으로 강제 확인
- **파이프라인 모니터링 알림 채널**: `notify_pipeline.py` — `TELEGRAM_CHAT_ID_MONITOR`(등록됨) → 전용 모니터 채널 우선, 폴백 `TELEGRAM_CHAT_ID`. 클로드 루틴 조기 종료는 GitHub Actions 외부이므로 어떤 채널로도 자동 알림 불가
- **Vercel vs GitHub Pages 배포 차이**: GitHub Pages는 `publish/` 전체 업로드, Vercel은 `news.yml` git add 목록만 배포 → `search-index.json`, `news/data.json` 반드시 git add에 포함 필요
- **Gemini 비정형 응답 (3가지 패턴)**: markdown 요청에 JSON 래퍼로 반환하는 경우 있음. 처리 함수: `_extract_md_field()`(Python 빌드), `extractMdField()`(SPA JS), `_unwrap_md_response()`(생성 단계), `telegram.py` next_week_outlook 파싱
  - 패턴1: `{"summary":"..."}` — `summary` 키 추출
  - 패턴2: `{"report":"..."}` — `report` 키 추출 (company_trends에서 발생)
  - 패턴3: `{"title":"...","points":[{"point":"...","commentary":"..."},...]}` — title+points 구조 변환 (next_week_outlook에서 발생)
- **AI이슈 HTML 빌드 구조**: `render_ai_issue_report()`는 MD 파일 전체를 `markdown2`로 변환한 `ctx['md_html']`을 본문으로 사용. `structured` dict(JSON 사이드카)는 top10 카드에만 사용. → MD 파일 자체에 JSON 블록이 있으면 HTML에도 raw JSON 출력됨. 사이드카만 고치는 것으로는 부족
- **카드뉴스 구조**: `templates/cardnews_card.css` (CSS, CSS var() 사용) + `config/cardnews_themes.json` (채널별 accent/topbar/label/hashtags) → `build_cardnews.py`가 로드하여 `_render_css()`로 `:root { --accent: ...; }` 주입
- **카드뉴스 텔레그램 발송**: `post_cardnews.py::post_telegram()` — PNG `sendMediaGroup` + 인라인 버튼 `sendMessage` 후속 전송
- **빌드 스크립트 인터페이스**: `build_site.build()` / `build_stock_site.build()` / `build_ai_issue_site.build()` 모두 `build()` 함수 통일 → `build_all.py` 오케스트레이터에서 동일 방식 호출
- **`templates/*.html` CSS 린터 오류**: Jinja2 `{{ }}` 변수를 VS Code CSS 파서가 오인한 것, 런타임 정상 동작 — 무시 가능
- **Supabase 구독 시스템**: `api/_supabase.py` + service_role 키로 서버에서만 접근. RLS 활성화, anon 키 차단. 구독자 채널별 선택: `channels JSONB {"news","stock","ai_issue"}`. 관리자: `is_admin=true`
- **관리자 vs 구독자**: is_admin=true → `send_admin_alert()` 시스템 알림 수신. 일반 구독자 → 채널별 브리핑만 수신. RECIPIENT_EMAILS는 Supabase 조회 실패 시 폴백
- **헤더 CSS 통일**: `templates/web_*.html` 4개 모두 `.hnav-tab` + `flex:1` + `3px border` 구조로 통일. `index.html`(editorial SPA)이 기준
- **`CLAUDE.md` 위치**: 프로젝트 루트가 표준 위치. Claude Code가 세션 시작 시 자동 로드하는 프로젝트 컨텍스트 파일. `.claude/`(디렉터리)와 다름 — `.gitignore`의 `.claude/`는 디렉터리만 차단
- **SNS 카드뉴스 5개 플랫폼**: Instagram(카루셀), Threads(텍스트/카루셀 설정), Facebook(멀티사진), Telegram(미디어그룹+버튼), Twitter(이미지스레드) — `post_cardnews.py::PLATFORM_HANDLERS`
- **Threads 발송 모드**: `config/cardnews_themes.json channels[].threads_mode` — `"text"`(기본, TEXT media_type) / `"carousel"`(이미지 카루셀). Instagram은 텍스트 단독 포스트 불가. `_get_threads_mode(channel)`로 로드
- **SNS Telegram 채널 분기**: `post_cardnews.py::post_telegram()` — channel='stock'→`TELEGRAM_CHAT_ID_STOCK`, 그 외→`TELEGRAM_CHAT_ID`
- **docs/ 파일명 규칙**: `{channel}_{type}.md` 또는 `{topic}_{type}.md` (underscore, 소문자). 구버전→`docs/backup/`, 계획→`docs/plan/`
- **scripts 가이드**: `docs/scripts_guide.md` — 21개 스크립트 역할·워크플로우 매핑 문서
- **뉴스 렌더링 경로 분기**: `editorial` 테마 → `editorial.py::render_report()` 직접 생성(Jinja2 미사용). `classic/ink/forest` 테마 → `base.py::render_report()` + `templates/web_news.html`. 주식은 테마 불문 `base.py::render_stock_report()` + `web_stock.html`
- **Design System 패치 파일 위치**: `storage/MS News Design System260611/` — P0~P4 원본 명세 보존
- **`a.tag` 터치 타깃**: `::after { inset: -12px -2px }` pseudo-element로 시각 크기 유지하면서 44px tap area 확보. `web_news.html`의 `.tag-row` 링크 태그에만 적용
- **구독 버튼 적용 범위**: editorial 페이지(뉴스·AI이슈·아카이브) → `editorial.py::_layout()` masthead nav / classic-계열(주식 등) → `header.html` `.btn-subscribe` (`.header-actions` 내)
- **`SUBSCRIBE_URL` 자동 연동**: `config/theme_config.py`에서 `SITE_BASE_URL + "/subscribe"` 조합. GitHub Secret `SUBSCRIBE_URL` 별도 설정 불필요
- **구독취소 이메일 링크**: `mailer.py::_make_token(email)`로 HMAC 토큰 생성 → `/api/unsubscribe?email=...&token=...` 형식. 뉴스·주식 이메일 푸터 우하단에 표시
- **`clauderoutine_v5` 핵심 키워드**: `v4`의 `키워드: 설명 1~2문장` 형식이 v5 업데이트 시 `#해시태그` 단순 나열로 축약됨 → 복원 완료
- **Notion 주식 Summary 파싱**: `## 3. 핵심 키워드 TOP 5` 섹션에서 파싱. `① 키워드: 설명` → `[키워드] 설명` / `#태그` → `[태그]` 양방향 처리 (`sync_notion.py::_parse_stock_md()`)
- **Notion 주식 시장온도**: `## 시장 온도계: 🟠 상승` 패턴 파싱 → `notion.py::sync_stock_to_notion(temperature=...)` 전달. Notion DB `시장온도` 컬럼 select/rich_text 자동 분기
- **Notion 주식 제목**: `📊 주식 시황 브리핑 — YYYY-MM-DD` 형식 (`notion.py` 262행). 과거 v4 레코드들은 Claude MCP 직접 기록으로 형식 불일치 — 신규 레코드부터 통일
- **Notion 기록 주체**: `stock_send.yml`이 매일 KST 08:00 `sync_notion.py --type stock` 실행. 루틴 성공/실패 무관. Claude 루틴(v5)은 Notion 직접 쓰기 없음 (v4는 MCP 직접, v5에서 GitHub Actions 이관)
- **AdSense (dailynews)**: `publish/app.html` — 사이드바 `.ad-card` (228×200)만 유지. 메인 상단 배너는 제거. `build_site.py`가 `app.html` → `index.html` 빌드 시 SUBSCRIBE_URL_PLACEHOLDER 치환
- **AdSense 슬롯 ID**: 현재 `data-ad-slot="AUTO"` 플레이스홀더. 심사 승인 후 실제 슬롯 ID로 교체 필요
- **`/api/unsubscribe` 401 원인**: GitHub Secrets ≠ Vercel 환경변수 (별도 시스템). `SUPABASE_SERVICE_KEY`를 Vercel 대시보드 → Project Settings → Environment Variables에 등록해야 함
- **`[skip ci]` 주의**: Vercel Git Integration도 `[skip ci]` 커밋 메시지를 인식해 배포 스킵. news/ai_issue/cardnews/stock_build 워크플로우 모두 제거 완료
- **`stock/data.json` 미업데이트 버그**: `stock_build.yml` git add에서 다중 파일 `\` 연속 + `2>/dev/null || true` 조합이 data.json staging을 누락시킴. edeed23 이후 모든 자동 빌드에서 발생. PR #27은 `data.json`/`index.html`/`archive.html` 부분만 단독 라인 분리 — `app.html`+`index.html`+`archive.html`(루트 SPA 파일) 결합 라인은 그대로 남아있었고, 세션 19차(2026-06-16)에서 `news.yml`/`stock_build.yml`/`weekly_build.yml` 3곳 모두 마무리 분리함. **교훈**: "PR #N에서 수정 완료"라는 기록도 범위를 정확히 확인할 것 — 부분 수정이 전체 수정으로 기록된 사례
- **`_parse_keywords()` v6 포맷**: `① 제목: 설명 (볼드 없음, 한 줄)` → `build_stock_site.py`에서 최우선 처리. v5(`#해시태그`), 구 포맷(`**①**`) 순으로 폴백
- **모바일 nav 이모지**: `header.html` + `nav.js` 이모지(📰🤖📈📚) + `_COMMON_CSS` `.tab-label { display: none }` at ≤600px → 모바일에서 이모지만 표시
- **Facebook `META_PAGE_ACCESS_TOKEN`**: 60일 만료. 만료 시 Developers 콘솔 → Graph API Explorer → Page Access Token 재생성 → long-lived token 교환 → GitHub Secret 업데이트
- **SPA 탭 href 설계**: `publish/index.html`의 비-archive 탭은 `href="#"` — 모바일 탭 경합(JS 핸들러 부착 전 빠른 탭) 시 editorial 서브페이지로 이탈 방지. archive 탭만 `href="archive.html"` (의도적 페이지 이동). `build_site.py` NAV_INJECT 단계에서 자동 치환
- **SPA ↔ editorial 서브페이지 독립 설계**: SPA(`publish/index.html`)는 JSON fetch → JS 렌더. editorial 서브페이지(`publish/ai-issue/*.html`, `publish/stock/*.html`, `publish/news/*.html`)는 Python 빌드 시 정적 HTML. 두 시스템은 URL 계층으로 구분 (루트=SPA, 서브디렉터리=editorial). 탭 공유하지만 서로 다른 코드베이스
- **이메일 MIME 구조 필수 규칙**: `multipart/alternative`에서 반드시 `text/plain` 먼저, `text/html` 나중 첨부 (RFC 2046: 클라이언트는 마지막 파트 선택). `_html_to_plain(html)` 함수로 HTML → 가독 텍스트 변환 (`mailer.py`)
- **이메일 CSS 인라인 필수 규칙**: Gmail/모바일 클라이언트는 `<style>` 블록 스트리핑. 배지 배경색(`background-color:#7c3aed`)·헤더 그라데이션 등 시각적으로 중요한 CSS는 반드시 `style=""` 인라인으로 지정. 클래스 기반 CSS는 보조 수단만
- **`SECTION_DEFAULTS["ai-issue"]` 누락 버그**: `build_site.py` line 486 이전엔 news/stock만 포함 → `state.aiIssueTheme = undefined` → `data-theme="undefined"` 설정됨. `"ai-issue": news_theme` 추가로 수정
- **Gemini `next_week_outlook` JSON 패턴**: LLM이 `{"points":[{"point":"..."},...],"summary":"..."}` 형태의 JSON string으로 반환하는 경우 있음 → `telegram.py::send_ai_issue_telegram()`에서 파싱하여 `points[].point` 앞 3개 추출. `extractMdField()` (SPA JS)도 동일 패턴 처리
- **AI이슈 git add 순서**: `ai_issue.yml`에서 날짜별 `.html`/`.json` 먼저 add → `index.html`, `archive.html`, `data.json` 각 단독 라인으로 add. 다중파일 `2>/dev/null || true` 패턴 금지 (뒤 파일 누락 위험)
- **`news.yml` stock git add**: `publish/stock/data.json` + `index.html` + `archive.html` + `stock-data.json` 모두 파일별 단독 라인 (PR #31에서 data.json 누락 수정 + 다중파일 패턴 분리)
- **카드뉴스 keyword 색상 강조**: `config/cardnews_themes.json channels[].keyword` 필드 + `build_cardnews.py::_render_label()` — 레이블의 keyword 부분만 `<span style="color:{accent}">` 감쌈
- **주간 주식 파이프라인 알림**: `weekly_build.yml` → `notify_pipeline.py --type weekly-stock` → `weekly_{date}.md` 파싱 후 기간·주간총평·지수성과·핫테마 텔레그램 발송
- **텔레그램 링크 미리보기 캐시**: 같은 URL을 매일 보내면 텔레그램이 처음 fetch한 OG 미리보기(구 날짜)를 영구 캐시 → `disable_web_page_preview: true` 필수. `notify_pipeline.py::_send()`에 적용 완료
- **SPA 헤더 섹션별 배경**: `publish/app.html`의 `<header data-section="news">` + `switchSection()`에서 `setAttribute("data-section", section)` → CSS `header[data-section="*"]` 규칙으로 섹션별 gradient. `switchSection()`의 tab 셀렉터는 `.hnav-tab[data-section=...]`으로 스코핑 필수 (header 자체와 충돌 방지)
- **`post_cardnews.py` Instagram 카루셀**: `_ig_post()` / `_ig_get()` / `_ig_wait_container()` 헬퍼로 직접 구현. PR #33에서 `post_instagram.py` 삭제 후 dead import 잔류로 `ImportError` 발생 — 인라인으로 대체
- **`cardnews.yml` SNS 실패 알림**: SNS발송 스텝에 `id: sns`, 후속 스텝 `if: always() && steps.sns.outcome == 'failure'`로 텔레그램 알림. `continue-on-error: true`와 `steps.*.outcome` vs `steps.*.conclusion` 차이 주의 — `outcome`이 실제 결과, `conclusion`은 continue-on-error 반영 후 값
- **`notify_pipeline.py` cardnews 타입**: `--type cardnews` 지원. `_msg_failure()` 레이블 `"카드뉴스 SNS"`, `_msg_cardnews_success()` 추가
- **`core/shared/alert.py`**: 3채널 공통 실패 알림 모듈. `send_pipeline_alert(channel, date_str, reason)` — 텔레그램+관리자 이메일(`mailer.send_admin_alert()` 재사용) best-effort 발송
- **`core/shared/report_date.py`**: KST 날짜 계산 공통 모듈. `kst_today()`/`kst_now()` — 타임존을 코드에 명시. `mailer.py`/`telegram.py`/`run_*.py`/`send_*.py` 전체 사용
- **카드뉴스 `data.json` extra 필드**: `_update_index(extra_data=)` 파라미터로 채널별 추가 데이터 저장. news/ai-issue: `issue_titles`(top3), stock: `summary`/`keywords`/`temperature`. `post_cardnews.py::_build_caption()`에서 채널 분기로 활용
- **카드뉴스 발송 순서 (stock)**: `stock_build.yml`(밤 빌드) → `stock_send.yml`(08:00 텍스트) → `cardnews.yml` 트리거(카드뉴스 이미지). `cardnews.yml` 트리거가 `"Stock Briefing Send"`임에 주의 — `"Stock Briefing Build"`가 아님
- **Instagram 카루셀 타이밍 에러(2207027)**: FINISHED 후에도 카루셀 생성 즉시 시도 시 "Media ID not available" 에러 발생. `_ig_wait_container()` 완료 후 5초 추가 대기 + 10초 간격 3회 재시도로 대응 (`post_cardnews.py`)

---

## 반복 에러 디버그 지침 (세션마다 참조)

> 같은 증상이 반복될 때 **이 섹션을 먼저 확인**한다. 원인 없이 코드 수정 금지.

### 패턴 1: "두 가지 디자인이 번갈아 보인다" (SPA ↔ 서브페이지 혼재)
- **원인**: 사용자가 SPA(`/`)와 editorial 서브페이지(`/ai-issue/`, `/stock/`)를 교차 탐색 중
- **진단**: 증상 발생 URL 먼저 확인 (Chrome 주소창 탭 → 전체 URL 표시). `/`이면 SPA, `/ai-issue/`이면 editorial
- **체크**: SPA의 비-archive 탭 `href`가 `#`인지 확인 (`index.html` 677-680행)
- **체크**: `build_site.py` NAV_INJECT 섹션에 `href="ai-issue/"` → `href="#"` 치환 로직 있는지 확인

### 패턴 2: "이메일이 다른 클라이언트에서 텍스트만 보인다"
- **원인A**: `multipart/alternative`에서 `text/html`이 없거나 순서가 `html` 먼저 → 일부 클라이언트가 `text/plain` 선택
- **원인B**: `text/plain` 파트 자체가 없어 오류 클라이언트가 raw HTML 표시
- **진단**: `mailer.py`의 `send_email()` / `_send_batch()` 에서 `MIMEText("plain")` 먼저, `MIMEText("html")` 나중 순서 확인
- **수정**: `_html_to_plain(html_body)` 결과를 `text/plain`으로 먼저 attach

### 패턴 3: "이메일 배지/헤더 색이 다르다" (CSS 미적용)
- **원인**: Gmail/모바일이 `<style>` 블록 스트리핑 → 클래스 기반 CSS 무효화
- **진단**: 해당 요소에 `class=` 만 있고 `style=""` 인라인이 없는지 확인
- **수정**: 배경색·텍스트색·패딩 등 시각적 핵심 속성은 반드시 인라인 `style` 직접 지정
- **참조**: `templates/email_ai_issue.html` 배지 (`style="...background-color:#7c3aed..."`)가 정상 패턴

### 패턴 4: "텔레그램/SPA에 JSON이 그대로 출력된다"
- **원인**: Gemini LLM이 마크다운 텍스트 대신 JSON string 반환 (`{"summary":"..."}` 또는 `{"points":[...]}`)
- **진단**: `reports/ai-issue/ai_issue_YYYY-MM-DD.json`의 `next_week_outlook`, `company_trends` 필드 값 확인
- **수정**: `telegram.py::send_ai_issue_telegram()` — JSON 감지 후 `points[].point` 또는 `summary` 추출
- **수정**: SPA `extractMdField()` — `trimmed.startsWith('{')` 패턴으로 JSON → `summary` 추출
- **예방**: `core/ai_issue/analyzer.py`에서 LLM 응답 파싱 시 JSON/markdown 양방향 처리

### 패턴 5: "Vercel에 최신 데이터가 반영이 안 된다"
- **원인A**: 워크플로우 `git add`에서 핵심 파일 누락 (다중파일 `|| true` 패턴이 에러 숨김)
- **원인B**: 커밋 메시지에 `[skip ci]` → Vercel Git Integration도 스킵
- **원인C**: GitHub Pages와 Vercel은 **별도 배포** — Pages는 `publish/` 전체, Vercel은 git add 목록만
- **진단**: 해당 워크플로우의 `git add` 목록에 `data.json`, `index.html`, `archive.html` 각각 단독 라인으로 있는지 확인
- **진단**: 최근 커밋 메시지에 `[skip ci]` 없는지 확인 (`git log --oneline -5`)
- **수정 패턴**: `git add -f publish/ai-issue/index.html 2>/dev/null || true` 금지 → `git add -f publish/ai-issue/index.html` 단독 라인

### 패턴 6: "AI이슈 분석 실패인데 텔레그램 알림이 없다"
- **원인**: `run_ai_issue.py`의 에러 핸들링에 `_telegram_alert()` 호출 누락
- **진단**: `run_ai_issue.py`에서 `sys.exit(1)` 모든 경로에 `_telegram_alert(msg)` 있는지 확인
- **진단**: 환경변수 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` GitHub Secrets 등록 확인 (MONITOR용은 `TELEGRAM_CHAT_ID_MONITOR`)
- **체크**: `send_telegram.py`의 `_send_ai_issue()`에 `top10` 공란 가드 있는지 확인

### 패턴 7: "git add 뒤 data.json이 커밋에 포함 안 된다"
- **원인**: 아래 패턴은 앞 파일 에러 시 뒤 파일 누락 + 에러 숨김
  ```bash
  git add -f publish/ai-issue/index.html publish/ai-issue/data.json 2>/dev/null || true  # 위험
  ```
- **수정 패턴**:
  ```bash
  git add -f publish/ai-issue/index.html   2>/dev/null || true
  git add -f publish/ai-issue/data.json    2>/dev/null || true
  git add -f publish/ai-issue/archive.html 2>/dev/null || true
  ```
- **규칙**: `2>/dev/null || true`를 사용할 경우 반드시 **파일 1개당 1줄** 원칙

### 패턴 8: "에러/성공인데 모니터링 텔레그램 알림이 한 번도 안 온다"
- **원인A (가장 흔함)**: `notify_pipeline.py`의 chat_id 폴백 = `TELEGRAM_CHAT_ID_MONITOR or TELEGRAM_CHAT_ID`. 그런데 워크플로우 env 블록이 `TELEGRAM_CHAT_ID_MONITOR`만 전달하고 폴백용 `TELEGRAM_CHAT_ID`는 전달 안 함 → MONITOR Secret 미등록 시 chat_id 빈 값 → `sys.exit(0)` 조용히 종료 (성공·실패 모두 알림 안 감)
- **진단**: 4개 워크플로우(news/stock_build/ai_issue/weekly_build) notify 스텝 env에 `TELEGRAM_CHAT_ID`가 폴백으로 있는지 확인. `notify_pipeline.py`는 "미설정 — 알림 건너뜀"을 stderr로만 출력하고 exit 0 → Actions 로그에서도 눈에 안 띔
- **원인B**: 클로드 루틴 자체 실패는 **GitHub Actions가 아님** (Claude Code 웹 세션). `notify_pipeline.py`는 워크플로우 안에서만 호출되므로 루틴의 조기 종료/오판은 어떤 알림도 못 보냄. 루틴은 에러를 던지지 않고 `return`으로 정상 종료하므로 알릴 "에러"조차 없음
- **수정**: 4개 워크플로우 notify env에 `TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}` 추가 (PR — 세션 18차). MONITOR 등록 시 그게 우선, 미등록 시 기본 채널로 발송
- **주의**: `TELEGRAM_CHAT_ID_MONITOR` Secret 등록됨 (사용자 확인). GitHub Actions 실패는 해당 채널로 정상 발송. 클로드 루틴 조기 종료는 GitHub Actions가 아니므로 어떤 채널로도 알림 불가.

### 패턴 9: "CLAUDE.md/문서에 '수정 완료'라고 적혀 있는데 실제로 또 같은 버그가 난다"
- **원인**: 메모리(CLAUDE.md)의 "수정 완료" 기록은 **그 기록이 작성된 시점·범위에서만** 사실이다. 이후 코드가 되돌려졌거나, 여러 파일 중 일부에만 수정이 적용되고 나머지는 누락된 채로 "완료"라고 통째로 적힌 경우가 실제로 있었다 (세션 19차에서 발견: "PR #27에서 git add 단독 라인 분리 완료"로 기록됐지만 실제로는 `ai_issue.yml`만 고쳐지고 `news.yml`/`stock_build.yml`/`weekly_build.yml`은 그대로였음)
- **진단**: 반복되는 버그를 마주쳤을 때 CLAUDE.md의 "수정 완료" 기록을 보고 "이미 고쳐졌으니 다른 원인일 것"이라 단정하지 말 것. **반드시 해당 파일을 직접 grep/Read해서 실제 코드 상태를 확인**한 뒤 판단할 것
- **수정 원칙**: 여러 파일에 걸친 수정을 기록할 때는 "어느 파일까지 적용했는지"를 명시적으로 적는다 (예: "news.yml만 수정, stock_build.yml은 동일 패턴 남아있음 — TODO"). "전체 적용 완료"라고 적기 전에 영향받는 파일 전체를 grep으로 재확인한다
- **참조**: `docs/pipeline_audit.md` 7-1절에 이번 사례 상세 기록

### 패턴 10: "구독취소 링크 클릭 시 500/400 에러 발생"
- **원인A (500 에러)**: Vercel 환경변수 `SUPABASE_SERVICE_KEY` 누락 상태에서 이메일 HMAC 토큰 검증보다 DB 조회가 먼저 실행되어 예외 발생
- **원인B (400 에러)**: 웹페이지 하단의 "전체 구독취소" 링크 클릭 시 `manage` 액션 토큰이 전달되나, `unsubscribe.py`는 `unsubscribe` 액션 토큰만 검증하여 차단
- **진단**: `api/unsubscribe.py`에서 파라미터가 16자리 HMAC 토큰인지, 32자리 DB 토큰인지 구분하여 정상 라우팅되는지 확인
- **수정**: HMAC 토큰은 DB를 조회하지 않고 즉시 검증 처리. DB 토큰 조회 시 `action` 완화 검증

### 패턴 11: "AI이슈 HTML에 특정 섹션만 JSON이 그대로 출력된다"
- **원인**: Gemini LLM이 `company_trends` / `next_week_outlook` 등 마크다운 요청 필드를 JSON 래퍼(`{"report":"..."}`, `{"title":"...","points":[...]}`)로 반환 → `_extract_md_field()`가 해당 패턴 미처리 시 raw JSON이 HTML 본문에 출력
- **진단 1**: `reports/ai-issue/ai_issue_YYYY-MM-DD.json`에서 해당 필드 값이 `{` 로 시작하는지 확인. 패턴 3가지 모두 확인 (summary/report/points)
- **진단 2**: MD 파일(`reports/ai-issue/ai_issue_YYYY-MM-DD.md`)에도 JSON 블록이 있는지 확인. `render_ai_issue_report()`는 MD 전체를 본문으로 사용하므로 **MD 파일 자체도 반드시 교정**
- **진단 3**: `publish/ai-issue/YYYY-MM-DD.json`의 normalized 버전도 확인 (build 결과물)
- **수정**: `_extract_md_field()`(Python), `extractMdField()`(JS), `_unwrap_md_response()`(생성 단계)가 모두 3가지 패턴을 처리하도록 확인. MD 파일도 정상 마크다운으로 재작성 후 `build_ai_issue_site.py`로 HTML 재빌드
- **이메일 경로는 안전**: `email_ai_issue.html`은 `top10`/`weekly_tips`/`stock_snapshots`만 사용 — `company_trends`/`next_week_outlook` 미사용

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
| `TELEGRAM_CHAT_ID_STOCK` | @msstockbrief 채널 ID | ✅ |
| `NOTION_API_KEY` | Notion 동기화 | ✅ |
| `NOTION_DATABASE_ID_NEWS` | Notion 뉴스 DB | ✅ |
| `NOTION_DATABASE_ID_STOCK` | Notion 주식 DB | ✅ |
| `NOTION_DATABASE_ID_AI_ISSUE` | Notion AI이슈 DB | ✅ |
| `NAVER_CLIENT_ID` / `NAVER_CLIENT_SECRET` | 주식 국내뉴스 수집 | ✅ |
| `GH_CONTENTS_TOKEN` | GitHub Contents API (레거시) | ✅ |
| `INSTAGRAM_ACCESS_TOKEN` | Meta Graph API (60일 만료 주의) | ✅ |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business ID | ✅ |
| `FACEBOOK_PAGE_ID` | Facebook Page ID (Ainews) | ✅ |
| `META_PAGE_ACCESS_TOKEN` | Facebook Page Access Token | ✅ |
| `THREADS_USER_ID` | Threads 사용자 ID | ✅ |
| `THREADS_ACCESS_TOKEN` | Threads API 토큰 | ✅ |
| `TWITTER_API_KEY` / `TWITTER_API_SECRET` | Twitter Developer App | ❌ 미발급 |
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
