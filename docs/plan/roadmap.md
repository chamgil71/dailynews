# AI News Brief — 개발 로드맵

> 최종 수정: 2026-06-10  
> 기준: PR #19 병합 완료 (카드뉴스 SNS 배포), PR #22 (주식 파이프라인 버그 수정)  
> 상세 계획: 각 Phase 전용 문서 참조

---

## 현재 아키텍처 (Phase 1 완료)

```
수집·분석·저장 → HTML 빌드 → 커밋·push → Pages 배포 → Notion → 이메일 → 텔레그램
```

| 채널 | 수집 스케줄 | 발송 |
|------|------------|------|
| 뉴스 | `news.yml` KST 03:15 매일 | 배포 완료 후 즉시 |
| 주식 | Claude 루틴 → `stock_build.yml` 23:00 | `stock_send.yml` 익일 08:00 |
| AI이슈 | `ai_issue.yml` 일요일 07:00 | 배포 완료 후 즉시 |

---

## Phase 2 — 구독 시스템 (최우선)

> 상세: `docs/plan/plan_subscription_system.md`

### 목표
RECIPIENT_EMAILS 하드코딩 → Supabase DB 기반 구독자 관리로 전환.  
콘텐츠 유형별(뉴스·주식·AI이슈) 선택 구독 지원.

### 인프라
- **Supabase** (무료 tier): `subscribers` 테이블 + `send_log` 테이블
- **Vercel Serverless API**: `/api/subscribe`, `/api/verify`, `/api/unsubscribe`, `/api/manage`
- 별도 서버 없음 — 기존 GitHub Actions + Vercel만 사용

### DB 스키마 요약
```sql
subscribers(id, email, status, token,
            subscribe_news, subscribe_stock, subscribe_ai_issue,
            created_at, verified_at, unsubscribed_at)

send_log(id, content_type, report_date, channel,
         status, recipient_count, analysis_ok, sent_at)
```

### 구현 순서
1. Supabase 프로젝트 생성 + 테이블 마이그레이션
2. `api/subscribe.py` (Vercel) — 이메일 등록 + 인증 메일 발송
3. `api/verify.py` — 토큰 확인 후 `status = active`
4. `api/unsubscribe.py` — 수신거부
5. `core/shared/mailer.py` 수정 — `RECIPIENT_EMAILS` 대신 Supabase 조회
6. 구독 폼 페이지 (`publish/subscribe.html`)

### 필요 GitHub Secrets
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

---

## ✅ Phase 3 — 카드뉴스 SNS 내보내기 (완료 — PR #19, 2026-06-06)

> 상세: `docs/plan/plan_cardnews.md`, `docs/plan/plan_improvement.md` §2-4

### 완료된 것
- `scripts/build_cardnews.py` — 3채널(뉴스·AI이슈·주식) 카드뉴스 HTML 빌드
- `scripts/generate_cardnews_images.py` — Playwright/Pillow → 1080×1080 PNG 생성
- `scripts/post_cardnews.py` — SNS 발송 (텔레그램 완료, Instagram/Twitter/Threads 스켈레톤)
- `scripts/post_instagram.py` — Instagram Graph API v21.0 카루셀
- `.github/workflows/cardnews.yml` — 3채널 트리거 자동화
- `publish/cardnews/{news|ai-issue|stock}/` — 채널별 HTML + PNG + data.json 출력

### 잔여 작업
- Instagram/Twitter Secrets 설정 후 실제 발송 검증 (`INSTAGRAM_ACCESS_TOKEN` 등 미설정)

---

## ✅ Phase 4 — 검색 고도화 (완료 — 2026-06-04)

> 상세: `docs/plan/plan_improvement.md` §2-6

### 완료된 것
- `publish/search-index.json` — `build_site.py` 빌드 시 자동 갱신 (뉴스 + AI이슈 + 주식 전체)
- 클라이언트 검색: `app.html`에서 인덱스 1회 fetch → 로컬 필터링
- 키워드 `<mark>` 하이라이팅, 결과에서 해당 날짜 브리핑 링크 제공

---

## Phase 5 — 클라우드 DB 전환 (장기)

> 상세: `docs/plan/plan_improvement.md` §3

### 목표
GitHub 레포 내 `storage/news_db.xlsx` → Supabase PostgreSQL 전환  
(Phase 2에서 Supabase를 이미 사용하므로 같은 인스턴스 확장)

### 마이그레이션 단계
1. Supabase에 `news_items`, `stock_reports` 테이블 생성
2. `scripts/migrate_to_cloud.py` — 기존 xlsx 데이터 일괄 이관
3. `core/shared/db.py` 쿼리 인터페이스를 Supabase REST API 호출로 대체
4. `storage/` 폴더 git 추적 제거

---

## 보류/아이디어

| 항목 | 메모 |
|------|------|
| Vercel 404 SPA 라우팅 | `/2026-05-22` → `app.html` 리라이트 (`plan_improvement.md` §2-2) |
| 이메일 본문 카드뉴스 인라인 | Phase 3 완료 후 `mailer.py` 연동 |
| 텔레그램 이미지 카드 발송 | `send_telegram.py`에 `send_photo` API 추가 |
| 주식 AI 분석 모델 개선 | `stock_routine_prompt_v5.md` 참고 |
