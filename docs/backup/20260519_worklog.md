# 작업 로그 (Work Log)

> 프로젝트: AI Daily News + 주식시황 브리핑 자동화  
> 레포지토리: chamgil71/dailynews  
> 기록 기준: 완료된 작업 단위

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
