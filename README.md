# 📰 AI News Daily

> RSS 뉴스 자동 수집 → AI 분석 → Markdown 리포트 → 웹사이트 + 이메일 발송  
> **서버 불필요 · 완전 자동화 · 월 $1 미만**

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [전체 워크플로우](#2-전체-워크플로우)
3. [파일 구조](#3-파일-구조)
4. [로컬에서 실행하기](#4-로컬에서-실행하기)
5. [GitHub Actions 자동화](#5-github-actions-자동화)
6. [웹사이트 공개](#6-웹사이트-공개)
7. [LLM 교체 방법](#7-llm-교체-방법)
8. [비용 정리](#8-비용-정리)
9. [확장 로드맵](#9-확장-로드맵)

---

## 1. 시스템 개요

| 항목 | 내용 |
|------|------|
| 뉴스 수집 | RSS (영어 4카테고리 + 한국어 2카테고리) |
| AI 분석 | OpenAI GPT (기본) / Claude / Gemini 교체 가능 |
| 리포트 형식 | Markdown (.md) — Obsidian 바로 사용 가능 |
| 웹사이트 | GitHub Pages (정적) 또는 Vercel (동적 검색·필터) |
| 이메일 | Resend API — 무료 100건/일 |
| 자동 실행 | GitHub Actions cron — 매일 오전 8시 KST |
| 서버 | **불필요** (완전 서버리스) |

---

## 2. 전체 워크플로우

### 데이터 흐름

```
트리거 (매일 08:00 KST / 수동 실행)
        │
        ▼
┌───────────────────────────────────────────────────┐
│  collector.py — RSS 수집                          │
│                                                   │
│  영어 소스 4개  ──┐                               │
│  한국어 소스 2개 ──┼──→ 중복 제거 (전일 캐시)      │
│  타임아웃 10초   ──┘     언어 분리 (en / ko)       │
│                          최대 35건으로 토큰 제한    │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  analyzer.py — AI 분석                            │
│                                                   │
│  영어 뉴스  ──→ 카테고리별 맞춤 프롬프트            │
│  한국어 뉴스 ──→ 언어별 분리 분석                  │
│                                                   │
│  뉴스 ≤ 20건 → gpt-4o-mini  (비용 절감)           │
│  뉴스 > 20건 → gpt-4o       (품질 우선)           │
│  실패 시    → 원문 제목 목록 폴백                  │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  report.py — Markdown 생성                        │
│                                                   │
│  Jinja2 템플릿 렌더링                             │
│  → reports/news_2026-03-09.md  (날짜별 저장)      │
└──────────────┬────────────────┬───────────────────┘
               │                │
               ▼                ▼
┌──────────────────┐  ┌────────────────────┐
│  build_site.py   │  │  mailer.py         │
│  MD → HTML 변환  │  │  Resend API 발송   │
│  docs/*.html     │  │  수신자 이메일      │
└──────────┬───────┘  └────────────────────┘
           │
           ▼
┌───────────────────────────────────────────────────┐
│  Git 커밋 & Push (GitHub Actions 자동)            │
│  reports/ + docs/ 저장                            │
└───────────────────────────────────────────────────┘
```

### 최종 결과물 3가지

```
실행 완료
   │
   ├── 📄 reports/news_2026-03-09.md
   │       Obsidian vault에 드래그 드롭 → 즉시 열람
   │
   ├── 🌐 웹사이트 자동 배포
   │       GitHub Pages → https://[이름].github.io/ai-news-daily/
   │       Vercel       → https://ai-news-daily.vercel.app
   │
   └── 📧 이메일
           RECIPIENT_EMAIL 수신자에게 HTML 메일 자동 발송
```

### LLM 교체 흐름

```
LLM_PROVIDER 환경변수
   │
   ├── gpt    → GPTAnalyzer    (기본값, 조건부 mini/full 자동 선택)
   ├── claude → ClaudeAnalyzer (haiku)
   └── gemini → GeminiAnalyzer (flash/pro)
               │
               ▼
         get_analyzer()가 자동 선택
         → 나머지 코드 변경 없음
```

---

## 3. 파일 구조

```
ai-news-daily/
│
├── main.py                  ← 전체 오케스트레이터 (순서대로 실행)
│
├── config/
│   ├── rss_sources.py       ← RSS URL 목록 (카테고리·언어별)
│   └── settings.py          ← 모델, 토큰 수, 이메일 등 전체 설정
│
├── core/
│   ├── collector.py         ← RSS 수집 + 중복 제거 + 언어 분리
│   ├── analyzer.py          ← GPT/Claude/Gemini 분석 (전략 패턴)
│   ├── report.py            ← MD 파일 생성 + 날짜별 저장
│   └── mailer.py            ← Resend 이메일 발송
│
├── scripts/
│   └── build_site.py        ← MD → HTML 변환 (웹사이트 빌드)
│
├── templates/
│   └── daily_report.md      ← Jinja2 리포트 템플릿
│
├── docs/                    ← 웹사이트 파일 (자동 생성됨)
│   ├── index.html           ← 최신 리포트 홈
│   ├── archive.html         ← 전체 목록
│   ├── app.html             ← 동적 웹앱 (검색·필터)
│   └── reports.json         ← 날짜 인덱스
│
├── reports/                 ← MD 원본 누적 저장
│   └── news_2026-03-09.md
│
├── .cache/
│   └── last_urls.json       ← 전일 URL 캐시 (중복 방지)
│
├── .github/workflows/
│   └── news.yml             ← GitHub Actions 자동 실행 설정
│
├── .env.example             ← 환경변수 샘플
├── .gitignore
├── requirements.txt
└── vercel.json              ← Vercel 배포 설정
```

---

## 4. 로컬에서 실행하기

> ✅ **GitHub 없이 완전히 동작합니다.**  
> 로컬 실행 결과는 `reports/` 폴더에 저장되고 이메일도 발송됩니다.

### 사전 준비

| 필요 항목 | 발급처 | 무료 여부 |
|-----------|--------|-----------|
| Python 3.10 이상 | python.org | ✅ |
| OpenAI API Key | platform.openai.com | 유료 (소량) |
| Resend API Key | resend.com | ✅ 100건/일 |

### Step 1 — 코드 준비

```bash
# ZIP 압축 해제 후 폴더 진입
cd ai-news-daily

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate       # Mac / Linux
venv\Scripts\activate          # Windows
```

### Step 2 — 패키지 설치

```bash
pip install -r requirements.txt
pip install markdown2           # 웹사이트 빌드용 추가 패키지
```

### Step 3 — 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열고 실제 값으로 채웁니다:

```dotenv
OPENAI_API_KEY=sk-...
RESEND_API_KEY=re_...
RECIPIENT_EMAIL=your@email.com

# 선택: LLM 교체
# LLM_PROVIDER=claude
# ANTHROPIC_API_KEY=sk-ant-...
```

### Step 4 — 실행

```bash
python main.py
```

실행 로그 예시:

```
2026-03-09 08:00:01 [INFO] main — AI News Daily 시작
2026-03-09 08:00:06 [INFO] collector — [수집 완료] 총 38건 (EN:28 KO:10) → AI 21건
2026-03-09 08:00:09 [INFO] analyzer — [모델 선택] gpt-4o-mini (뉴스 21건)
2026-03-09 08:00:24 [INFO] report — [리포트 저장] reports/news_2026-03-09.md
2026-03-09 08:00:25 [INFO] mailer — [이메일 발송] 성공
2026-03-09 08:00:25 [INFO] main — 완료! 소요 시간: 24초
```

### Step 5 — 웹사이트 로컬 미리보기 (선택)

```bash
python scripts/build_site.py

cd docs && python -m http.server 8000
# 브라우저에서 http://localhost:8000 열기
```

### 모듈별 단독 실행 (디버깅)

```bash
# RSS 수집만 테스트
python -c "from core.collector import collect_news; r=collect_news(); print(r['stats'])"

# 사이트 빌드만 실행
python scripts/build_site.py
```

### 로컬 자동화 (cron)

**Mac / Linux:**
```bash
crontab -e
# 매일 오전 8시 실행
0 8 * * * cd /path/to/ai-news-daily && /path/to/venv/bin/python main.py
```

**Windows — 작업 스케줄러:**
```
작업 스케줄러 → 기본 작업 만들기
→ 트리거: 매일 08:00
→ 동작: python C:\path\to\ai-news-daily\main.py
```

---

## 5. GitHub Actions 자동화

> ✅ **한 번 설정하면 매일 자동 실행됩니다. 컴퓨터를 켜지 않아도 됩니다.**

### Step 1 — Repository 생성

```
github.com → 우상단 + → New repository
→ 이름: ai-news-daily
→ Public 선택 (Actions 무료 사용)
→ Create repository
```

### Step 2 — Secrets 등록

```
Repository → Settings → Secrets and variables → Actions
→ New repository secret
```

| Secret 이름 | 값 | 필수 |
|-------------|-----|------|
| `OPENAI_API_KEY` | sk-... | ✅ |
| `RESEND_API_KEY` | re_... | ✅ |
| `RECIPIENT_EMAIL` | your@email.com | ✅ |
| `LLM_PROVIDER` | gpt / claude / gemini | 선택 (기본 gpt) |
| `ANTHROPIC_API_KEY` | sk-ant-... | Claude 사용 시 |
| `GEMINI_API_KEY` | AIza... | Gemini 사용 시 |

> ⚠️ `.env` 파일은 로컬 전용입니다. GitHub에는 반드시 Secrets에 등록하세요.

### Step 3 — 코드 업로드

```bash
git clone https://github.com/[이름]/ai-news-daily
# ZIP 압축 해제한 파일들을 복사

git add .
git commit -m "initial commit"
git push
```

### Step 4 — 첫 실행 테스트

```
GitHub → Actions 탭
→ Daily News Report → Run workflow → Run workflow
→ 약 30~60초 후 완료
```

성공 시 확인:
- Actions 탭 → 초록 체크 ✅
- `reports/` 폴더 → MD 파일 생성
- `docs/` 폴더 → HTML 파일 생성
- 이메일 수신 확인

### 실행 시간 변경

```yaml
# .github/workflows/news.yml
schedule:
  - cron: '0 23 * * *'   # 현재: UTC 23:00 = KST 08:00
```

| 원하는 시간 (KST) | cron 값 |
|-------------------|---------|
| 오전 7시 | `0 22 * * *` |
| **오전 8시 (기본)** | `0 23 * * *` |
| 오전 9시 | `0 0 * * *` |
| 오후 6시 | `0 9 * * *` |

### 로컬 vs GitHub Actions 비교

| 항목 | 로컬 실행 | GitHub Actions |
|------|-----------|----------------|
| 설정 난이도 | 쉬움 | 보통 |
| 자동화 | cron 직접 설정 | 자동 (설정 후 방치) |
| 컴퓨터 필요 | ✅ 켜져 있어야 함 | ❌ 불필요 |
| 웹사이트 자동 배포 | 수동 | 자동 커밋·배포 |
| 비용 | $0 | $0 (월 2,000분 무료) |
| 추천 상황 | 테스트·개발 | 실제 운영 |

---

## 6. 웹사이트 공개

### GitHub Pages (정적, 클릭 3번)

```
Repository → Settings → Pages
→ Source: Deploy from a branch
→ Branch: main  /  Folder: /docs  →  Save
```

주소: `https://[이름].github.io/ai-news-daily/`

### Vercel (동적 웹앱, 검색·필터)

```
vercel.com → Add New Project → Import ai-news-daily
→ Framework: Other → Deploy
```

주소: `https://ai-news-daily.vercel.app`

| 항목 | GitHub Pages | Vercel |
|------|--------------|--------|
| 비용 | 무료 | 무료 |
| 검색·필터 | ❌ | ✅ |
| 설정 난이도 | 클릭 3번 | 클릭 5번 |
| 추천 | 빠른 시작 | 기능 활용 |

---

## 7. LLM 교체 방법

### Claude — 코드 수정 없음

```dotenv
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

### Gemini — 코드 3곳 수정

**① requirements.txt:**
```
google-generativeai==0.7.2
```

**② core/analyzer.py — GeminiAnalyzer 추가** (ClaudeAnalyzer 아래):
```python
class GeminiAnalyzer(BaseAnalyzer):
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def _call(self, prompt):
        return self.model.generate_content(prompt).text.strip()

    def analyze_by_lang(self, en_news, ko_news):
        results = {"en": "", "ko": "", "combined": ""}
        if en_news:
            try:    results["en"] = self._call(_build_prompt(en_news, "en"))
            except: results["en"] = _fallback_summary(en_news, "en")
        if ko_news:
            try:    results["ko"] = self._call(_build_prompt(ko_news, "ko"))
            except: results["ko"] = _fallback_summary(ko_news, "ko")
        results["combined"] = _merge(results["en"], results["ko"])
        return results
```

**③ get_analyzer() 수정:**
```python
def get_analyzer():
    provider = LLM_PROVIDER.lower()
    if provider == "claude":  return ClaudeAnalyzer()
    if provider == "gemini":  return GeminiAnalyzer()
    return GPTAnalyzer()
```

**④ 환경변수:**
```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...
```

---

## 8. 비용 정리

| 항목 | 내용 | 월 비용 |
|------|------|---------|
| GitHub Actions | 무료 2,000분/월 | $0 |
| RSS 수집 | feedparser (무료) | $0 |
| Resend 이메일 | 무료 100건/일 | $0 |
| GPT 분석 | gpt-4o-mini 주력 | ~$0.5~1 |
| GitHub Pages / Vercel | 무료 플랜 | $0 |
| **합계** | | **~$0.5~1/월** |

---

## 9. 확장 로드맵

| 단계 | 내용 | 난이도 |
|------|------|--------|
| Phase 1 ✅ | RSS → AI 분석 → MD + 이메일 + 웹사이트 | ⭐ |
| Phase 2 | Slack / Discord 알림 추가 | ⭐ |
| Phase 2 | 주간 트렌드 요약 리포트 | ⭐⭐ |
| Phase 3 | SQLite 아카이브 DB | ⭐⭐ |
| Phase 4 | Vector DB + RAG 뉴스 검색 | ⭐⭐⭐ |
| Phase 4 | 시장·투자 영향 분석 모듈 | ⭐⭐⭐ |

---

 MD 파일만 이메일 발송 테스트
main.py 건드리지 않고 터미널에서 바로 실행하세요.
bashpython -c "
from dotenv import load_dotenv
load_dotenv()
from core.mailer import send_email
with open('reports/news_2026-03-10.md', encoding='utf-8') as f:
    md = f.read()
result = send_email(md)
print('성공' if result else '실패')
"

---

사용가능한 목록 확인
python -c "
from dotenv import load_dotenv
load_dotenv()
from google import genai
from config.settings import GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)
for m in client.models.list():
    print(m.name)
"

모델 작동 테스트
python -c "
from dotenv import load_dotenv
load_dotenv()
from google import genai
from config.settings import GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model='gemini-2.0-flash-lite',
    contents='안녕하세요, 한 문장으로 답해주세요.'
)
print(response.text)
"