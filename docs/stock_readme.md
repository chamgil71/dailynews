# 📊 주식시황 브리핑 — README

> 매일 장 마감 후 국내외 시장 데이터 수집 → AI 분석 → MD 저장 → 이메일 + 사이트  
> **두 경로 병행: Claude Code 루틴 (주) + GitHub Actions 자동화 (백업)**

---

## 시스템 개요

| 항목 | Primary (루틴) | Backup (자동화) |
|------|----------------|-----------------|
| 실행 방법 | Claude Code 웹 루틴 | GitHub Actions 정기 실행 |
| 데이터 수집 | PlayMCP UsStockInfo + NaverSearch | yfinance 라이브러리 |
| AI 분석 | Claude (웹 구독, API 키 불필요) | Gemini API |
| Notion 등록 | GitHub Actions에 위임 | GitHub Actions |
| 이메일 발송 | GitHub Actions (익일 08:00 KST) | GitHub Actions (익일 08:00 KST) |
| HTML 빌드 | GitHub Actions (push 트리거) | GitHub Actions |
| 트리거 | MD 파일 push → Actions 자동 실행 | cron: 평일 KST 23:00 |

---

## 워크플로우 아키텍처 (3단계 분리)

```
[1단계 — Claude Code 웹 루틴] 매일 KST 21:25
  루틴 프롬프트 (docs/stock_routine_prompt_v5.md)
       │
       ├─ Step 1: UsStockInfo.get_stock_info → 지수·환율·금리·유가 (8개)
       ├─ Step 2: get_historical_stock_prices → 섹터 대표 종목 (7개, 1일치)
       ├─ Step 3: NaverSearch.search_news → 국내 뉴스 헤드라인
       ├─ Step 4: Claude 분석 (핵심요약·온도계·키워드·섹터·리스크)
       ├─ Step 5: Write → reports/stock/stock_YYYY-MM-DD.md 저장
       └─ Step 6: git push → stock_build.yml 자동 트리거

[2단계 — GitHub Actions: stock_build.yml]
  push 트리거 (즉시) 또는 backup cron KST 23:00
       │
       ├─ update_history.py → 티커 이력 업데이트
       ├─ build_stock_site.py → HTML 빌드
       ├─ build_site.py → 뉴스 사이트도 재빌드
       └─ git commit + GitHub Pages 배포

[3단계 — GitHub Actions: stock_send.yml]
  매일 KST 08:00 (익일 아침)
       │
       ├─ 최신 MD 자동 감지 (3일 이내)
       ├─ send_stock_email.py → 이메일 발송 (품질 게이트 포함)
       ├─ sync_notion.py → Notion 주식시황 DB 동기화
       └─ [예정] send_stock_telegram.py → 텔레그램 발송
```

---

## Claude Code 루틴 설정

### 루틴 프롬프트

`docs/stock_routine_prompt_v5.md` 내용을 Claude Code 웹 루틴에 붙여넣기.

### 실행 조건

- KST 21:25 예약 실행 (장 마감 약 6시간 후)
- MCP 서버 활성화 필요: `UsStockInfo`, `NaverSearch`
- Notion MCP는 불필요 (GitHub Actions에서 처리)

### 루틴 완료 후 자동 처리

git push 후 GitHub Actions가 순서대로:

1. **즉시** — stock_build.yml: HTML 빌드 + Pages 배포
2. **익일 08:00** — stock_send.yml: 이메일 + Notion + 텔레그램

---

## GitHub Actions 설정

### Secrets 등록

```
Repository → Settings → Secrets and variables → Actions
```

| Secret | 용도 | 필수 |
|--------|------|------|
| `GMAIL_USER` | 이메일 발송 | ✅ |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 | ✅ |
| `RECIPIENT_EMAILS` | 수신자 목록 (콤마 구분) | ✅ |
| `NOTION_API_KEY` | Notion 동기화 | ✅ |
| `NOTION_DATABASE_ID_STOCK` | Notion 주식시황 DB ID | ✅ |
| `SITE_BASE_URL` | GitHub Pages URL | 권장 |
| `LLM_PROVIDER` | 백업 경로 LLM (gemini) | 백업용 |
| `GEMINI_API_KEY` | 백업 경로 분석 | 백업용 |
| `NAVER_CLIENT_ID` | 네이버 뉴스 API | 백업용 |
| `NAVER_CLIENT_SECRET` | 네이버 뉴스 API | 백업용 |
| `TELEGRAM_BOT_TOKEN` | 텔레그램 발송 (향후) | 예정 |
| `TELEGRAM_CHAT_ID` | 텔레그램 채널 (향후) | 예정 |

### 워크플로우 파일

| 파일 | 역할 | 트리거 |
|------|------|--------|
| `stock_build.yml` | 빌드 + Pages 배포 | push(즉시) / cron KST 23:00 |
| `stock_send.yml` | 이메일·Notion·텔레그램 | cron KST 08:00 / 수동 |

---

## 품질 게이트

`send_stock_email.py`는 발송 전 MD 분석 품질을 자동 검증합니다:

- `## ■ 핵심 요약` 섹션 내용이 10자 이상
- `## 시장 온도계` 근거 문장이 5자 이상

위 조건 미충족 시 이메일 발송을 차단하고 경고 로그를 남깁니다.

---

## 리포트 구조 (`reports/stock/stock_YYYY-MM-DD.md`)

```
# 📊 일일 주식 시황 브리핑 — YYYY-MM-DD
## ■ 핵심 요약 (3줄)
## 1. 주요 지수·매크로  (표)
## 2. 섹터 동향  (표)
## 3. 핵심 키워드 TOP 5
## 4. 주목 섹터
## 5. 리스크 요인
## 6. 장기투자 관점
## 시장 온도계: 🔴/🟠/🟡/🟢/🔵
## 참고 뉴스
```

---

## 수동 재발송

특정 날짜 리포트를 다시 발송하려면:

1. GitHub → Actions → **Stock Briefing Send**
2. **Run workflow** 클릭
3. `date` 입력란에 `2026-06-03` 형식으로 입력

---

## 관련 문서

- [루틴 프롬프트 v5](stock_routine_prompt_v5.md) — Claude Code 루틴에 붙여넣기할 전체 프롬프트
- [개발자 가이드](stock_guide.md) — 코드 구조, 유지보수, 확장
- [작업 로그](worklog.md) — 개발 이력 및 변경사항
- [통합 README](../README.md) — 뉴스 + 주식시황 전체 개요
