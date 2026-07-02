# dailynews (AI News Brief) 사양서 (spec.md)

> [!IMPORTANT]
> 본 사양서는 개발 요구사항 및 설계의 **닻(anchor)**입니다.
> 에이전트 단독으로 수정할 수 없으며, 변경 시 반드시 사용자의 사전 승인을 받아야 합니다.
> 환경변수 **전체 명세는 [`env_spec.md`](./env_spec.md)가 SSOT**이며, 본 문서는 그룹만 요약합니다.

## 1. 개요 및 목적
- **비즈니스 배경**: 뉴스·주식·AI이슈 정보를 매일 수집·요약해 여러 채널로 발행하는 작업을 자동화하고자 한다.
- **해결하려는 문제**: RSS 수집 → LLM 분석 → 웹/이메일/텔레그램/SNS 발행을 서버리스(비용 $0/월 지향)로 완전 자동화한다.
- **최종 목표**: 3채널을 GitHub Actions 스케줄로 무인 수집·빌드·발송하며, 크레덴셜·비용·발송 안전을 통제한다.

## 2. 세부 요구사항 및 범위
- **채널별 기능 요구사항** (`.github/workflows/` + `core/`):
  | 채널 | 수집 | 빌드/배포 | 발송 | 코드 |
  |---|---|---|---|---|
  | 뉴스 | `news.yml` (KST 03:15) | 동일 워크플로우 | 배포 후 즉시 | `core/news/` |
  | 주식 | Claude Code 루틴 21:25 | `stock_build.yml` (23:00) | `stock_send.yml` (익일 08:00) | `core/stock/` |
  | AI이슈 | `ai_issue.yml` (일 07:00) | 동일 워크플로우 | 배포 후 즉시 | `core/ai_issue/` |
- **공통 발송/연동 요구사항** (`core/shared/`):
  - F-1 이메일: `mailer.py`(Gmail SMTP) + Supabase 구독자, 폴백 `RECIPIENT_EMAILS`, HMAC 구독취소 서명
  - F-2 텔레그램: `telegram.py` — 뉴스/AI이슈(`TELEGRAM_CHAT_ID`), 주식(`TELEGRAM_CHAT_ID_STOCK`), 모니터링(`_MONITOR`)
  - F-3 웹 배포: `publish/` → Vercel(주) + GitHub Pages(백업)
  - F-4 Notion 동기화: `notion.py` — 채널별 DB(`NOTION_DATABASE_ID_*`)
  - F-5 SNS 카드뉴스: `build_cardnews.py → generate_cardnews_images.py → post_cardnews.py` (Instagram/Facebook/Threads/Twitter)
  - F-6 구독 API(Vercel 서버리스): `api/subscribe.py`·`unsubscribe.py`·`confirm.py` (Supabase)
- **비기능 요구사항 (강화)**:
  - 보안: 모든 시크릿은 `.env`/GitHub Secrets/Vercel 환경변수로만(하드코딩 금지). GitHub Secrets ≠ Vercel 환경변수(별도 등록). 상세 [`env_spec.md`](./env_spec.md)
  - 발송 안전: 실발송 로직 변경 시 드라이런/샌드박스 검증 후 **사용자 승인 하에만** 실발송
  - 비용: LLM 토큰 낭비·무한 재시도 차단, 모델/프롬프트 변경 시 비용 영향 명시 (기본 `gemini-2.5-pro`/`gemini-2.0-flash-lite`)
  - 관측성: 발송 성공/실패 로깅, 모니터링 채널(`TELEGRAM_CHAT_ID_MONITOR`) 미설정 시 조용히 건너뜀

## 3. 시스템 아키텍처 및 설계
- **데이터 흐름**: `RSS/네이버 수집` → `LLM 분석(Gemini/Claude/GPT)` → `렌더(templates/themes)` → `publish/ 배포(Vercel/Pages)` → `mailer·telegram·notion·SNS 발송`
- **스케줄러**: `.github/workflows/*.yml` cron 기반 (`news.yml`, `stock_build.yml`, `stock_send.yml`, `ai_issue.yml`) — 시각 임의 변경 금지
- **환경변수 그룹** (전체·획득법은 [`env_spec.md`](./env_spec.md)):
  1. LLM API (`LLM_PROVIDER`, `GEMINI_API_KEY` …)
  2. 이메일 Gmail SMTP (`GMAIL_USER`, `GMAIL_APP_PASSWORD`, `UNSUBSCRIBE_SECRET`)
  3. 사이트/Vercel (`SITE_BASE_URL` …)
  4. Supabase 구독 (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`)
  5. 네이버 API (`NAVER_CLIENT_ID/SECRET`)
  6. Notion (`NOTION_API_KEY`, `NOTION_DATABASE_ID_*`)
  7. 텔레그램 (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID[_STOCK|_MONITOR]`)
  8. SNS 카드뉴스 (Instagram/Facebook/Threads/Twitter 토큰)
  9. 테마 (`SITE_THEME`, `THEME_*`)
- **아키텍처 상세**: [`architecture.md`](./architecture.md), 운영 컨텍스트 [`../CLAUDE.md`](../CLAUDE.md)

## 4. 검증 계획
- **테스트 시나리오**: 드라이런으로 수집·분석·렌더 파이프라인 무결성 확인(실발송 없이), 채널별 워크플로우 빌드 확인
- **검증 명령**:
  ```bash
  git pull origin main
  python -m pytest tests/
  ```
  > `main.py`는 `scripts/run_news.py`로 위임되는 뉴스 파이프라인 진입점이며 실행 시 발송까지 이어질 수 있으므로, "검증" 용도로 직접 실행하지 않습니다. 발송은 `scripts/send_email.py`·`send_telegram.py`(`--type news|stock|ai-issue`)를 통하며, 변경 시 안전한 방식으로 사전 검증 후 사용자 승인 하에만 실발송합니다.
- **기대 성공 지표**: pytest 통과 + 실발송 0건(사전 검증 단계). 합격선 _TODO(목표치)_.
