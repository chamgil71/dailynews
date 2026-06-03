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
- 새 작업 시작 시: `git checkout main && git pull && git checkout -b claude/작업명`
- 작업 완료 시: PR 생성 → 병합 → 브랜치 삭제

---

## 현재 상태 (2026-06-03)

### 완료된 작업 (main 반영 완료)
- [x] 3채널 파이프라인 발송 순서 통일 (수집→빌드→배포→이메일→텔레그램)
- [x] `run_news.py`에서 이메일·텔레그램 분리
- [x] `send_email.py` / `send_telegram.py` 통합 스크립트 생성 (6개→2개)
- [x] 주식 텔레그램 발송 구현 (`@msstockbrief`, `TELEGRAM_CHAT_ID_STOCK`)
- [x] `build_site.py` archive 카운트 버그 수정 (JSON 인덱스 기반)
- [x] AI이슈 탭 클릭 버그 수정 (`tabAI` → `tabAi`)
- [x] `news.yml` Notion sync `continue-on-error`, `-X ours` 추가
- [x] `ai_issue.yml` Notion sync / 이메일·텔레그램 배포 후 실행
- [x] **PR #18** (`claude/pipeline-fix-clean` → `main`) 병합 완료 (2026-06-03 10:42)
- [x] `CLAUDE.md` main 반영

### 검증 필요 (다음 실행 시 확인)
- [ ] `stock_send.yml` workflow_dispatch 수동 실행 → @msstockbrief 채널 수신 확인
- [ ] `news.yml` 자동 실행 시 이메일·텔레그램이 Pages 배포 로그 이후에 찍히는지 확인
- [ ] `ai_issue.yml` 자동 실행 시 deploy-pages 스텝 이후 이메일·텔레그램 실행 확인

### 다음 개발 (우선순위 순)
- [ ] 구독 시스템 구현 — Supabase + Vercel API (`docs/plan/roadmap.md` Phase 2 참고)
- [ ] 카드뉴스 SNS 내보내기 — html2canvas, 인스타용 1080×1080 PNG
- [ ] 전체 검색 인덱스 (`publish/search-index.json`) 빌드 + 앱 검색 고도화

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
