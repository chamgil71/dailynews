# config/ai_issue_sources.py
"""
주간 AI 이슈 브리핑(ai-issue) 전용 수집 소스 및 스코어링 설정 파일.
Phase 0 실 접속 유효성 검증을 마친 최적의 16개 RSS 피드를 카테고리별로 정밀하게 탑재합니다.
"""
from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────
# cs.AI arXiv 1차 스코어링 키워드 가중치 (추후 설정 조정을 통해 손쉽게 수집 성격 변경 가능)
# ──────────────────────────────────────────────────────────────────────────
SCORING_KEYWORDS = {
    # 1. 기술적 핵심 키워드 (가장 가중치가 높은 트렌드 기술)
    "llm": 5,
    "gpt": 5,
    "claude": 5,
    "gemini": 5,
    "transformer": 4,
    "rag": 4,
    "agent": 4,
    "fine-tuning": 3,
    "quantization": 3,
    "inference": 3,
    "diffusion": 3,
    "multimodal": 4,
    "reinforcement": 3,
    "finetuning": 3,
    
    # 2. 비즈니스 / 인프라
    "nvidia": 4,
    "openai": 4,
    "anthropic": 4,
    "datacenter": 3,
    "hbm": 3,
    "supercomputer": 3,
    
    # 3. 한국어 핵심 필터 키워드
    "거대언어모델": 5,
    "인공지능": 2,
    "네이버": 3,
    "카카오": 3,
    "반도체": 3,
    "생성형": 3,
    "규제": 2,
    "스타트업": 2,
}

# ──────────────────────────────────────────────────────────────────────────
# 1. AI 기업 공식 블로그 (실 접속 검증 완료)
# ──────────────────────────────────────────────────────────────────────────
AI_BLOG_SOURCES = {
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Google AI Blog": "https://blog.google/technology/ai/rss",
    "Microsoft AI": "https://blogs.microsoft.com/ai/feed/",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
}

# ──────────────────────────────────────────────────────────────────────────
# 2. AI 전문 미디어 (실 접속 검증 완료)
# ──────────────────────────────────────────────────────────────────────────
AI_MEDIA_SOURCES = {
    "The Decoder": "https://the-decoder.com/feed/",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/index",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "MIT Tech Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
}

# ──────────────────────────────────────────────────────────────────────────
# 3. 연구 및 논문 피드 (arXiv cs.AI/cs.LG/cs.CL 전수 수집 및 스코어링 대상)
# ──────────────────────────────────────────────────────────────────────────
ARXIV_SOURCES = {
    "arXiv cs.AI": "https://arxiv.org/rss/cs.AI",
    "arXiv cs.LG": "https://arxiv.org/rss/cs.LG",
    "arXiv cs.CL": "https://arxiv.org/rss/cs.CL",
}

# ──────────────────────────────────────────────────────────────────────────
# 4. 국내 IT 및 AI 미디어 (실 접속 검증 완료)
# ──────────────────────────────────────────────────────────────────────────
DOMESTIC_SOURCES = {
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "전자신문": "https://rss.etnews.com/Section901.xml",
}

# ──────────────────────────────────────────────────────────────────────────
# 5. 투자 및 펀딩 동향 (실 접속 검증 완료)
# ──────────────────────────────────────────────────────────────────────────
FUNDING_SOURCES = {
    "TechCrunch Funding": "https://techcrunch.com/tag/funding/feed/",
}

# 통합 맵핑 리스트 (순회 목적)
ALL_SOURCES = {
    **AI_BLOG_SOURCES,
    **AI_MEDIA_SOURCES,
    **ARXIV_SOURCES,
    **DOMESTIC_SOURCES,
    **FUNDING_SOURCES
}
