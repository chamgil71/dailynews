# 작업 로그 (Work Log)

> 프로젝트: AI Daily News + 주식시황 브리핑 자동화  
> 레포지토리: chamgil71/dailynews  
> 기록 기준: 완료된 작업 단위

---

## 2026-05-19 — 폴더 구조 재편 + 테마 시스템 아키텍처 정립

### 배경 (docs/test.md 요구사항 요약)
- 폴더를 기본설정/스크립트/테마/웹서비스 레이어로 분리
- 뉴스데일리·주식시황 콘텐츠는 독립·유기적으로 동작
- 테마: 전체 레이아웃 테마 vs 색상만 바꾸는 방식 검토
- 불필요 파일 storage/ 이동, README·guide·worklog 업데이트
- 3개 실험 트랙: ① 클리핑·저장 ② 테마 디자인 ③ 서비스 연동

### 1. 루트 정리
- `integration_plan_mywiki.md`, `changes.patch`, `requirements.txt.backup` → `storage/` 이동
- `docs/*.md` → `docs/backup/20260519_*.md` 전체 백업

### 2. core/ 서브패키지 구조 도입

```
core/
  news/    collector.py · analyzer.py · report.py   ← 실제 코드
  stock/   collector.py · analyzer.py · report.py   ← 실제 코드
  shared/  mailer.py · db.py                        ← 실제 코드
  *.py (루트)  → 하위 호환 1-line shim (기존 임포트 경로 유지)
```

- `core/__init__.py`에 구조 문서화
- 기존 `from core.stock_collector import ...` 등 구 임포트 경로 모두 호환 유지

### 3. scripts/ 신규 진입점 추가

| 파일 | 역할 |
|---|---|
| `scripts/run_news.py` | 뉴스 수집·분석·저장·발송 (권장 진입점, core.news.* 직접 사용) |
| `scripts/run_stock.py` | 주식 수집·분석·저장·발송 (권장 진입점, core.stock.* 직접 사용) |
| `main.py` | GitHub Actions 호환 shim → scripts/run_news.py |

### 4. 테마 아키텍처 정립 — config vs themes 역할 분리

**변경 전:**
- `config/theme_config.py`에 CSS 색상값(THEME_TOKENS) 포함 → 설정과 구현 혼재

**변경 후:**

| 파일 | 역할 |
|---|---|
| `config/theme_config.py` | 순수 설정만: 어떤 테마 쓸지(SECTION_THEMES), 푸터 텍스트, 내비 구조 |
| `themes/{name}.py` | CSS·폰트·레이아웃 렌더링 코드 + `TOKENS` dict |
| `themes/base.py` | 공통 렌더링 엔진, `get_tokens(name)` → importlib으로 동적 로드 |

- 6개 테마 모두 `TOKENS` dict 보유 (colors, typography, meta)
- `config/theme_config.py`에서 `THEME_TOKENS` 완전 제거
- `themes/base.py`의 `get_tokens()` → `importlib.import_module(f"themes.{name}").TOKENS`

### 5. 새 테마 추가 규칙 확정

```
themes/{name}.py 파일 하나만 생성하면 됨:
  TOKENS = { "meta": {...}, "colors": {...}, "typography": {...} }
  + render_report(), render_archive(), render_email(), render_stock_*() 함수
```
`config/theme_config.py`의 `DESIGN_TEMPLATES`에 추가는 UI 표시용(선택사항).

### 6. 3개 실험 트랙 확정

| Track | 흐름 |
|---|---|
| 1 클리핑·저장 | RSS/API → core/news\|stock → reports/*.md → DB |
| 2 테마 디자인 | reports/*.md + themes/*.py → scripts/build_*.py → publish/*.html |
| 3 서비스 연동 | publish/*.html → Pages, reports/*.md → Notion, email → Gmail/TG |

### 7. 문서 정리
- `docs/test.md` → `docs/backup/` (스크래치 패드, 내용 worklog 반영 완료)
- `docs/Additional_Task.md` → `docs/backup/` (watchlist 설계문서, 구현 완료)
- `themes/Additional_Task.md` → `docs/backup/` (themes 폴더 내 설계문서 부적합)

---

## 2026-05-18 — Phase 1 완료: 디자인 시스템 + 주식시황 자동화

### 1. 프롬프트 구조화 (config/prompts.py)

**목표:** AI 분석 결과를 파싱 가능한 구조로 고정

- `## 핵심 이슈 TOP 3` → `### 핵심 이슈 TOP 3` (h3, h2 섹션 충돌 방지)
- `## 주목할 트렌드` → `### 주목할 트렌드 키워드`
- 각 이슈에 `🔗 출처: [기사 제목](URL)` 형식 추가
- 키워드 형식: `- **키워드**: 설명` 고정
- `max_tokens`: 800 → 1500 (키워드 섹션 잘림 방지)

### 2. 분석기 URL 전달 (core/analyzer.py)

- `_build_prompt()` 수정: title_block에 기사 URL 포함
  ```
  [카테고리] 제목 — https://...
  ```

### 3. 사이트 빌드 구조화 파싱 (scripts/build_site.py)

- `_parse_issues(text)`: `### 핵심 이슈 TOP 3` 섹션 파싱 → title/body/url 추출
- `_parse_keywords(text)`: `### 주목할 트렌드 키워드` 파싱 → keyword/desc 추출
- `parse_md_for_json()`: `issues_en`, `issues_ko`, `keywords_en`, `keywords_ko` → `reports-data.json`

### 4. 테마 시스템 (themes/)

**설정(config) - 코드(themes) - 콘텐츠(reports/publish) 분리 원칙 확립**

- `config/theme_config.py`: CSS 디자인 토큰, NAV/HUB 섹션 설정
- `themes/base.py`: 공통 레이아웃·CSS·컴포넌트 렌더러 (뉴스 + 주식)
- `themes/classic.py`: Classic Navy (기본 테마)
- `themes/minimal.py`: Minimal Pretendard (넓은 여백, stats-row 컴포넌트)
- `themes/ink.py`: Ink 신문 스타일 (붉은 accent)
- `themes/forest.py`: Forest 핀테크 그린 (에메랄드 accent)
- 테마 전환: `SITE_THEME` 환경변수 (또는 GitHub Secret)

### 5. 주식시황 시스템 구현

**두 경로 아키텍처:**
- **Primary**: Claude Code 웹 루틴 → MCP(UsStockInfo + NaverSearch) → MD 저장 → git push → GitHub Actions 자동 트리거
- **Backup**: GitHub Actions 정기실행 (KST 16:45 평일) → yfinance → Gemini → 완전 자동화

**신규 파일:**
| 파일 | 역할 |
|------|------|
| `config/stock_prompts.py` | 루틴 프롬프트 + LLM 분석 프롬프트 + 티커 정의 |
| `templates/stock_report.md` | Jinja2 주식 리포트 템플릿 (섹션 구조 기준) |
| `core/stock_collector.py` | yfinance 데이터 수집 (지수/환율/섹터 종목/뉴스) |
| `core/stock_analyzer.py` | LLM 분석 + 섹션 파싱 (온도계/키워드/섹터표) |
| `core/stock_report.py` | Jinja2 렌더링 + MD 저장 |
| `scripts/stock_main.py` | GitHub Actions 백업 경로 진입점 |
| `scripts/build_stock_site.py` | stock MD → HTML 빌드 |
| `scripts/send_stock_email.py` | push 트리거 경로 이메일 발송 |
| `.github/workflows/stock_build.yml` | push 트리거 + 정기 백업 워크플로우 |

**기존 파일 수정:**
| 파일 | 변경 내용 |
|------|----------|
| `config/settings.py` | STOCK_REPORTS_DIR, STOCK_EMAIL_SUBJECT, NAVER_* 추가 |
| `config/theme_config.py` | NAV/HUB stock 섹션 enabled: True |
| `themes/base.py` | render_stock_report/archive/email 추가 |
| `themes/classic/ink/forest/minimal.py` | stock 렌더러 wrapper 추가 |
| `core/mailer.py` | subject_override 파라미터 추가 |
| `requirements.txt` | yfinance>=0.2.40 추가 |

### 6. Claude 루틴 프롬프트 정비

- `docs/claude_주식시황.md` 전면 재작성
  - 기존: 웹 검색 + Gmail MCP 이메일 발송
  - 변경: PlayMCP UsStockInfo + NaverSearch + Write tool + Notion MCP + git push
  - 이메일은 GitHub Actions에 위임 (루틴에서 제거)

---

## 2026-05-18 — Phase 0: 기반 작업

> (이전 세션 포함 내용)

- RSS 수집 → AI 분석 → Markdown 리포트 → 이메일 + 사이트 기본 파이프라인 구축
- Gmail SMTP로 이메일 발송 전환 (Resend API 제거)
- LLM 전략 패턴: GPT / Claude / Gemini 환경변수로 교체
- GitHub Actions cron 자동화 (news.yml)
- Vercel 동적 웹앱 (app.html + reports-data.json) 연동

---

## 미완료 / 다음 단계

| 항목 | 상태 | 비고 |
|------|------|------|
| Phase 2: 카드뉴스 | 미시행 | `_parse_issues`, `_parse_keywords` 데이터 준비 완료 |
| 주식 Notion 연동 테스트 | 미완 | 루틴 실행 후 확인 필요 |
| GitHub Secrets 등록 | 미완 | NAVER_CLIENT_ID/SECRET (네이버 API 미보유 시 선택) |
| stock_build.yml 실 테스트 | 미완 | stock MD push 후 Actions 트리거 확인 필요 |


## [추가 질의] app.html UX 이슈 정리 — 2026-05-19

### 이슈 1. 이메일 email_html 연결 끊김
- build_site.py 가 email_html(분석 섹션만) 별도 생성하지만 run_news.py send_email(md_content)에는 원본 MD 전체 전달됨 (플러밍 단절)
- 조치: send_email()에 선택적 html_content 파라미터 추가. 현재는 원본과 동일하게 발송, 향후 분리 가능 구조 확보

### 이슈 2. 뉴스브리핑 — 기사 목록 이중 표시 인식
- combined 필드 생성 시 ## 🌐 헤더가 regex 비캡처 그룹에 소비됨 → Global News Analysis가 h2가 아닌 평문으로 표시, 섹션 구분 불명확
- combined에 분석 불릿/번호 목록이 있고, 하단에 newsHtml() 기사 토글이 별도 추가 → 같은 리스트가 두 번 나오는 것처럼 인식됨
- 조치: build_site.py combined 추출 regex 수정 — ## 🌐 / ## 🇰🇷 헤더 포함하도록 변경

### 이슈 3. 아카이브 날짜 클릭 → 별도 standalone HTML 오픈
- renderArchive()가 날짜.html 링크 생성 → 다른 CSS의 단독 페이지로 이동
- 조치: onclick으로 app.html 내부 섹션 전환 (navToReport() 함수 신설)

### 이슈 4. 탭 전환 시 디자인 불일치
- app.html(SPA)과 standalone HTML(테마 CSS)이 별개로 작동
- 조치: 이슈 3 조치로 해결 — 날짜 클릭이 SPA 내부에서 처리되면 디자인 통일

### 이슈 5. 아카이브 사이드바 미작동
- archive 탭에서 좌측 날짜 목록이 뉴스 전용으로 고정되어 클릭 동작이 어색함
- 조치: archive 탭 활성 시 사이드바 날짜 목록 카드 숨김 처리

### 이슈 6. 아카이브 레이아웃 — 뉴스/주식 분리 요청
- 현재: 뉴스+주식 혼합 날짜 목록
- 요구: 뉴스브리핑 통계+날짜 목록 / 주식시황 통계+날짜 목록 두 그룹으로 분리
- 조치: archiveSection 내부에 두 그룹 카드로 재설계

### 이슈 7. 중복 뉴스 수집 (캐시 미지속)
- .cache/ 폴더가 .gitignore에 포함 → GitHub Actions 실행마다 캐시 초기화 → 동일 기사 재수집
- 조치 옵션 확인 중: (A) DB URL 기반 중복 제거, (B) .cache/ git 커밋 허용 — 사용자 선택 필요