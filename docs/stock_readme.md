# 📊 주식시황 브리핑 — README

> 매일 장 마감 후 국내외 시장 데이터 수집 → AI 분석 → MD 저장 → 이메일 + 사이트  
> **두 경로 병행: Claude Code 루틴 (주) + GitHub Actions 자동화 (백업)**

---

## 시스템 개요

| 항목 | Primary (루틴) | Backup (자동화) |
|------|----------------|-----------------|
| 실행 방법 | Claude Code 웹 루틴 수동 실행 | GitHub Actions 정기 실행 |
| 데이터 수집 | PlayMCP UsStockInfo + NaverSearch | yfinance 라이브러리 |
| AI 분석 | Claude (웹 구독, API 키 불필요) | Gemini API |
| Notion 등록 | Notion MCP (자동) | 미지원 |
| 이메일 발송 | GitHub Actions에 위임 | GitHub Actions |
| HTML 빌드 | GitHub Actions (push 트리거) | GitHub Actions |
| 트리거 | MD 파일 push → Actions 자동 실행 | cron: 평일 KST 16:45 |

---

## 두 경로 아키텍처

```
[Primary — Claude Code 웹 루틴]
  루틴 프롬프트 (docs/claude_주식시황.md)
       │
       ├─ Step 1: PlayMCP UsStockInfo → 지수/환율/섹터 종목 수집
       ├─ Step 1: NaverSearch → 국내 뉴스 헤드라인
       ├─ Step 2: Read templates/stock_report.md → 형식 확인
       ├─ Step 2: Claude가 리포트 작성
       ├─ Step 3: Write → reports/stock/stock_YYYY-MM-DD.md 저장
       ├─ Step 4: Notion MCP → 주식시황 DB 페이지 생성
       └─ Step 5: git push → GitHub Actions 자동 트리거
                        │
                        ▼
              [GitHub Actions — stock_build.yml]
                  send_stock_email.py → 이메일 발송
                  build_stock_site.py → HTML 빌드
                  build_site.py       → 뉴스 사이트도 재빌드
                  git commit + Pages 배포

[Backup — GitHub Actions 정기 실행]
  cron: 평일 KST 16:45 (UTC 07:45)
       │
       ├─ stock_main.py
       │   ├─ stock_collector.py → yfinance + Naver News API
       │   ├─ stock_analyzer.py  → Gemini 분석
       │   ├─ stock_report.py    → MD 저장
       │   └─ send_stock_email.py → 이메일 발송
       └─ build_stock_site.py → HTML 빌드
```

---

## Claude Code 루틴 사용법

### 루틴 프롬프트 등록

`docs/claude_주식시황.md` 내용을 Claude Code 웹 루틴에 그대로 붙여넣기.

### 실행 조건

- KST 16:30 이후 (장 마감 후) 루틴 실행
- PlayMCP UsStockInfo, NaverSearch, Notion MCP 활성화 상태

### 자동 처리되는 항목

루틴 실행 후 git push가 되면 GitHub Actions가 자동으로:
1. 이메일 발송 (chamgil@gmail.com)
2. HTML 빌드 (publish/stock/)
3. GitHub Pages 배포

---

## GitHub Actions 설정

### Secrets 등록

```
Repository → Settings → Secrets and variables → Actions
```

| Secret | 필수 여부 | 값 |
|--------|-----------|----|
| `GMAIL_USER` | 필수 | Gmail 주소 |
| `GMAIL_APP_PASSWORD` | 필수 | 앱 비밀번호 (16자리) |
| `RECIPIENT_EMAILS` | 필수 | email1,email2 |
| `LLM_PROVIDER` | 백업 경로 | gemini |
| `GEMINI_API_KEY` | 백업 경로 | AIza... |
| `SITE_BASE_URL` | 선택 | GitHub Pages URL |
| `SITE_THEME` | 선택 | classic |
| `NAVER_CLIENT_ID` | 선택 | Naver API 보유 시 |
| `NAVER_CLIENT_SECRET` | 선택 | Naver API 보유 시 |
| `VERCEL_TOKEN` | 필수(배포) | Vercel API Token |
| `VERCEL_ORG_ID` | 필수(배포) | Vercel Org/Team ID |
| `VERCEL_PROJECT_ID` | 필수(배포) | Vercel Project ID |

### 워크플로우 트리거

```yaml
# .github/workflows/stock_build.yml
on:
  push:
    paths: ['reports/stock/**.md']   # Primary: 루틴 push 시 자동
  schedule:
    - cron: '45 07 * * 1-5'          # Backup: 평일 KST 16:45
  workflow_dispatch:
    inputs:
      mode: {build_only | full}       # 수동 테스트용
```

---

## 리포트 구조 (templates/stock_report.md)

```
# 📊 일일 주식 시황 브리핑 — {date}
## ■ 핵심 요약 (3줄)
## 1. 국내 시장 (지수표 + 핵심이슈)
## 2. 글로벌 시장 (지수표 + 매크로)
## 3. 핵심 키워드 TOP 5  ← ① ② ③ ④ ⑤ 마커 고정
## 4. 섹터별 영향 분석 (표)
## 5. 내일 주목 이벤트
## 6. 장기투자 관점 코멘트
## 시장 온도계: 🔴리스크오프 / 🟡중립 / 🟢리스크온
```

---

## 관련 문서

- [루틴 프롬프트](claude_주식시황.md) — Claude Code 루틴에 붙여넣기할 전체 프롬프트
- [개발자 가이드](stock_guide.md) — 코드 구조, 유지보수, 확장
- [통합 README](../README.md) — 뉴스 + 주식시황 전체 개요
