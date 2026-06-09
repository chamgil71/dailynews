# 📋 Work Log — DailyNews

개발 이력 및 주요 변경사항 기록.

---


## 2026-06-09 (5차 — 데이터구조·테마 일관성 통일 & 검색 폴백)

### 주제: 3채널 데이터 소스 및 아카이브 테마 일관성 통일 + 검색 링크 폴백 처리 + 마이그레이션 검증

#### 배경
- 뉴스, 주식, AI이슈 등 카테고리별 데이터 소스(JSON 위치, 구조)의 파편화로 인해 관리 및 렌더링에 일관성 부족.
- Vercel 라이브 사이트 배포 시 `index.html`과 각 서브페이지(주식 `stock/*.html`, AI이슈 등)의 상단바(Navigation) 및 레이아웃 디자인이 테마에 따라 파편화됨.
- 검색 결과 클릭 시 뉴스만 원본 기사로 링크되고, 주식/AI이슈는 `h.art.link`가 없어 클릭이 되지 않고 화면이 멈추는 버그 발생.
- 기존 테마(Editorial)만 3채널 탭과 통합 검색이 구현되어 있었고, 다른 테마들(Classic, Minimal, Terminal)은 미구현 상태였음.

---

### 변경 내용

#### 1. 검색 기능 링크 폴백 구현 (`publish/app.html`, `themes/editorial.py`)
- SPA(`publish/app.html`) 및 Editorial 테마의 검색 결과 렌더링 로직 수정.
- `h.art.link`가 없을 경우 해당 일자의 데일리 리포트 URL인 `h.report_url`로 폴백(fallback)되도록 수정하여 주식 및 AI이슈 검색 결과도 클릭 시 상세 리포트로 안전하게 이동하도록 개선.

#### 2. 테마별 아카이브 페이지(`archive.html`) 디자인 및 기능 일관성 확보
- 기존에 Editorial 테마에만 적용되어 있던 3채널(뉴스, 주식, AI이슈) 탭 전환 및 통합 검색(Search Engine) 기능을 모든 테마로 확장 적용.
- **공통 템플릿(Classic, Forest, Ink)**: `templates/web_archive.html`을 수정하여, 상단 검색 바, 카테고리 체크박스 필터, 3채널 탭 메뉴(뉴스/주식/AI이슈), 탭 전환 JS 스크립트를 추가.
- **커스텀 테마(Minimal, Terminal)**: `themes/minimal.py` 및 `themes/terminal.py`의 `render_archive` 메소드에 해당 테마 고유의 미학적 스타일(Minimal의 미니멀리즘, Terminal의 모노크롬 CLI 느낌)을 유지하면서 3채널 탭과 검색 기능 코드를 이식.
- Python f-string 내의 자바스크립트 중괄호가 템플릿 컴파일 오류를 내지 않도록 모두 이중 중괄호(`{{` 및 `}}`)로 이스케이프 처리 완료.

#### 3. 데이터소스 및 빌드 일관성 통일
- 뉴스, 주식, AI이슈의 데이터소스 위치와 JSON 구조의 정합성을 확인하고, 빌드 파이프라인에서 일관되게 `reports-data.json` 등을 처리하도록 지원.
- `render_archive` 시 주식 리스트(`stock_items`)와 AI이슈 리스트(`ai_items`)를 Jinja2 컨텍스트에 주입하도록 `themes/base.py` 수정.

#### 4. 마이그레이션 완결성 검증
- `python scripts/build_all.py --all`을 통해 과거 108개 분량의 전체 리포트 HTML을 새 템플릿 및 일관성 기반으로 완벽하게 컴파일 재생성.
- `scratch/verify_migration.py` 실행을 통해 이전 발행된 데이터와의 정합성 및 무결성을 100% 검증 완료.

---

### 영향받은 파일
| 파일 | 변경 |
|------|------|
| `themes/base.py` | `render_archive()` 컨텍스트에 `stock_items`, `ai_items` 리스트 추가 |
| `themes/editorial.py` | `render_archive()` 내 검색 결과 렌더링에 `h.report_url` 폴백 추가 및 디자인 마크업 개선 |
| `themes/minimal.py` | `render_archive()`에 미니멀 스타일의 3채널 탭, 통합 검색창 및 JS 로직 추가 |
| `themes/terminal.py` | `render_archive()`에 터미널 다크 스타일의 3채널 탭, 통합 검색창 및 JS 로직 추가 |
| `templates/web_archive.html` | 공통 테마용 아카이브 페이지에 검색 바, 체크박스 필터, 3채널 탭 및 JS 스크립트 이식 |
| `publish/app.html` | SPA 검색 결과 렌더링 로직 수정 (출처 링크가 없을 때 상세 보고서로 폴백) |
| `docs/plan/plan_theme_design_unification.md` | [NEW] 디자인/테마 통합 구현 계획서 및 검증 보고서 작성 |

---

## 2026-06-04 (4차 — UI 통합·검색 고도화·nav 모듈화)

### 주제: 사이트 디자인 통합 + 통합 검색 (뉴스·AI이슈·주식) + nav.js 모듈화

#### 배경
- SPA(`index.html`)와 서브페이지(stock/ai-issue) 헤더 구조 불일치
- 로고명 "AI News Daily" / "AI News Brief" 혼재
- `archive.html` 마스트헤드 유지하면서 검색 기능 추가 필요
- SPA 검색이 현재 날짜 1건만 필터, 전체 기간 통합 검색 부재
- 아카이브 탭이 SPA 내부 섹션 스위처로 연결 (독립 페이지로 분리 필요)

---

### 변경 내용

#### 1. 로고·홈링크 통일 (`config/theme_config.py`, `themes/base.py`, `themes/editorial.py`)
- `SITE_LOGO_HTML` 변수 신설 — `SITE_TITLE`에서 자동 생성 (`📰 AI <span class="accent">News</span> Brief`)
- 모든 서브페이지 로고 "AI News Daily" → "AI News Brief" 통일
- 홈 링크 `location.href='/'` → `'../'` (GitHub Pages `/dailynews/` 경로 대응)

#### 2. `publish/nav.js` 신설 — 공유 nav 모듈
- URL 깊이 감지 → 상대 경로 prefix 자동 계산 (Vercel·GitHub Pages 공통)
- `id="site-nav"` 요소에 탭 HTML 주입 (active 탭 자동 감지)
- 탭 목록: 📰 뉴스 브리핑 / 🤖 AI이슈 / 📊 주식 시황 / 📚 아카이브
- 4개 서브페이지 템플릿 모두 적용 (`web_news.html`, `web_stock.html`, `web_archive.html`, `web_stock_archive.html`)

#### 3. AI이슈 탭 추가 (`config/theme_config.py`, `themes/editorial.py`, `publish/nav.js`)
- `NAV_SECTIONS`에 `ai-issue` 항목 추가
- `editorial.py` `_layout()` nav_items 동기화
- 모든 페이지에서 AI이슈 탭 접근 가능

#### 4. SPA 아카이브 탭 분리 (`publish/app.html`)
- 아카이브 탭: JS 섹션 스위처 → `<a href="archive.html">` 직접 링크로 변경
- SPA 내장 아카이브 섹션 주석 처리 (삭제 아님 — `ARCHIVE_SECTION_HIDDEN_START/END`)

#### 5. 통합 검색 구현 (`scripts/build_site.py`, `publish/app.html`, `themes/editorial.py`)

**`build_search_index()` 확장** (`scripts/build_site.py`)
- 뉴스(`publish/news/*.json`): `news_en` + `news_ko` → 개별 기사 제목·링크·라벨
- AI이슈(`publish/ai-issue/YYYY-*.json`): `top10` 이슈 제목 + 소스 URL + 카테고리
- 주식(`publish/stock/stock-data.json`): 날짜별 시황 요약 문장
- `type` 필드 추가 (`news` / `ai-issue` / `stock`)
- 결과: 뉴스 84 · AI이슈 1 · 주식 13 = **8,175건** 인덱싱

**SPA 검색 교체** (`publish/app.html`)
- 기존: 현재 날짜 기사만 인라인 필터
- 신규: `search-index.json` lazy-fetch → 전체 기간 통합 검색
- 📰 뉴스 / 🤖 AI이슈 / 📊 주식 체크박스 필터
- 결과: 타입 배지 + 날짜(리포트 링크) + 기사 제목(원문 링크) + 키워드 하이라이트
- 최대 80건 표시, 체크박스 변경 시 즉시 재검색

**아카이브 검색 업그레이드** (`themes/editorial.py`)
- 동일한 통합 검색 UI (체크박스·배지·하이라이트)
- 최대 100건 표시

---

#### 6. 추가 개선 (세션 후반)
- **AI이슈 카드뉴스 슬라이더** (`publish/app.html`): 뉴스 섹션과 동일하게 `top10` → 가로 슬라이더 상단 표시. 카테고리 아이콘·중요도 별표·원문 링크 포함
- **archive.html 검색창 위치 이동** (`themes/editorial.py`): 하단 → "전체 리포트 색인" 제목 오른쪽 flex 배치
- **서브페이지 nav 탭 인디케이터 통일** (`templates/web_*.html` 4개): SPA `hnav-tab.active`와 동일하게 `border-bottom: 2px solid var(--color-blue-light)` 추가. 주식·뉴스·아카이브 서브페이지 현재 탭에 하단 컬러 바 표시

---

### 영향받은 파일
| 파일 | 변경 |
|------|------|
| `config/theme_config.py` | `SITE_LOGO_HTML` 추가, `NAV_SECTIONS` AI이슈 추가 |
| `themes/editorial.py` | nav_items AI이슈 추가, `render_archive()` 통합 검색 |
| `themes/base.py` | `SITE_LOGO_HTML` import·적용 |
| `scripts/build_site.py` | `build_search_index()` 3채널 확장, `_fmt_date()` 추출 |
| `publish/nav.js` | 신규 생성 |
| `publish/app.html` | 아카이브 탭 분리, 통합 검색 교체 |
| `templates/web_*.html` (4개) | `id="site-nav"`, `nav.js` script 태그 추가 |
| `publish/search-index.json` | 8,175건 통합 인덱스 |
| `publish/index.html` | 빌드 산출물 갱신 |
| `publish/archive.html` | 빌드 산출물 갱신 |

---

## 2026-06-03 (3차 — 파이프라인 정합성 + 스크립트 통합) [PR #18]

### 주제: 3채널 발송 순서 통일 · send 스크립트 6→2 통합 · 주식 텔레그램 구현

#### 배경
- `news.yml`: 이메일·텔레그램이 `main.py` 내부(HTML 빌드 전)에서 발송되던 순서 오류
- `ai_issue.yml`: 이메일·텔레그램이 커밋 전 단계에서 발송 (Pages 배포 전)
- `send_stock_email.py`, `send_news_email.py` 등 채널별 개별 스크립트 6개가 난립

---

### 변경 내용

#### 1. 파이프라인 발송 순서 통일
전체 채널 공통 순서: **수집·분석·저장 → HTML 빌드 → 커밋·push → Pages 배포 → Notion → 이메일 → 텔레그램**

- **`scripts/run_news.py`**: 이메일·텔레그램 발송 로직 제거. 수집/분석/MD저장(5단계)만 담당
- **`.github/workflows/news.yml`**: 이메일·텔레그램을 `deploy-pages` 스텝 이후로 이동. `RECIPIENT_EMAILS`·`TELEGRAM_*` 환경변수를 `main.py` 스텝에서 제거
- **`.github/workflows/ai_issue.yml`**: 이메일·텔레그램을 `deploy-pages` 스텝 이후로 이동 (커밋 전에 실행되던 것 수정)

#### 2. send 스크립트 6→2 통합
| 이전 (6개) | 이후 (2개) |
|-----------|-----------|
| `send_news_email.py` | `scripts/send_email.py --type news` |
| `send_stock_email.py` | `scripts/send_email.py --type stock` |
| `send_ai_issue_email.py` | `scripts/send_email.py --type ai-issue` |
| `send_news_telegram.py` | `scripts/send_telegram.py --type news` |
| `send_stock_telegram.py` | `scripts/send_telegram.py --type stock` |
| `send_ai_issue_telegram.py` | `scripts/send_telegram.py --type ai-issue` |

실제 발송 로직은 `core/shared/mailer.py` / `core/shared/telegram.py`에 유지.
스크립트는 타입별 데이터 로드·검증·전달만 수행.

#### 3. 주식 텔레그램 발송 구현
- **`core/shared/telegram.py`**: `send_stock_telegram()` 추가
  - `TELEGRAM_CHAT_ID_STOCK` 환경변수 → @msstockbrief 채널
  - 형식: 시장온도계 → 핵심요약 → 주요지수(코스피/코스닥/S&P500/원달러) → 키워드TOP3 → 사이트링크
- **`.github/workflows/stock_send.yml`**: 텔레그램 stub → 실제 구현 활성화, `TELEGRAM_CHAT_ID_STOCK` 시크릿 사용

#### 4. archive 카운트 버그 추가 수정
- **`scripts/build_site.py`** `build_archive_ctx()`: JSON 인덱스 기반으로 재변경
  - `reports-data.json` / `stock-data.json` / `ai-issue-data.json` 읽어서 항상 전체 목록 반영
  - (이전: MD glob이 `--from today` 파라미터에 영향받아 카운트가 1로 리셋되던 문제)

#### 5. CLAUDE.md 신규 생성
- 세션 간 컨텍스트 유지를 위한 프로젝트 컨텍스트 파일
- 3기기(웹/VSCode터미널/데스크탑앱) 공통 — `git pull` 로 동기화

---

### 워크플로우 에러 처리 현황 (수정 후)

| 스텝 | news.yml | stock_send.yml | ai_issue.yml |
|------|----------|----------------|--------------|
| 이메일 발송 | continue-on-error ✓ | continue-on-error ✓ | continue-on-error ✓ |
| 텔레그램 발송 | continue-on-error ✓ | continue-on-error ✓ | continue-on-error ✓ |
| Notion 동기화 | continue-on-error ✓ | continue-on-error ✓ | continue-on-error ✓ |
| git rebase 전략 | -X ours ✓ | — | -X ours ✓ |

---

## 2026-06-03 (2차 — 워크플로우 안정화)

### 주제: 아카이브 버그 수정 + 워크플로우 충돌 방지 개선

#### 배경
- PR #16 머지 후 stock_build.yml 봇이 구버전 코드로 archive.html 덮어씀 → 뉴스 1개로 리셋
- 3개 워크플로우(news/stock/ai_issue) 간 충돌 위험 및 에러 처리 불일치 발견

---

### 변경 내용

#### 1. archive.html 구조적 버그 수정 (`themes/editorial.py`, `scripts/build_site.py`)

**`themes/editorial.py`**
- `id="tabAI"` / `id="tabPanelAI"` → `id="tabAi"` / `id="tabPanelAi"`
  - JS `showTab('ai')` 는 `charAt(0).toUpperCase()+slice(1)` = `'Ai'` 로 ID를 찾음
  - 대문자 `AI` 와 불일치하여 AI이슈 탭 클릭이 무반응이던 버그 수정

**`scripts/build_site.py`**
- `build_archive_ctx(pages)` — news items를 `pages` 파라미터(필터된 목록)에서 읽던 로직 제거
- `reports/news_*.md` 전체 glob으로 변경 (stock/AI items와 동일 방식)
- 효과: `--from today` 실행 시에도 archive.html에 항상 전체 뉴스 목록 표시

#### 2. ai_issue.yml 커밋 목록 누락 수정 (`.github/workflows/ai_issue.yml`)
- 커밋 스텝에 `publish/archive.html`, `publish/reports-data.json` 추가
- AI이슈 주간 배포 후 메인 아카이브 카운트가 갱신되지 않던 문제 수정

#### 3. 워크플로우 충돌 방지 (`.github/workflows/news.yml`)
- `git add -f publish/stock/` (디렉토리 통째) → 명시적 파일 목록으로 교체
  ```
  publish/stock/20??-??-??.html
  publish/stock/index.html, archive.html, stock-data.json
  ```
  - stock_build.yml과 동일 목록으로 맞춤 (불필요한 파일 포함 방지)
- `git pull --rebase --autostash origin main` → `-X ours` 추가
  - stock_build.yml / ai_issue.yml 은 이미 `-X ours` 적용 중 → 3개 워크플로우 통일

#### 4. ai_issue.yml 에러 처리 강화 (`.github/workflows/ai_issue.yml`)
- Notion 동기화 스텝: `continue-on-error: true` 추가
- 이메일 발송 스텝: `continue-on-error: true` + `id: send_email` 추가
- 이메일 발송 실패 시 Actions 경고 로그 출력 스텝 추가 (`if: steps.send_email.outcome == 'failure'`)
- 효과: SMTP/Notion 장애 시에도 HTML 커밋·Vercel 배포는 정상 진행, 실패는 Actions UI 노란 경고(⚠)로 확인

---

### 워크플로우 에러 처리 현황 (수정 후)

| 스텝 | news.yml | stock_send.yml | ai_issue.yml |
|------|----------|----------------|--------------|
| 이메일 발송 | main.py 내부 처리 | continue-on-error ✓ | continue-on-error ✓ |
| 텔레그램 발송 | main.py 내부 처리 | (미구현) | continue-on-error ✓ |
| Notion 동기화 | (별도 스텝, 미설정) | continue-on-error ✓ | continue-on-error ✓ |
| git rebase 전략 | -X ours ✓ | — | -X ours ✓ |

---

## 2026-06-03

### 주제: 주식시황 워크플로우 재설계 + 뉴스 재분석 시스템 구축

#### 배경
- 6/1~6/3 뉴스 AI 분석 실패 (기사 목록만 기록됨)
- 주식시황 이메일이 당일 오전에 발송되는 타이밍 이슈
- 루틴 실행 시간이 4~5시간으로 길어지는 문제

---

### 변경 내용

#### 1. 뉴스 재분석 시스템 (`scripts/reanalyze.py`)
- **smart 모드**: 분석 실패 마커(`⚠ AI analysis failed`) 감지 후 해당 언어만 재분석
- **full 모드**: EN + KO 전체 초기화 재분석
- MD 섹션 교체 + JSON 사이드카 스마트 병합
- `news.yml`에 `workflow_dispatch` 추가 (mode/target_date/reanalyze_mode 파라미터)

#### 2. 뉴스 분석 버그 수정 (`core/news/analyzer.py`)
- `parse_md_for_json()` 반환값에 `category` 필드 누락 → `n.get("category", "")` 처리
- label→category 역매핑 추가 (`RSS_FEEDS` 기반)

#### 3. 주식시황 워크플로우 분리
**`stock_build.yml` 변경**:
- 백업 스케줄: KST 21:55 → **23:00** (`0 14 * * 1-5`)
- 이메일·Notion 발송 스텝 제거 (stock_send.yml로 이관)
- 루틴 → build 배포 흐름 명확화

**`stock_send.yml` 신규 생성**:
- 스케줄: **익일 08:00 KST** (`0 23 * * 0-4`)
- 최신 MD 자동 감지, 3일 초과 리포트 재발송 방지
- `workflow_dispatch` 특정 날짜 재발송 지원
- 이메일 + Notion + 텔레그램 stub

#### 4. 주식 시황 품질 게이트 (`scripts/send_stock_email.py`, `scripts/run_stock.py`)
- `_is_analysis_complete()`: MD에서 핵심 요약·온도계 근거 길이 검증
- 분석 미완성 시 이메일 발송 차단 + 관리자 알림

#### 5. 수집 모듈 날짜 버그 수정 (`core/stock/collector.py`)
- `market_close_time` 하드코딩 → `_trading_date_kst()` 함수로 정확한 거래일 계산
- 15:30 KST 기준 장 전/후 판단, 주말 역산 처리

#### 6. Notion DB ID 관리 방식 변경
- `watchlist.yaml` 하드코딩 제거 → GitHub Secret `NOTION_DATABASE_ID_STOCK`으로 이관
- `config/watchlist.py`의 `get_notion_db_id()` 함수 제거
- `stock_build.yml`은 이미 `${{ secrets.NOTION_DATABASE_ID_STOCK }}` 참조

#### 7. 루틴 프롬프트 v5 (`docs/stock_routine_prompt_v5.md`)
- Step 4 (Notion 등록) 제거
- Step 2 최적화: 섹터당 대표 종목 1개 + `get_historical_stock_prices` 사용
- 예상 MCP 호출: 39회 → ~15회

#### 8. 6/1·6/2 뉴스 분석 수동 복구
- AI 분석 실패 섹션을 수동 분석으로 교체
- 6/1: 봇넷 해체, 텍사스 홍역, 연방 과학 펀딩 위기 / 조선업·LG분할·현대차
- 6/2: OpenAI 소송, Nvidia RTX Spark, Meta AI 해킹 / 코스피 최고·청소년금융·IMF

---

### GitHub Secret 등록 필요
| Secret | 값 |
|---|---|
| `NOTION_DATABASE_ID_STOCK` | `362fae739c2b80c2ba08c6f31ae8f922` |

---

## 2026-05 (이전 작업)

- AI Issue 브리핑 시스템 추가 (`scripts/run_ai_issue.py`)
- 테마 시스템 분리 (`themes/`) — editorial/terminal/classic 등
- Notion 뉴스·주식 동기화 (`scripts/sync_notion.py`)
- reanalyze.py 초기 버전 추가
- `config/prompts.py` Gemini `response_mime_type` 충돌 수정
