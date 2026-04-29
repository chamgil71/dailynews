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

# ── 한국어 뉴스 분석 프롬프트 템플릿 ─────────────────────────────────────────
# {hints}      : 카테고리 힌트 문구 (자동 삽입)
# {title_block}: 기사 제목+요약 목록 (자동 삽입)

PROMPT_TEMPLATE_KO: str = """\
당신은 뉴스 분석 전문가입니다. 아래 한국어 뉴스 제목을 분석하세요.
{hints}
**반드시 한국어로 답변하세요.**

출력 형식 (반드시 준수):
## 핵심 이슈 TOP 3
1. **이슈 제목** — 2~3문장 요약, 중요도·배경 포함
2. ...
3. ...

## 주목할 트렌드
- 공통 키워드·패턴 2~3개를 짧게 서술

뉴스 목록:
{title_block}
"""

# ── 영어 뉴스 분석 프롬프트 템플릿 ───────────────────────────────────────────

PROMPT_TEMPLATE_EN: str = """\
You are a professional news analyst. Analyze the following news headlines.
{hints}

Output format (strictly follow):
## Top 3 Key Issues
1. **Issue Title** — 2-3 sentence summary with context and significance
2. ...
3. ...

## Notable Trends
- 2-3 bullet points on patterns or common themes

Headlines:
{title_block}
"""
