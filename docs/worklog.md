# 📋 Work Log — DailyNews

개발 이력 및 주요 변경사항 기록.

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
