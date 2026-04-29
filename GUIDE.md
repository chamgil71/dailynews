# AI News Daily — 개발자 가이드

> 이 문서는 **코드 구조 이해, 로직 흐름, 유지보수, 확장** 을 위한 개발자 참조 문서입니다.  
> 초기 실행 방법은 `README.md`를 먼저 보세요.

---

## 목차

1. [전체 로직 흐름](#1-전체-로직-흐름)
2. [수집 단계 (collector.py)](#2-수집-단계-collectorpy)
3. [AI 분석 단계 (analyzer.py)](#3-ai-분석-단계-analyzerpy)
4. [리포트 생성 (report.py)](#4-리포트-생성-reportpy)
5. [RSS 소스 관리](#5-rss-소스-관리)
6. [프롬프트 관리 (config/prompts.py)](#6-프롬프트-관리-configpromptspy)
7. [감시 키워드 관리 (config/keywords.py)](#7-감시-키워드-관리-configkeywordspy)
8. [설정 파라미터 조정 (settings.py)](#8-설정-파라미터-조정-settingspy)
9. [LLM 교체 및 추가](#9-llm-교체-및-추가)
10. [웹사이트 빌드 및 배포](#10-웹사이트-빌드-및-배포)
11. [유지보수 체크리스트](#11-유지보수-체크리스트)
12. [자주 발생하는 문제](#12-자주-발생하는-문제)
13. [모듈별 단독 실행 (디버깅)](#13-모듈별-단독-실행-디버깅)
14. [확장 포인트](#14-확장-포인트)

---

## 1. 전체 로직 흐름

### 실행 순서 (`main.py`)

```
python main.py
     │
     ▼  Step 1
collector.collect_news()
     │  ├─ 모든 RSS URL 전부 수집 (중단 없음)
     │  ├─ 전일 캐시로 중복 URL 제거
     │  ├─ 감시 키워드 포함 기사 → keyword_news 분리
     │  ├─ 언어 분리: en_news / ko_news (키워드 기사 제외)
     │  └─ AI 전송용 trimmed (최대 40건, 영60:한40 비율) 생성
     │
     ▼  Step 2
analyzer.analyze(news_data)
     │  ├─ 영어 뉴스 → _build_prompt("en") → AI 호출 → en 결과 (영문)
     │  ├─ 한국어 뉴스 → _build_prompt("ko") → AI 호출 → ko 결과 (한국어)
     │  └─ _merge(en, ko) → combined
     │
     ▼  Step 3
report.generate() + report.save_report()
     │  └─ Jinja2 템플릿 렌더링 → reports/news_YYYY-MM-DD.md
     │
     ▼  Step 4
db.append_news()
     │  └─ storage/news_db.xlsx 에 날짜 태그와 함께 누적 저장 (키워드 기사 포함)
     │
     ▼  Step 5
mailer.send_email()
     └─ Resend API → RECIPIENT_EMAIL 수신자에게 HTML 메일 발송
```

### 핵심 질문 답변

#### Q. 영어/한국어가 합쳐서 분석되나, 따로 되나?

**따로 분석됩니다 — AI 호출이 2번 발생합니다.**

- 영어 뉴스 전체 → AI 1회 호출 → **영문** 결과
- 한국어 뉴스 전체 → AI 1회 호출 → **한국어** 결과 (프롬프트에 `반드시 한국어로 답변하세요` 명시)
- 리포트에는 두 결과가 `---` 구분선으로 합쳐져서 들어감

#### Q. AI는 전체를 한번에? 카테고리별? 많이 등장한 것만?

**전체를 언어별로 한번에 분석합니다.** 카테고리는 프롬프트 힌트 조정에만 사용됩니다.

- 수집된 기사의 카테고리 빈도 Top 2를 추출 → 해당 카테고리 분석 힌트를 프롬프트에 자동 추가
- 기사 제목 + 요약을 한번에 전달 → AI가 자체 판단으로 Top 3 이슈 선정

#### Q. 수집 중 50개 채워지면 중단?

**아닙니다.** 모든 RSS URL을 끝까지 수집하고, AI 전달용 개수(`MAX_TITLES_TO_ANALYZE=40`)만 나중에 잘라냅니다.

```python
en_cap  = min(len(en_news), int(40 * 0.6))   # 최대 24건
ko_cap  = min(len(ko_news), 40 - en_cap)       # 최대 16건
trimmed = en_news[:en_cap] + ko_news[:ko_cap]  # AI에 전달
```

#### Q. 키워드 기사는?

| 대상 | AI 분석 | xlsx DB | 리포트 |
|------|---------|---------|--------|
| 일반 기사 | ✅ | ✅ | 전체 목록 섹션 |
| 키워드 기사 | ❌ 제외 | ✅ 포함 | 별도 키워드 섹션 |

---

## 2. 수집 단계 (collector.py)

### 동작 상세

```
1. _load_cache()     → .cache/last_urls.json 에서 전일 URL 로드 (TTL 23시간)
2. for category in RSS_FEEDS:
     for url in meta["feeds"]:
         _fetch_feed(url, ...)   → feedparser.parse(url)
         결과: 피드당 최대 MAX_ENTRIES_PER_FEED(=8)건
         seen_urls에 이미 있는 URL은 skip
3. _matches_keywords() 로 감시 키워드 기사 분리 → keyword_news
4. 키워드 기사 제외 후 en/ko 분리
5. trimmed 슬라이스 생성
6. _save_cache()     → 신규 URL을 .cache/last_urls.json에 추가
```

### 중복 제거 2단계

| 단계 | 범위 | 방법 |
|------|------|------|
| 세션 내 | 현재 실행 중 | `seen_urls` set — 같은 URL이 여러 피드에 있으면 첫 번째만 수집 |
| 전일 캐시 | 23시간 이내 | `.cache/last_urls.json` — 어제 수집한 기사 재수집 방지 |

### 수집 데이터 구조

```python
{
    "category":  "technology",
    "label":     "글로벌 기술",
    "lang":      "en",           # "en" | "ko"
    "title":     "기사 제목",
    "link":      "https://...",  # 중복 제거 기준 키
    "published": "Tue, 09 Apr 2026 ...",
    "summary":   "첫 150자 요약...",
}
```

### collect_news() 반환 구조

```python
{
    "en":      [...],   # 영어 기사 (키워드 기사 제외)
    "ko":      [...],   # 한국어 기사 (키워드 기사 제외)
    "all":     [...],   # 전체 (키워드 기사 포함)
    "keyword": [...],   # 감시 키워드 매칭 기사
    "trim":    [...],   # AI 분석용 (영60:한40 비율로 최대 40건)
    "stats": {
        "total":           int,
        "en":              int,
        "ko":              int,
        "keyword_matches": int,
        "sent_to_ai":      int,
        "skipped_dup":     int,
    }
}
```

---

## 3. AI 분석 단계 (analyzer.py)

### 전략 패턴 구조

```
analyze(news_data)
    └─ get_analyzer()          → LLM_PROVIDER 환경변수 기준
         ├─ "gemini" → GeminiAnalyzer (현재 기본값)
         ├─ "claude" → ClaudeAnalyzer
         └─ "gpt"    → GPTAnalyzer
              └─ analyze_by_lang(en_news, ko_news)
```

### 모델 자동 선택 (mini / full)

뉴스 건수에 따라 저렴한 모델과 고품질 모델을 자동으로 전환합니다.

| LLM | 기준 건수 | 적은 경우 | 많은 경우 |
|-----|-----------|-----------|-----------|
| GPT | ≤ 20건 | gpt-4o-mini | gpt-4o |
| Claude | ≤ 20건 | claude-haiku-4-5 | claude-opus-4-5 |
| Gemini | ≤ 40건 | flash-lite-preview | flash-lite-preview |

### AI 실패 시 폴백

API 오류 발생 시 원문 제목 15건 목록을 리포트에 삽입합니다. 파이프라인은 중단 없이 계속 실행됩니다.

---

## 4. 리포트 생성 (report.py)

### 템플릿 위치

```
templates/daily_report.md     ← Jinja2 템플릿
```

### 템플릿 변수

| 변수 | 내용 |
|------|------|
| `date` | 생성 일시 (YYYY-MM-DD HH:MM KST) |
| `analysis_en` | 영어 뉴스 AI 분석 결과 (영문) |
| `analysis_ko` | 한국어 뉴스 AI 분석 결과 (한국어) |
| `combined` | `analysis_en` + `analysis_ko` 합본 |
| `news_en` | 수집된 영어 기사 리스트 |
| `news_ko` | 수집된 한국어 기사 리스트 |
| `keyword_news` | 감시 키워드 매칭 기사 리스트 |
| `stats` | `{total, en, ko, keyword_matches, sent_to_ai, skipped_dup}` |

### 리포트 섹션 구조

```
> 📅 생성일시 / 📊 수집 통계

AI 분석 결과 (영어 + 한국어)

🔍 키워드 매칭 기사 (있을 때만 표시)

📋 수집 기사 전체 목록
  🌐 영어 뉴스
  🇰🇷 한국어 뉴스
```

### 저장 경로

```
reports/news_YYYY-MM-DD.md     ← 날짜별 파일 (같은 날 재실행 시 덮어씀)
```

---

## 5. RSS 소스 관리

### 소스 활성화/비활성화

`config/rss_sources.py`에서 주석만 조작합니다.

```python
RSS_FEEDS = {
    **KO_ECONOMY,          # 활성화
    **KO_TECH,             # 활성화
    **EN_TECH,             # 활성화
    **EN_AI,               # 활성화
    # **KO_GENERAL,        # 비활성화
}
```

### 현재 활성화된 소스 (2026-04-29 기준)

| 카테고리 키 | 레이블 | 언어 | 피드 수 |
|-------------|--------|------|---------|
| `korean_economy` | 국내 경제 | ko | 5개 |
| `korean_tech` | 국내 IT·기술 | ko | 7개 |
| `technology` | 글로벌 기술 | en | 6개 |
| `ai_ml` | AI·ML | en | 8개 |

### 새 카테고리 추가 절차

1. `config/sources/en_news.py` 또는 `ko_news.py`에 카테고리 dict 정의
2. `config/rss_sources.py`에 import 및 `RSS_FEEDS`에 추가
3. `config/prompts.py`의 `CATEGORY_PROMPTS`에 분석 힌트 추가

### 피드 URL 확인

```bash
python -c "
import feedparser
f = feedparser.parse('https://feeds.arstechnica.com/arstechnica/index')
print(f'entries: {len(f.entries)}')
for e in f.entries[:3]: print(' -', e.title[:60])
"
```

---

## 6. 프롬프트 관리 (config/prompts.py)

프롬프트는 로직 파일(`analyzer.py`)과 분리되어 있습니다. 분석 방향이나 출력 형식 변경 시 이 파일만 수정합니다.

### 구성 요소

| 항목 | 역할 |
|------|------|
| `CATEGORY_PROMPTS` | 카테고리별 분석 힌트 문구 (수집 기사 Top 2 카테고리 자동 적용) |
| `DEFAULT_PROMPT_HINT` | 카테고리 매칭 없을 때 기본 힌트 |
| `PROMPT_TEMPLATE_KO` | 한국어 뉴스용 프롬프트 템플릿 |
| `PROMPT_TEMPLATE_EN` | 영어 뉴스용 프롬프트 템플릿 |

### 템플릿 자리표시자

```
{hints}       ← 카테고리 힌트 (자동 삽입)
{title_block} ← 기사 제목+요약 목록 (자동 삽입)
```

### 출력 형식 변경 예시

Top 3를 Top 5로 늘리려면:

```python
# PROMPT_TEMPLATE_KO 수정
## 핵심 이슈 TOP 5
1. ...
2. ...
...
5. ...
```

### 새 카테고리 힌트 추가

```python
CATEGORY_PROMPTS: dict[str, str] = {
    ...
    "security": "사이버 위협, 취약점, 보안 사고 및 대응 동향 중심으로 분석하세요.",
}
```

`rss_sources.py`의 카테고리 키와 동일하게 맞춰야 합니다.

---

## 7. 감시 키워드 관리 (config/keywords.py)

특정 조직명, 기관명, 제품명 등의 키워드를 포함한 기사를 AI 분석에서 제외하고 리포트 별도 섹션에 모읍니다.

### 현재 설정

```python
WATCH_KEYWORDS: list[str] = [
    "정보통신산업진흥원",
    "nipa",
    "과학기술정보통신부",
    "과기정통부",
]
```

### 동작 방식

- 기사 **제목 + 요약** 전체에서 검색 (대소문자 무시)
- 매칭 기사는 `keyword_news` 버킷으로 분리
- `en_news`, `ko_news`, `trim`에서 제외 → AI 분석 안 됨
- `all_news`에는 유지 → xlsx DB에는 정상 저장됨
- 리포트에 `🔍 키워드 매칭 기사` 섹션으로 표시 (매칭 기사 없으면 섹션 숨김)

### 키워드 추가

```python
WATCH_KEYWORDS: list[str] = [
    "정보통신산업진흥원",
    "nipa",
    "과학기술정보통신부",
    "과기정통부",
    "새로운키워드",   # ← 여기에 추가
]
```

---

## 8. 설정 파라미터 조정 (settings.py)

### 수집량 조정

```python
MAX_ENTRIES_PER_FEED    = 8    # 피드 1개당 최대 수집 건수
MAX_TITLES_TO_ANALYZE   = 40   # AI에 전달하는 최대 기사 수
RSS_TIMEOUT_SECONDS     = 10   # 피드 요청 타임아웃 (초)
```

### 캐시 설정

```python
CACHE_ENABLED   = True
CACHE_FILE      = ".cache/last_urls.json"
CACHE_TTL_HOURS = 23    # 23시간 = 매일 실행 시 전날 기사 제외
```

캐시 초기화:
```bash
# Windows
del .cache\last_urls.json
```

### LLM 모델 교체

```python
# Gemini 안정 버전으로 교체 예시
GEMINI_MODEL_FULL = "gemini-2.0-flash"
GEMINI_MODEL_MINI = "gemini-1.5-flash-8b"
```

---

## 9. LLM 교체 및 추가

### 환경변수만으로 교체

```bash
# .env 파일
LLM_PROVIDER=claude          # gemini | claude | gpt
ANTHROPIC_API_KEY=sk-ant-...
```

### 새 LLM Analyzer 추가

`core/analyzer.py`에서 `BaseAnalyzer` 상속:

```python
class MyAnalyzer(BaseAnalyzer):
    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": ""}
        if en_news:
            try:
                results["en"] = self._call_api(_build_prompt(en_news, "en"))
            except Exception as e:
                results["en"] = _fallback_summary(en_news, "en")
        if ko_news:
            try:
                results["ko"] = self._call_api(_build_prompt(ko_news, "ko"))
            except Exception as e:
                results["ko"] = _fallback_summary(ko_news, "ko")
        results["combined"] = _merge(results["en"], results["ko"])
        return results
```

`get_analyzer()`에 분기 추가 후 `settings.py`에 관련 설정 추가.

---

## 10. 웹사이트 빌드 및 배포

### 폴더 구조

```
publish/          ← 빌드 결과물 (GitHub Pages / Vercel 서빙)
  index.html      ← 최신 리포트
  archive.html    ← 전체 목록
  app.html        ← 동적 웹앱 (검색·필터)
  reports.json    ← 날짜 인덱스
  reports-data.json ← 전체 리포트 데이터 (app.html용)
  YYYY-MM-DD.html ← 날짜별 리포트

docs/             ← 프로젝트 문서 (소스 관리)
  google-sheets-setup.md
  ...
```

### 로컬 빌드 및 미리보기

```bash
python scripts/build_site.py
cd publish && python -m http.server 8000
# http://localhost:8000
```

### GitHub Pages 설정 (최초 1회)

```
Repository → Settings → Pages
→ Source: GitHub Actions   ← 반드시 이 옵션 선택
```

> 기존에 "Deploy from a branch → /docs"로 설정했다면 "GitHub Actions"로 변경 필요.  
> 변경 후 다음 Actions 실행부터 `publish/` 폴더가 자동 배포됩니다.

### GitHub Actions 워크플로우 구조

```yaml
1. 뉴스 수집 및 리포트 생성 (python main.py)
2. 사이트 빌드 (python scripts/build_site.py)
3. reports/ publish/ storage/ 커밋 & 푸시
4. publish/ → GitHub Pages 배포 (actions/upload-pages-artifact)
5. actions/deploy-pages 실행
```

### Vercel

`vercel.json`이 `publish/` 폴더를 서빙하도록 설정되어 있습니다.

```bash
vercel --prod   # 루트에서 실행
```

---

## 11. 유지보수 체크리스트

### 정기 점검 (월 1회)

- [ ] **RSS 피드 상태 확인** — 응답 없는 URL 제거 또는 교체
- [ ] **캐시 파일 크기 확인** — `.cache/last_urls.json` 과도하게 커지면 정리
- [ ] **reports/ 폴더 정리** — 30일 이상된 MD 파일 아카이브 또는 삭제
- [ ] **storage/news_db.xlsx 백업** — 외부 백업
- [ ] **API 비용 확인** — 사용 중인 LLM 대시보드에서 청구 확인
- [ ] **Gemini 모델명 확인** — preview 모델은 주기적으로 서비스 종료될 수 있음

### RSS 피드 장애 대응

로그 패턴:
```
[RSS 오류] https://... — <exception>
[피드 실패] https://...: <exception>
```

장애가 지속되는 URL은 `ko_news.py` 또는 `en_news.py`에서 주석 처리합니다.

### 캐시 초기화 (재수집 필요 시)

```bash
del .cache\last_urls.json   # Windows
rm .cache/last_urls.json    # Mac/Linux
```

---

## 12. 자주 발생하는 문제

### 수집된 뉴스가 0건

1. 전체 RSS 피드 오프라인 → 네트워크 확인
2. 캐시에 이미 수집된 URL만 있음 → 캐시 삭제 후 재실행
3. `RSS_TIMEOUT_SECONDS`가 너무 짧음 → `settings.py`에서 20으로 증가

### AI 분석 실패 (fallback 출력)

1. API 키 미설정 → `.env` 파일 확인
2. API 키 만료 또는 한도 초과 → LLM 대시보드 확인
3. Gemini preview 모델 서비스 종료 → `settings.py`에서 안정 버전으로 교체

```python
GEMINI_MODEL_FULL = "gemini-2.0-flash"
GEMINI_MODEL_MINI = "gemini-1.5-flash-8b"
```

### Gemini `thought_signature` 오류

2.0 계열 모델 사용 시 발생할 수 있습니다. `analyzer.py`의 `GeminiAnalyzer._call()`에서 해당 파라미터 블록을 주석 처리하세요.

### GitHub Pages 배포 안 됨

1. Pages 소스가 "Deploy from a branch"로 설정되어 있음  
   → Settings → Pages → Source를 **GitHub Actions**로 변경
2. 워크플로우 `permissions`에 `pages: write`, `id-token: write` 없음  
   → `news.yml` 상단의 permissions 블록 확인

### 이메일 발송 실패

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from core.mailer import send_email
import glob
files = sorted(glob.glob('reports/*.md'))
with open(files[-1], encoding='utf-8') as f: md = f.read()
print('결과:', '성공' if send_email(md) else '실패')
"
```

---

## 13. 모듈별 단독 실행 (디버깅)

### RSS 수집만 테스트

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from core.collector import collect_news
r = collect_news()
print('통계:', r['stats'])
print('키워드 매칭:', [n['title'][:40] for n in r['keyword']])
"
```

### 사용 가능한 Gemini 모델 목록

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from google import genai
from config.settings import GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)
for m in client.models.list(): print(m.name)
"
```

### Gemini 모델 동작 테스트

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from google import genai
from config.settings import GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)
r = client.models.generate_content(model='gemini-2.0-flash-lite', contents='한 문장으로 답해주세요.')
print(r.text)
"
```

### 이메일만 단독 발송

```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
from core.mailer import send_email
import glob
files = sorted(glob.glob('reports/*.md'))
if not files: print('리포트 없음'); exit()
with open(files[-1], encoding='utf-8') as f: md = f.read()
print('파일:', files[-1])
print('결과:', '성공' if send_email(md) else '실패')
"
```

### 사이트 빌드만 실행

```bash
python scripts/build_site.py
cd publish && python -m http.server 8000
```

---

## 14. 확장 포인트

### Slack / Discord 알림

```python
# core/notifier.py
import os, requests

def send_slack(md_content: str) -> bool:
    webhook = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook: return False
    r = requests.post(webhook, json={"text": md_content[:500] + "\n..."})
    return r.status_code == 200
```

### 주간 요약 리포트

```python
from datetime import datetime
if datetime.now().weekday() == 0:   # 월요일
    from core.weekly import generate_weekly
    generate_weekly()
```

### 기사 중요도 스코어링

```python
from collections import Counter
title_words = [w for n in all_news for w in n["title"].split()]
freq = Counter(title_words)
for n in all_news:
    n["score"] = sum(freq[w] for w in n["title"].split())
all_news.sort(key=lambda x: x["score"], reverse=True)
```

---

## 파일 구조 요약

```
dailynews/
├── main.py                          실행 진입점 (5단계 순서 실행)
├── config/
│   ├── settings.py                  전체 설정 (모델, 수집량, 이메일)
│   ├── rss_sources.py               활성 소스 조합 (주석/해제로 제어)
│   ├── prompts.py                   AI 프롬프트 템플릿 + 카테고리 힌트
│   ├── keywords.py                  감시 키워드 목록
│   └── sources/
│       ├── ko_news.py               한국어 RSS 소스 정의
│       └── en_news.py               영어 RSS 소스 정의
├── core/
│   ├── collector.py                 RSS 수집 + 캐시 + 키워드 분리
│   ├── analyzer.py                  AI 분석 (GPT/Claude/Gemini 전략 패턴)
│   ├── report.py                    Markdown 리포트 생성
│   ├── db.py                        xlsx 누적 저장
│   └── mailer.py                    Resend 이메일 발송
├── scripts/
│   └── build_site.py                MD → HTML 변환 (publish/ 폴더 출력)
├── templates/
│   └── daily_report.md              Jinja2 리포트 템플릿
├── publish/                         빌드 결과물 (GitHub Pages / Vercel)
├── docs/                            프로젝트 문서 (소스 관리용)
├── reports/                         날짜별 MD 리포트 누적
├── storage/
│   └── news_db.xlsx                 전체 기사 누적 DB
├── .cache/
│   └── last_urls.json               전일 URL 캐시 (TTL 23h)
├── .env                             환경변수 (로컬 전용, git 제외)
├── .env.example                     환경변수 샘플 (Gemini 기본값)
├── requirements.txt
├── vercel.json                      Vercel 배포 설정 (publish/ 서빙)
├── README.md                        빠른 시작 가이드
└── GUIDE.md                         이 파일 (개발자 상세 가이드)
```

---

*최종 업데이트: 2026-04-29*
