# core/analyzer.py
"""
AI 분석 모듈
- 카테고리별 맞춤 프롬프트 (기술 / 경제 / AI·ML / 종합)
- 한국어 / 영어 뉴스 분리 분석 후 통합
- GPT / Claude / Gemini 모두 조건부 모델 선택 (뉴스 건수 기준)
- 분석 실패 시 원문 제목 목록 폴백
- LLM_PROVIDER 환경변수로 LLM 교체 (코드 수정 불필요)
"""

import logging
import os
from abc import ABC, abstractmethod
from collections import Counter

from config.settings import (
    LLM_PROVIDER,
    OPENAI_API_KEY, GPT_MODEL_FULL, GPT_MODEL_MINI, GPT_MINI_THRESHOLD,
    ANTHROPIC_KEY,  CLAUDE_MODEL_FULL, CLAUDE_MODEL_MINI, CLAUDE_MINI_THRESHOLD,
    GEMINI_API_KEY, GEMINI_MODEL_FULL, GEMINI_MODEL_MINI, GEMINI_MINI_THRESHOLD,
)

logger = logging.getLogger(__name__)


# ── 카테고리별 분석 프롬프트 ──────────────────────────────────────────────────

CATEGORY_PROMPTS = {
    "technology":     "기술 트렌드, 제품 출시, 주요 기업 동향에 초점을 맞춰 분석하세요.",
    "economy":        "시장 영향, 금리·환율 변동, 투자 시사점 중심으로 분석하세요.",
    "ai_ml":          "AI 모델 출시, 연구 성과, 산업 적용 사례 중심으로 분석하세요.",
    "global_news":    "지정학적 리스크, 국제 정세, 주요 이벤트 중심으로 분석하세요.",
    "korean_news":    "국내 정치·사회 주요 이슈, 정책 변화 중심으로 분석하세요.",
    "korean_economy": "국내 경제 지표, 기업 실적, 부동산·주식 시장 중심으로 분석하세요.",
}

DEFAULT_PROMPT_HINT = "핵심 이슈와 공통 트렌드 중심으로 분석하세요."


def _build_prompt(news: list, lang: str) -> str:
    """카테고리 분포를 파악해 프롬프트 힌트를 동적으로 구성."""
    cat_counts = Counter(n["category"] for n in news)
    top_cats   = [c for c, _ in cat_counts.most_common(2)]
    hints      = " ".join(CATEGORY_PROMPTS.get(c, "") for c in top_cats).strip()
    if not hints:
        hints = DEFAULT_PROMPT_HINT
    
    ## title 만
    ## title_block = "\n".join(f"[{n['label']}] {n['title']}" for n in news)
    
    # 요약 포함
    title_block = "\n".join(
    f"[{n['label']}] {n['title']}"
    + (f"\n  요약: {n['summary']}" if n.get('summary') else "")
    for n in news
    )

    if lang == "ko":
        return f"""당신은 뉴스 분석 전문가입니다. 아래 한국어 뉴스 제목을 분석하세요.
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
    else:
        return f"""You are a professional news analyst. Analyze the following news headlines.
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


# ── 베이스 클래스 ─────────────────────────────────────────────────────────────

class BaseAnalyzer(ABC):

    def _pick_model(self, news_count: int, model_full: str,
                    model_mini: str, threshold: int) -> str:
        """뉴스 건수에 따라 full/mini 모델 자동 선택."""
        model = model_mini if news_count <= threshold else model_full
        logger.info(f"[모델 선택] {model} (뉴스 {news_count}건, 기준 {threshold}건)")
        return model

    @abstractmethod
    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        """반환: {"en": str, "ko": str, "combined": str}"""


# ── GPT ───────────────────────────────────────────────────────────────────────

class GPTAnalyzer(BaseAnalyzer):

    def __init__(self):
        from openai import OpenAI
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def _call(self, prompt: str, news_count: int) -> str:
        model = self._pick_model(
            news_count, GPT_MODEL_FULL, GPT_MODEL_MINI, GPT_MINI_THRESHOLD
        )
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": ""}
        if en_news:
            try:
                results["en"] = self._call(_build_prompt(en_news, "en"), len(en_news))
                logger.info(f"[GPT 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[GPT EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
        if ko_news:
            try:
                results["ko"] = self._call(_build_prompt(ko_news, "ko"), len(ko_news))
                logger.info(f"[GPT 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[GPT KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
        results["combined"] = _merge(results["en"], results["ko"])
        return results


# ── Claude ────────────────────────────────────────────────────────────────────

class ClaudeAnalyzer(BaseAnalyzer):

    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    def _call(self, prompt: str, news_count: int) -> str:
        model = self._pick_model(
            news_count, CLAUDE_MODEL_FULL, CLAUDE_MODEL_MINI, CLAUDE_MINI_THRESHOLD
        )
        msg = self.client.messages.create(
            model=model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": ""}
        if en_news:
            try:
                results["en"] = self._call(_build_prompt(en_news, "en"), len(en_news))
                logger.info(f"[Claude 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[Claude EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
        if ko_news:
            try:
                results["ko"] = self._call(_build_prompt(ko_news, "ko"), len(ko_news))
                logger.info(f"[Claude 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[Claude KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
        results["combined"] = _merge(results["en"], results["ko"])
        return results


# ── Gemini ────────────────────────────────────────────────────────────────────

class GeminiAnalyzer(BaseAnalyzer):

    def __init__(self):
        from google import genai
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def _call(self, prompt: str, news_count: int) -> str:
        from google.genai import types
        model_name = self._pick_model(
            news_count, GEMINI_MODEL_FULL, GEMINI_MODEL_MINI, GEMINI_MINI_THRESHOLD
        )
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=800,
                temperature=0.3,
            )
        )
        return response.text.strip()

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": ""}
        if en_news:
            try:
                results["en"] = self._call(_build_prompt(en_news, "en"), len(en_news))
                logger.info(f"[Gemini 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[Gemini EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
        if ko_news:
            try:
                results["ko"] = self._call(_build_prompt(ko_news, "ko"), len(ko_news))
                logger.info(f"[Gemini 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[Gemini KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
        results["combined"] = _merge(results["en"], results["ko"])
        return results


# ── 헬퍼 ──────────────────────────────────────────────────────────────────────

def _fallback_summary(news: list, lang: str) -> str:
    header = "⚠ AI 분석 실패 — 원문 제목 목록" if lang == "ko" \
             else "⚠ AI analysis failed — raw headlines"
    lines  = "\n".join(f"- [{n['label']}] {n['title']}" for n in news[:15])
    return f"{header}\n\n{lines}"


def _merge(en: str, ko: str) -> str:
    parts = []
    if en: parts.append("## 🌐 Global News Analysis\n\n" + en)
    if ko: parts.append("## 🇰🇷 국내 뉴스 분석\n\n" + ko)
    return "\n\n---\n\n".join(parts) if parts else "분석 결과 없음"


# ── 팩토리 ────────────────────────────────────────────────────────────────────

def get_analyzer() -> BaseAnalyzer:
    provider = LLM_PROVIDER.lower()
    if provider == "claude":
        logger.info("[Analyzer] Claude 사용")
        return ClaudeAnalyzer()
    if provider == "gemini":
        logger.info("[Analyzer] Gemini 사용")
        return GeminiAnalyzer()
    logger.info("[Analyzer] GPT 사용")
    return GPTAnalyzer()


# ── 공개 API ──────────────────────────────────────────────────────────────────

def analyze(news_data: dict) -> dict:
    analyzer = get_analyzer()
    return analyzer.analyze_by_lang(
        en_news=news_data.get("en", []),
        ko_news=news_data.get("ko", []),
    )