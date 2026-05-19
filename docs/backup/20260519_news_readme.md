# 📰 데일리 뉴스 브리핑 — README

> RSS 뉴스 자동 수집 → AI 분석 → Markdown 리포트 → 웹사이트 + 이메일  
> **서버 불필요 · 완전 자동화 · 월 $1 미만**

---

## 시스템 개요

| 항목 | 내용 |
|------|------|
| 뉴스 수집 | RSS (영어 4카테고리 + 한국어 2카테고리) |
| AI 분석 | Gemini (기본) / Claude / GPT 교체 가능 |
| 리포트 형식 | Markdown (.md) — Obsidian 바로 사용 가능 |
| 웹사이트 | GitHub Pages (정적) |
| 이메일 | Gmail SMTP — 수신자별 개별 발송 |
| 자동 실행 | GitHub Actions cron — 매일 오전 8시 KST |
| 서버 | 불필요 (완전 서버리스) |

---

## 전체 워크플로우

```
[GitHub Actions / 로컬 실행]
         │
         ▼
  collector.py — RSS 수집
  (영어 4카테고리 + 한국어 2카테고리)
  중복 제거(전일 캐시) → 언어 분리 → AI 전송용 최대 40건
         │
         ▼
  analyzer.py — AI 분석 (언어별 2회 호출)
  영어 뉴스 → h3 이슈 TOP 3 + 트렌드 키워드 + URL 출처
  한국어 뉴스 → 동일 형식 한국어 출력
         │
         ▼
  report.py — Markdown 리포트 생성
  templates/daily_report.md (Jinja2) → reports/news_YYYY-MM-DD.md
         │
    ┌────┴────┐
    ▼         ▼
mailer.py  build_site.py
이메일 발송  MD → HTML 변환
           publish/*.html + reports-data.json
                 │
                 ▼
          GitHub Pages 자동 배포
```

---

## 빠른 시작

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 편집:

```dotenv
# LLM (기본: Gemini)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...

# 이메일 (Gmail SMTP)
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=앱비밀번호16자리
RECIPIENT_EMAILS=수신자1@gmail.com,수신자2@naver.com

# 사이트
SITE_BASE_URL=https://chamgil71.github.io/dailynews
```

### 3. 로컬 실행

```bash
python main.py
```

### 4. 사이트 빌드 (선택)

```bash
python scripts/build_site.py
```

---

## GitHub Actions 설정

### Secrets 등록

```
Repository → Settings → Secrets and variables → Actions
```

| Secret | 값 |
|--------|----|
| `LLM_PROVIDER` | gemini |
| `GEMINI_API_KEY` | AIza... |
| `GMAIL_USER` | your@gmail.com |
| `GMAIL_APP_PASSWORD` | 앱비밀번호 |
| `RECIPIENT_EMAILS` | email1,email2 |
| `SITE_BASE_URL` | https://chamgil71.github.io/dailynews |
| `SITE_THEME` | classic (또는 minimal/ink/forest) |

### GitHub Pages 설정 (최초 1회)

```
Repository → Settings → Pages → Source: GitHub Actions
```

---

## 테마 선택

| 테마 | 특징 |
|------|------|
| `classic` | Classic Navy (기본) |
| `minimal` | Pretendard, 넓은 여백 |
| `ink` | 신문 스타일, 붉은 accent |
| `forest` | 핀테크 그린, 에메랄드 accent |

```bash
SITE_THEME=minimal python scripts/build_site.py
```

---

## GitHub Secrets 비용

| 항목 | 월 비용 |
|------|---------|
| GitHub Actions | $0 (2,000분/월 무료) |
| Gemini API | $0 (무료 티어, 1일 1회) |
| Gmail SMTP | $0 |
| GitHub Pages | $0 |
| 합계 | $0 |

---

## 관련 문서

- [개발자 가이드](news_guide.md) — 코드 구조, 유지보수, 확장
- [통합 README](../README.md) — 뉴스 + 주식시황 전체 개요
