# 개선 작업 기록

> 최초 작성: 2026-04-29  
> 최종 수정: 2026-04-29

---

## 진행 현황

| # | 작업 | 상태 | 파일 |
|---|------|------|------|
| 1 | 영문 기사 한글 분석 | ✅ 완료 | `config/prompts.py` |
| 2 | RSS 오류 피드 정리 | ✅ 완료 | `config/sources/ko_news.py`, `en_news.py` |
| 3 | 키워드 볼드 하이라이트 | ✅ 완료 | `core/report.py`, `templates/daily_report.md` |
| 4 | 오전/오후 분리 발송 | 🔲 예정 | `rss_sources.py`, `collector.py`, `main.py`, `mailer.py`, `news.yml` |

---

## ✅ 완료된 작업

### 1. 영문 기사 한글 분석 (`config/prompts.py`)

**문제:** `PROMPT_TEMPLATE_EN`이 영어로 답변하도록 지시되어 있어 글로벌 기사 분석 결과가 영문으로 출력됨.

**수정:** 영문 기사도 한국어로 분석·요약하도록 프롬프트 변경.

```python
# 변경 전
PROMPT_TEMPLATE_EN = "You are a professional news analyst... Output format (strictly follow): ## Top 3 Key Issues ..."

# 변경 후
PROMPT_TEMPLATE_EN = "당신은 뉴스 분석 전문가입니다. 아래 영어 뉴스 제목을 분석하세요. ... **반드시 한국어로 답변하세요.**"
```

---

### 2. RSS 오류 피드 정리

#### 2-1. 에러 유형 분류

| 유형 | 설명 |
|------|------|
| **404** | URL 자체가 없음. 서비스 종료 |
| **HTML 반환** | RSS 엔드포인트가 HTML 페이지로 교체됨 |
| **접근 거부** | 봇 차단(403) 또는 방화벽 |

#### 2-2. 피드별 확인 결과

| 피드 | URL | 상태 | 조치 |
|------|-----|------|------|
| ZDNet Korea | `zdnet.co.kr/rss/?t=a` | 404 | ❌ 제거 |
| ITWorld Korea | `itworld.co.kr/rss/feed` | 404 | ❌ 제거 |
| 인공지능신문 | `aitimes.kr/rss/all.xml` | 404 | ❌ 제거 |
| DeepLearning.AI | `deeplearning.ai/the-batch/feed/` | 404 | ❌ 제거 |
| Stanford HAI | `hai.stanford.edu/news/rss.xml` | 404 | ❌ 제거 |
| OECD.AI | `oecd.ai/en/news-and-blog/feed` | 404 | ❌ 제거 |
| 이데일리 | `edaily.co.kr/rss/rss_economy.xml` | HTML 반환 | ❌ 제거 |
| 조선비즈 | `biz.chosun.com/rss/rss.htm` | 봇 차단 | ❌ 제거 |
| 블로터 | `bloter.net/feed` | 404 | 🔄 URL 교체 |
| Wired | `feeds.wired.com/wired/index` | HTML 반환 | ❌ 제거 |
| AI News | `artificialintelligence-news.com/feed/` | 간헐적 오류 → 현재 정상 | ✅ 유지 |

#### 2-3. 적용 내용 (`config/sources/ko_news.py`)

**KO_ECONOMY** — 이데일리·조선비즈 제거, Google News 경제 RSS 추가
```python
feeds: [
    "https://www.hankyung.com/feed/economy",
    "https://www.mk.co.kr/rss/40300001/",
    "https://news.einfomax.co.kr/rss/allArticle.xml",
    # 신규: Google News 경제·금융 (100여 개 매체 집계)
    "https://news.google.com/rss/search?q=%EA%B2%BD%EC%A0%9C+%EA%B8%88%EC%9C%B5&hl=ko&gl=KR&ceid=KR:ko",
]
```

**KO_TECH** — ZDNet·ITWorld·인공지능신문 제거, 블로터 URL 교체, Google News IT·AI 추가
```python
feeds: [
    "https://rss.etnews.com/Section901.xml",
    "https://rss.etnews.com/04046.xml",
    "https://www.aitimes.com/rss/allArticle.xml",
    "https://feeds.feedburner.com/bloter",   # ← URL 교체
    # 신규: Google News IT 종합
    "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ko&gl=KR&ceid=KR:ko",
    # 신규: Google News AI·기술
    "https://news.google.com/rss/search?q=%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5+AI+%EA%B8%B0%EC%88%A0&hl=ko&gl=KR&ceid=KR:ko",
]
```

#### 2-4. 적용 내용 (`config/sources/en_news.py`)

**EN_TECH** — Wired 구 URL 제거, Google News Tech 추가
```python
feeds: [
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://www.technologyreview.com/feed/",
    "https://www.zdnet.com/news/rss.xml",
    # 신규: Google News 글로벌 기술
    "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
]
```

**EN_AI** — DeepLearning.AI·Stanford HAI·OECD 제거, Google News AI 추가
```python
feeds: [
    "https://venturebeat.com/category/ai/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://aiweekly.co/issues.rss",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://www.wired.com/feed/tag/ai/latest/rss",
    # 신규: Google News AI 영문
    "https://news.google.com/rss/search?q=artificial+intelligence+LLM&hl=en-US&gl=US&ceid=US:en",
]
```

#### 2-5. Google News RSS 활용 전략

RSS가 죽은 게 아니라 개별 언론사 관리 부실로 하나씩 깨지는 것.  
**Google News RSS**는 피드 하나에 100여 개 매체를 집계하며 구글 인프라로 안정성이 보장된다.

```
# 키워드 검색형
https://news.google.com/rss/search?q={키워드(URL인코딩)}&hl=ko&gl=KR&ceid=KR:ko

# 주제 분류형
https://news.google.com/rss/headlines/section/topic/{TOPIC}?hl=ko&gl=KR&ceid=KR:ko
# TOPIC: TECHNOLOGY, BUSINESS, SCIENCE, WORLD
```

> **주의:** Google News RSS의 `<link>`는 `news.google.com/rss/articles/...` 리다이렉트 URL.  
> 현 시스템은 링크를 중복 제거 키·DB 저장에만 쓰므로 별도 처리 불필요.

#### 2-6. 피드 수 변화

| | 수정 전 | 수정 후 |
|-|--------|--------|
| 활성 피드 수 | 29개 | 26개 |
| 오류 발생 피드 | 11개/일 | 0~1개/일 (예상) |
| 수집 성공률 | ~65% | ~95% (예상) |

---

### 3. 키워드 볼드 하이라이트

**문제:** 키워드 매칭 기사 섹션에서 어떤 단어가 매칭됐는지 본문에서 식별 불가.

**수정 파일:**
- `core/report.py` — `_highlight()` 함수 추가, Jinja2 커스텀 필터로 등록
- `templates/daily_report.md` — 키워드 섹션에 `| highlight` 필터 적용

**`core/report.py`**
```python
def _highlight(text: str) -> str:
    """감시 키워드를 **bold** 처리."""
    for kw in WATCH_KEYWORDS:
        text = re.sub(re.escape(kw), f"**{kw}**", text, flags=re.IGNORECASE)
    return text

# generate() 내부에서 Jinja2 Environment에 필터 등록
env = Environment(loader=BaseLoader())
env.filters["highlight"] = _highlight
```

**`templates/daily_report.md`**
```jinja
{% for n in keyword_news %}
- **[{{ n.label }}]** [{{ n.title | highlight }}]({{ n.link }})
  > {{ n.summary | highlight }}
{% endfor %}
```

**결과:** 제목·요약에서 키워드(`정보통신산업진흥원`, `NIPA` 등)가 **굵게** 표시됨.  
이메일 HTML에서는 `<strong>`, 웹사이트에서도 동일 적용.

---

## 🔲 예정 작업: 오전/오후 분리 발송

### 목표

| 에디션 | 발송 시각 (KST) | UTC cron | 카테고리 |
|--------|--------------|----------|---------|
| 🌅 오전판 | 08:00 | `0 23 * * *` | 국내 종합 + 국내 경제 + 증권·투자 |
| 💻 오후판 | 14:00 | `0 5 * * *` | 국내 IT·기술 + 글로벌 기술 + AI·ML |

### 수정 대상 파일

| 파일 | 변경 내용 |
|------|---------|
| `config/rss_sources.py` | `MORNING_FEEDS` / `AFTERNOON_FEEDS` dict 추가 |
| `config/settings.py` | 에디션별 이메일 제목 상수 추가 |
| `core/collector.py` | `collect_news(feeds=None)` 파라미터 추가 |
| `main.py` | `--edition morning\|afternoon` argparse 추가 |
| `core/mailer.py` | `send_email(md, subject=None)` 파라미터 추가 |
| `.github/workflows/news.yml` | 이중 cron + 에디션 결정 로직으로 교체 |

### 주요 변경 내용 (미리보기)

**`config/rss_sources.py`**
```python
from config.sources.ko_news import KO_GENERAL, KO_ECONOMY, KO_STOCK, KO_TECH
from config.sources.en_news import EN_TECH, EN_AI

MORNING_FEEDS = {**KO_GENERAL, **KO_ECONOMY, **KO_STOCK}
AFTERNOON_FEEDS = {**KO_TECH, **EN_TECH, **EN_AI}
RSS_FEEDS = {**MORNING_FEEDS, **AFTERNOON_FEEDS}  # 하위 호환
```

**`.github/workflows/news.yml`**
```yaml
on:
  schedule:
    - cron: '0 23 * * *'   # KST 08:00 오전판
    - cron: '0 5 * * *'    # KST 14:00 오후판
  workflow_dispatch:
    inputs:
      edition:
        description: 'morning 또는 afternoon'
        required: true
        default: morning
```

---

## 전체 요약

| 항목 | 개선 전 | 개선 후 (완료분) | 개선 후 (예정 포함) |
|------|--------|----------------|-----------------|
| 영문 분석 언어 | 영어 | **한국어** | 한국어 |
| 오류 피드 수 | 11개/일 | **0~1개/일** | 0~1개/일 |
| 활성 피드 수 | 29개 | **26개** | 26개 |
| 키워드 표시 | 별도 섹션만 | **볼드 하이라이트** | 볼드 하이라이트 |
| 발송 횟수 | 1회/일 (11시) | 1회/일 | **2회/일 (8시, 14시)** |
| 에디션 구분 | 단일 종합 | 단일 종합 | **경제판 / IT판** |
