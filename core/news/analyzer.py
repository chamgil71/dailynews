"""
AI 분석 모듈 (Gemini 3.1 최적화 버전)
- 카테고리별 맞춤 프롬프트
- Gemini 3.1의 'Thought Signature(사고 흔적) 순환' 로직 반영
- google-genai 최신 SDK 기반 구현
"""

import logging
import os
from abc import ABC, abstractmethod
from collections import Counter

# 최신 SDK 임포트
from google import genai
from google.genai import types

from config.settings import (
    LLM_PROVIDER,
    OPENAI_API_KEY, GPT_MODEL_FULL, GPT_MODEL_MINI, GPT_MINI_THRESHOLD,
    ANTHROPIC_KEY,  CLAUDE_MODEL_FULL, CLAUDE_MODEL_MINI, CLAUDE_MINI_THRESHOLD,
    GEMINI_API_KEY, GEMINI_MODEL_FULL, GEMINI_MODEL_MINI, GEMINI_MINI_THRESHOLD,
    LLM_MAX_TOKENS,
)
from config.prompts import (
    CATEGORY_PROMPTS, DEFAULT_PROMPT_HINT,
    PROMPT_TEMPLATE, PROMPT_TEMPLATE_JSON,
)

logger = logging.getLogger(__name__)


def _build_prompt(news: list, lang: str, use_json: bool = False) -> str:
    """카테고리 분포를 파악해 프롬프트 힌트를 동적으로 구성."""
    cat_counts = Counter(n.get("category", "") for n in news)
    top_cats   = [c for c, _ in cat_counts.most_common(2)]
    hints      = " ".join(CATEGORY_PROMPTS.get(c, "") for c in top_cats).strip()
    if not hints:
        hints = DEFAULT_PROMPT_HINT

    title_block = "\n".join(
        f"[{n['label']}] {n['title']}"
        + (f" | {n['link']}" if n.get("link") else "")
        + (f"\n  요약: {n['summary']}" if n.get("summary") else "")
        for n in news
    )

    if use_json:
        return PROMPT_TEMPLATE_JSON.format(hints=hints, title_block=title_block, lang=lang)

    lang_label = "한국어" if lang == "ko" else "영어"
    return PROMPT_TEMPLATE.format(hints=hints, title_block=title_block, lang_label=lang_label)


def _parse_json_response(text: str) -> dict | None:
    """AI 응답에서 JSON을 추출해 파싱. ```json 블록 또는 순수 JSON 모두 처리."""
    import json, re
    text = text.strip()
    # 1차: ```json 블록 추출
    m = re.search(r'```json\s*([\s\S]*?)```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # 2차: raw_decode — 첫 번째 유효한 JSON 객체에서 멈춤 (trailing 내용 무시)
    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # 3차: 첫 번째 '{' 위치부터 raw_decode 재시도 (앞에 다른 텍스트가 있을 경우)
    idx = text.find('{')
    if idx > 0:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text[idx:])
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    logger.warning(f"[JSON 파싱] 모든 방법 실패. 응답 앞 300자: {text[:300]!r}")
    return None

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
            max_tokens=LLM_MAX_TOKENS,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": "", "structured": {},
                   "analysis_ok": False, "fallback_used": {"en": False, "ko": False}}
        json_mode = True
        if en_news:
            try:
                raw = self._call(_build_prompt(en_news, "en", json_mode), len(en_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["en"] = data or {}
                    if data:
                        results["en"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[GPT 분석 완료] 영어 {len(en_news)}건")
                    else:
                        results["en"] = _fallback_summary(en_news, "en")
                        results["fallback_used"]["en"] = True
                        logger.warning("[GPT EN] JSON 파싱 실패 — fallback 사용")
                else:
                    results["en"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[GPT 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[GPT EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
                results["fallback_used"]["en"] = True
        if ko_news:
            try:
                raw = self._call(_build_prompt(ko_news, "ko", json_mode), len(ko_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["ko"] = data or {}
                    if data:
                        results["ko"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[GPT 분석 완료] 한국어 {len(ko_news)}건")
                    else:
                        results["ko"] = _fallback_summary(ko_news, "ko")
                        results["fallback_used"]["ko"] = True
                        logger.warning("[GPT KO] JSON 파싱 실패 — fallback 사용")
                else:
                    results["ko"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[GPT 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[GPT KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
                results["fallback_used"]["ko"] = True
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
            max_tokens=LLM_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": "", "structured": {},
                   "analysis_ok": False, "fallback_used": {"en": False, "ko": False}}
        json_mode = True
        if en_news:
            try:
                raw = self._call(_build_prompt(en_news, "en", json_mode), len(en_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["en"] = data or {}
                    if data:
                        results["en"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[Claude 분석 완료] 영어 {len(en_news)}건")
                    else:
                        results["en"] = _fallback_summary(en_news, "en")
                        results["fallback_used"]["en"] = True
                        logger.warning("[Claude EN] JSON 파싱 실패 — fallback 사용")
                else:
                    results["en"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[Claude 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[Claude EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
                results["fallback_used"]["en"] = True
        if ko_news:
            try:
                raw = self._call(_build_prompt(ko_news, "ko", json_mode), len(ko_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["ko"] = data or {}
                    if data:
                        results["ko"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[Claude 분석 완료] 한국어 {len(ko_news)}건")
                    else:
                        results["ko"] = _fallback_summary(ko_news, "ko")
                        results["fallback_used"]["ko"] = True
                        logger.warning("[Claude KO] JSON 파싱 실패 — fallback 사용")
                else:
                    results["ko"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[Claude 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[Claude KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
                results["fallback_used"]["ko"] = True
        results["combined"] = _merge(results["en"], results["ko"])
        return results

# ── Gemini (3.1 최적화) ────────────────────────────────────────────────────────

class GeminiAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    @staticmethod
    def _make_config(json_mode: bool) -> "types.GenerateContentConfig":
        kwargs: dict = {"max_output_tokens": LLM_MAX_TOKENS, "temperature": 0.3}
        if json_mode:
            kwargs["response_mime_type"] = "application/json"
        return types.GenerateContentConfig(**kwargs)

    def _call(self, prompt: str, news_count: int) -> str:
        import time
        from core.shared.alerts import send_llm_failure_alert, is_model_error, gha_warning
        model_name = self._pick_model(
            news_count, GEMINI_MODEL_FULL, GEMINI_MODEL_MINI, GEMINI_MINI_THRESHOLD
        )
        config = self._make_config(json_mode=True)
        # 503/429 과부하 대응: 최대 3회 재시도 (2s / 4s / 8s 백오프)
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                if is_model_error(e):
                    # 모델 만료·미존재: 재시도 불필요, 즉시 관리자 알림
                    send_llm_failure_alert("gemini", model_name, e, context="news analyzer")
                    raise
                is_retryable = any(k in err_str for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                if is_retryable and attempt < 2:
                    wait = 2 ** (attempt + 1)
                    gha_warning(f"Gemini 일시 과부하 — {wait}초 후 재시도 ({attempt+1}/3): {err_str[:80]}")
                    time.sleep(wait)
                else:
                    send_llm_failure_alert("gemini", model_name, e, context="news analyzer")
                    raise

    def analyze_by_lang(self, en_news: list, ko_news: list) -> dict:
        results = {"en": "", "ko": "", "combined": "", "structured": {},
                   "analysis_ok": False, "fallback_used": {"en": False, "ko": False}}
        json_mode = True

        if en_news:
            try:
                raw = self._call(_build_prompt(en_news, "en", json_mode), len(en_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["en"] = data or {}
                    if data:
                        results["en"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[Gemini 분석 완료] 영어 {len(en_news)}건")
                    else:
                        results["en"] = _fallback_summary(en_news, "en")
                        results["fallback_used"]["en"] = True
                        logger.warning("[Gemini EN] JSON 파싱 실패 — fallback 사용")
                else:
                    results["en"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[Gemini 분석 완료] 영어 {len(en_news)}건")
            except Exception as e:
                logger.error(f"[Gemini EN 실패] {e}")
                results["en"] = _fallback_summary(en_news, "en")
                results["fallback_used"]["en"] = True

        if ko_news:
            try:
                raw = self._call(_build_prompt(ko_news, "ko", json_mode), len(ko_news))
                if json_mode:
                    data = _parse_json_response(raw)
                    results["structured"]["ko"] = data or {}
                    if data:
                        results["ko"] = _structured_to_markdown(data)
                        results["analysis_ok"] = True
                        logger.info(f"[Gemini 분석 완료] 한국어 {len(ko_news)}건")
                    else:
                        results["ko"] = _fallback_summary(ko_news, "ko")
                        results["fallback_used"]["ko"] = True
                        logger.warning("[Gemini KO] JSON 파싱 실패 — fallback 사용")
                else:
                    results["ko"] = raw
                    results["analysis_ok"] = True
                    logger.info(f"[Gemini 분석 완료] 한국어 {len(ko_news)}건")
            except Exception as e:
                logger.error(f"[Gemini KO 실패] {e}")
                results["ko"] = _fallback_summary(ko_news, "ko")
                results["fallback_used"]["ko"] = True

        results["combined"] = _merge(results["en"], results["ko"])
        return results

# ── 헬퍼 및 API ──────────────────────────────────────────────────────────────

def _structured_to_markdown(data: dict) -> str:
    """JSON 구조 데이터를 마크다운 텍스트로 변환 (MD 리포트 저장용)."""
    if not data:
        return ""
    lines = ["## 핵심 이슈 TOP 3", ""]
    for issue in data.get("issues", []):
        lines += [
            f"### {issue['rank']}. {issue['title']}",
            "",
            issue.get("summary", ""),
            "",
        ]
        for src in issue.get("sources", []):
            lines.append(f"🔗 주요 출처: [{src['title']}]({src['url']})")
        lines.append("")
    lines += ["## 주목할 트렌드", ""]
    for i, trend in enumerate(data.get("trends", []), 1):
        lines += [
            f"{i}. **{trend['keyword']}**",
            "",
            f"   {trend.get('description', '')}",
            "",
        ]
    return "\n".join(lines).strip()


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

def get_analyzer() -> BaseAnalyzer:
    provider = LLM_PROVIDER.lower()
    if provider == "claude":
        return ClaudeAnalyzer()
    if provider == "gemini":
        return GeminiAnalyzer()
    return GPTAnalyzer()

def analyze(news_data: dict) -> dict:
    analyzer = get_analyzer()
    return analyzer.analyze_by_lang(
        en_news=news_data.get("en", []),
        ko_news=news_data.get("ko", []),
    )