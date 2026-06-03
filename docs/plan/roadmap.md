# AI News Brief — 개발 로드맵

> 최종 수정: 2026-06-03  
> 기준: PR #18 병합 완료 (파이프라인 정합성·스크립트 통합 완료)  
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

## Phase 3 — 카드뉴스 SNS 내보내기

> 상세: `docs/plan/plan_cardnews.md`, `docs/plan/plan_improvement.md` §2-4

### 목표
뉴스 이슈·키워드를 슬라이드형 카드뉴스 HTML로 자동 생성.  
인스타그램·스레드 등 SNS용 1080×1080 PNG로 1클릭 내보내기.

### 현재 준비된 것
- `build_site.py`에 `_parse_issues()`, `_parse_keywords()` 구현 완료
- `publish/reports-data.json`에 `issues_en/ko`, `keywords_en/ko` 적재 중

### 구현 내용
1. **카드뉴스 HTML 템플릿** (`templates/cardnews.html`)
   - 순수 CSS scroll-snap 가로 슬라이드 (외부 라이브러리 없음)
   - 디자인 테마: `config/cardnews_themes.json` — glass_dark / neon_cyber / minimal_light
2. **`scripts/build_cardnews.py`** — 날짜별 `publish/cardnews/YYYY-MM-DD.html` 빌드
3. **SNS 내보내기 버튼** — `html2canvas` CDN, 1080×1080px PNG 다운로드
4. **사이트 연동** — `app.html` 상단 Shorts 배너 영역으로 노출

### 디자인 테마 구조
```json
{
  "active_card_theme": "glass_dark",
  "themes": {
    "glass_dark":    { "bg_gradient": "...", "card_bg": "rgba(255,255,255,0.05)", ... },
    "neon_cyber":    { "accent_color": "#a78bfa", ... },
    "minimal_light": { "bg_gradient": "linear-gradient(135deg, #f8fafc ...)", ... }
  }
}
```

---

## Phase 4 — 검색 고도화

> 상세: `docs/plan/plan_improvement.md` §2-6

### 목표
현재 당일 리포트 내 검색 → 전체 기간 과거 기사 전수 검색

### 구현 방안 (B안 권장)
- **빌드 시** `build_site.py`에서 `publish/search-index.json` 생성 (~100~200KB)
  - 구조: `[{date, title, category, link, summary}, ...]`
- **클라이언트**: `app.html`에서 검색 입력 시 인덱스 1회 fetch → 로컬 필터링
- **UX**: 매칭 키워드 `<mark>` 하이라이팅, 결과 항목에 "해당 날짜 브리핑 전체 보기" 링크

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
