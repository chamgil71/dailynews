# 파이프라인 파일 생성 루틴 점검 (2026-06-14)

## 개요

3채널 × 파이프라인별로 **"어떤 날짜명으로 파일이 생성되어야 하는가"** 와 **"실제 코드가 하는 것"** 을 정리한다.
반복 에러 원인과 재발 방지 수정 내용 포함.

---

## 1. 채널별 파일 생성 요약

| 채널 | 파일 패턴 | 날짜 기준 | 실행 시각 | 주말 동작 |
|------|---------|---------|---------|---------|
| 뉴스 | `news_YYYY-MM-DD.md` | 실행일(KST) | 매일 KST 03:15 | 생성됨 (의도적) |
| AI이슈 | `ai_issue_YYYY-MM-DD.md/.json` | 실행일(일요일 KST) | 매주 일 KST 07:00 | 일요일만 실행 |
| 주식 일일 | `stock_YYYY-MM-DD.md` | **거래일** (≠ 실행일) | 평일 21:25 KST (Claude 루틴) | ~~경고만 출력하고 계속~~ → **수정: return으로 중단** |
| 주식 주간 | `weekly_YYYY-MM-DD.md` | 토요일 날짜 | 토요일 수동 (Claude 루틴) | 토요일 전용 |

---

## 2. 채널별 상세 흐름

### 2-1. 뉴스 채널

```
news.yml (매일 UTC 18:15 = KST 03:15)
  └─ run_news.py          → reports/news_YYYY-MM-DD.md (실행일)
  └─ build_site.py        → publish/news/YYYY-MM-DD.html + data.json
  └─ GitHub Pages 배포
  └─ send_email.py --type news
  └─ send_telegram.py --type news
```

**날짜 규칙**: `datetime.now(KST)` 실행 시각 기준.
토·일도 생성 (주말 뉴스 요약 목적).

**실제 파일 확인**:
- `reports/news/` 없음 (MD는 `reports/` 직하에 `news_YYYY-MM-DD.md`)
- `publish/news/2026-06-14.html` — 오늘(일요일)도 정상 생성됨 ✅

---

### 2-2. AI이슈 채널

```
ai_issue.yml (UTC 토 22:00 = KST 일 07:00)
  └─ run_ai_issue.py      → reports/ai-issue/ai_issue_YYYY-MM-DD.md + .json
  └─ build_ai_issue_site.py → publish/ai-issue/YYYY-MM-DD.html + data.json
  └─ GitHub Pages 배포
  └─ send_email.py --type ai-issue
  └─ send_telegram.py --type ai-issue
```

**날짜 규칙**: 실행일(일요일) KST 기준.
실제 파일: `ai_issue_2026-05-31`, `ai_issue_2026-06-07`, `ai_issue_2026-06-14` — 모두 일요일 날짜 ✅

**주의**: `--date` 인자로 날짜 오버라이드 가능.

---

### 2-3. 주식 일일

```
Claude Code 루틴 (평일 21:25 KST)
  └─ run_stock.py         → reports/stock/stock_{거래일}.md
       ↓ mcp__github__push_files (main 직접)
stock_build.yml (push 감지 또는 평일 23:00 KST 스케줄 백업)
  └─ build_stock_site.py  → publish/stock/YYYY-MM-DD.html + data.json
  └─ GitHub Pages 배포
stock_send.yml (익일 KST 08:00, 일~토)
  └─ send_email.py --type stock
  └─ sync_notion.py --type stock
  └─ send_telegram.py --type stock
```

**날짜 규칙 (핵심)**:
- `core/stock/collector.py::_trading_date_kst()` 가 거래일을 역산
- 15:30 KST 이후 → 당일 거래일
- 토요일 실행 → 금요일 거래일
- 일요일 실행 → 전주 금요일 거래일
- 이 값(`trading_date`)이 파일명·제목 모두의 기준

**파일명 예시**:
- 금요일(6/12) 21:25 실행 → `stock_2026-06-12.md` ✅
- 토요일(6/13) 21:27 실행 → `stock_2026-06-12.md` 이어야 함 (거래일=6/12)

---

### 2-4. 주식 주간

```
Claude Code 토요일 루틴 (수동)
  └─ 월~금 5일치 MD 수집·분석
  └─ mcp__github__push_files → reports/stock/weekly_YYYY-MM-DD.md (토요일 날짜)
weekly_build.yml (weekly_*.md push 감지)
  └─ update_history.py
  └─ build_stock_site.py    → 일일+주간 통합 빌드
  └─ build_site.py          → 뉴스 SPA 재빌드
  └─ GitHub Pages 배포
stock_send.yml (익일 일요일 KST 08:00)
  └─ weekly 파일 감지 시 --type weekly-stock 분기
```

**현황**: `weekly_*.md` 파일 없음 → 주간 루틴 미실행 상태.

---

## 3. 발견된 버그 및 수정 내역

### 버그 1: `run_stock.py` 주말 차단 미구현 (수정 완료)

**증상**: 토·일에 `run_stock.py` 실행 시 경고만 출력하고 수집·분석·MD 저장까지 계속 진행.

**원인 코드** (`scripts/run_stock.py` 113행):
```python
if now_weekday >= 5:
    logger.warning("...")   # return 없음 → 계속 실행
```

**수정 코드**:
```python
if now_weekday >= 5:
    day_name = "토요일" if now_weekday == 5 else "일요일"
    logger.warning(f"[주말 감지] {day_name} — 주식 시장 휴장. 실행을 건너뜁니다.")
    return   # ← 추가
```

---

### 버그 2: 루틴 Step 6 날짜 혼동 (문서 수정 완료)

**증상**: 토요일(6/13)에 루틴을 수동 실행할 때 거래일(6/12) 대신 실행일(6/13)로 파일 경로를 지정 → `stock_2026-06-13.md` 잘못 생성.

**원인**: `docs/stock_routine.md` Step 5/6의 `YYYY-MM-DD`가 "거래일"인지 "실행일"인지 명시 없었음.

**수정**: Step 5/6에 명시적 경고 추가
```
⚠️ 날짜 규칙: 파일명·제목은 Step 1 trading_date(거래일) 사용. 실행일 아님.
```

---

### 버그 3: `stock_2026-06-13.md` 중복 오염 파일

**현황**: `reports/stock/`에 두 파일 동시 존재
- `stock_2026-06-12.md` — 금요일 21:25 정상 생성 (S&P +1.75%, 정확)
- `stock_2026-06-13.md` — 토요일 21:27 잘못 생성 (S&P +0.50%, 동일 거래일 데이터인데 수치 다름)

**처리 필요**: `stock_2026-06-13.md` 삭제 + `publish/stock/2026-06-13.html/json` 삭제 후 재빌드.
→ **사용자 확인 후 별도 진행** (data.json에서 6/13 항목 제거 포함).

---

## 4. 재발 방지 체크리스트

### 루틴 실행 전 체크
- [ ] 오늘이 평일(월~금)인가? 토·일이면 일일 루틴 실행 금지
- [ ] Step 6 파일 경로: `trading_date`(Step 1 수집값)를 쓰고 있는가?
- [ ] 동일 날짜 MD가 이미 존재하는가? → 재실행 시 덮어쓰기 확인

### 수동 실행 시 특히 주의
- 주간 루틴(토요일)과 일일 루틴(평일)을 혼동하지 말 것
- 토요일에 일일 루틴 실행 → `run_stock.py`가 차단 (수정 완료)
- 주간 루틴은 `docs/weekly_routine_v1.md` 별도 프로세스

---

## 5. 각 채널 최신 생성 현황 (2026-06-14 기준)

| 채널 | 최신 파일 | 날짜 | 상태 |
|------|---------|------|------|
| 뉴스 | `publish/news/2026-06-14.html` | 오늘(일) | ✅ |
| AI이슈 | `reports/ai-issue/ai_issue_2026-06-14.md` | 오늘(일) | ✅ |
| 주식 일일 | `reports/stock/stock_2026-06-12.md` | 금요일 | ✅ (정상) |
| 주식 일일 (오염) | `reports/stock/stock_2026-06-13.md` | 토요일 잘못생성 | ⚠️ 삭제 필요 |
| 주식 주간 | 없음 | — | ⏳ 루틴 실행 대기 중 |

---

## 6. 각 워크플로우 트리거 요약

| 워크플로우 | 트리거 | 스케줄 |
|-----------|-------|-------|
| `news.yml` | push(뉴스 MD) + 스케줄 | 매일 KST 03:15 |
| `ai_issue.yml` | push(AI이슈 MD) + 스케줄 | 매주 일 KST 07:00 |
| `stock_build.yml` | push(`stock_*.md`) + 스케줄 | 평일 KST 23:00 |
| `stock_send.yml` | 스케줄만 | 매일 KST 08:00 (일~토) |
| `weekly_build.yml` | push(`weekly_*.md`) + 수동 | 수동 전용 |
| `cardnews.yml` | `workflow_run` (위 3개 완료 후) | 자동 체인 |
