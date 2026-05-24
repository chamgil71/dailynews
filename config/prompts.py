# config/prompts.py
# AI 분석 프롬프트 설정
# - 카테고리 힌트, 출력 형식, 언어별 템플릿을 여기서 관리합니다.
# - 분석 방향이나 출력 형식을 바꾸려면 이 파일만 수정하세요.

# ── 카테고리별 분석 힌트 ──────────────────────────────────────────────────────
# 수집된 기사의 카테고리 분포 Top 2를 자동 감지해 프롬프트에 삽입됩니다.
# 새 카테고리를 rss_sources.py에 추가했다면 여기에도 힌트를 추가하세요.

CATEGORY_PROMPTS: dict[str, str] = {
    "technology":        "기술 트렌드, 제품 출시, 주요 기업 동향에 초점을 맞춰 분석하세요.",
    "economy":           "시장 영향, 금리·환율 변동, 투자 시사점 중심으로 분석하세요.",
    "ai_ml":             "AI 모델 출시, 연구 성과, 산업 적용 사례 중심으로 분석하세요.",
    "global_news":       "지정학적 리스크, 국제 정세, 주요 이벤트 중심으로 분석하세요.",
    "korean_news":       "국내 정치·사회 주요 이슈, 정책 변화 중심으로 분석하세요.",
    "korean_economy":    "국내 경제 지표, 기업 실적, 부동산·주식 시장 중심으로 분석하세요.",
    "korean_tech":       "국내 IT·기술 산업 동향, 스타트업, 정책 지원 중심으로 분석하세요.",
    "security":          "사이버 위협, 취약점, 보안 사고 및 대응 동향 중심으로 분석하세요.",
    "startup":           "스타트업 투자, 성장 사례, VC 트렌드 중심으로 분석하세요.",
}

DEFAULT_PROMPT_HINT: str = "핵심 이슈와 공통 트렌드 중심으로 분석하세요."

# ── 뉴스 분석 공통 프롬프트 템플릿 ─────────────────────────────────────────
# {hints}      : 카테고리 힌트 문구 (자동 삽입)
# {lang_label} : "한국어" 또는 "영어" (자동 삽입)
# {title_block}: 기사 제목+요약 목록 (자동 삽입)

PROMPT_TEMPLATE: str = """\
당신은 뉴스 분석 전문가입니다. 아래 {lang_label} 뉴스 제목을 분석하세요.
{hints}
**반드시 한국어로 답변하세요.**

출력 형식 (반드시 준수 — 빈 줄 포함):

## 핵심 이슈 TOP 3

### 1. [이슈 핵심 제목]

2~3문장 요약. 중요도와 배경 포함.

🔗 주요 출처: [기사제목](링크URL)

### 2. [이슈 제목]

설명.

🔗 주요 출처: [기사제목](링크URL)

### 3. [이슈 제목]

설명.

🔗 주요 출처: [기사제목](링크URL)

## 주목할 트렌드

1. **[키워드]**

   1~2문장 설명

2. **[키워드]**

   1~2문장 설명

3. **[키워드]**

   1~2문장 설명

뉴스 목록:
{title_block}
"""

# ── JSON 구조화 출력 프롬프트 (Editorial/Terminal 테마용) ─────────────────────
# 사용 조건: THEME_NEWS=editorial 또는 terminal 일 때 analyzer가 선택
# 반환값: ```json ... ``` 블록 안의 JSON을 파싱해서 data["structured"] 에 저장

PROMPT_TEMPLATE_JSON: str = """\
당신은 뉴스 분석 AI입니다. 아래 뉴스 목록을 분석하고 **JSON만** 출력하세요.
{hints}
**반드시 한국어 텍스트로 작성하고, JSON 외 다른 설명은 출력하지 마세요.**

출력 형식 (```json 블록으로 감싸세요):
```json
{
  "lang": "{lang}",
  "issues": [
    {
      "rank": 1,
      "title": "이슈 핵심 제목",
      "summary": "2~3문장 요약. 중요도와 배경 포함.",
      "category": "ai_ml",
      "importance": "high",
      "sources": [
        {"title": "기사 제목", "url": "https://..."}
      ]
    },
    {"rank": 2, "title": "...", "summary": "...", "category": "...", "importance": "medium", "sources": []},
    {"rank": 3, "title": "...", "summary": "...", "category": "...", "importance": "medium", "sources": []}
  ],
  "trends": [
    {"keyword": "키워드1", "description": "1~2문장 설명", "category": "ai_ml"},
    {"keyword": "키워드2", "description": "설명", "category": "technology"},
    {"keyword": "키워드3", "description": "설명", "category": "economy"}
  ],
  "category_stats": {
    "ai_ml": 0,
    "technology": 0,
    "economy": 0,
    "global_news": 0,
    "korean_news": 0,
    "security": 0,
    "startup": 0
  }
}
```

category 값은 다음 중 하나: ai_ml, technology, economy, global_news, korean_news, korean_economy, korean_tech, security, startup
importance 값: high, medium, low
category_stats: 뉴스 목록에서 각 카테고리 기사 수를 카운트

뉴스 목록:
{title_block}
"""
