# core/stock_analyzer.py
"""
주식 시황 LLM 분석 모듈 (GitHub Actions 백업 경로).

stock_collector.build_stock_data() 결과를 받아
STOCK_ANALYSIS_PROMPT 에 주입 후 LLM 호출 → 섹션별 파싱 반환.

Claude Code 루틴 경로에서는 이 모듈 없이 Claude가 직접 분석한다.
"""
from __future__ import annotations

import logging
import re

from config.stock_prompts import STOCK_ANALYSIS_PROMPT, TEMPERATURE_OPTIONS, TEMPERATURE_EMOJI
from config.settings import (
    LLM_PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL_FULL, GEMINI_MODEL_MINI, GEMINI_MINI_THRESHOLD,
    OPENAI_API_KEY, GPT_MODEL_FULL, GPT_MODEL_MINI, GPT_MINI_THRESHOLD,
    ANTHROPIC_KEY, CLAUDE_MODEL_FULL, CLAUDE_MODEL_MINI, CLAUDE_MINI_THRESHOLD,
)

logger = logging.getLogger(__name__)


# ── 프롬프트 빌더 ──────────────────────────────────────────────────────────────

def _build_market_block(stock_data: dict) -> str:
    """market dict → 텍스트 블록 (LLM 입력용)."""
    m = stock_data.get("market", {})
    lines = []

    def _pct(val) -> str:
        if val is None or val == "?":
            return "N/A"
        try:
            return f"{float(val):+.2f}%"
        except (ValueError, TypeError):
            return "N/A"

    def _bp(val) -> str:
        if val is None or val == "N/A":
            return "N/A"
        try:
            return f"{float(val):+.1f}bp"
        except (ValueError, TypeError):
            return "N/A"

    def _v(key: str, subkey: str, label: str, unit: str = "") -> str:
        val = m.get(key, {}).get(subkey)
        if val is None:
            return f"{label}: N/A"
        return f"{label}: {val:,.2f}{unit}"

    us10y_val = m.get('us10y', {}).get('value')
    us10y_bp = m.get('us10y', {}).get('change_bp')
    us10y_str = f"미국 10년물 금리: {us10y_val:,.2f}%" if us10y_val is not None else "미국 10년물 금리: N/A"
    if us10y_val is not None and us10y_bp is not None:
        us10y_str += f"  ({_bp(us10y_bp)})"

    lines += [
        "[ 국내 지수 ]",
        _v("kospi",   "close",      "코스피", "pt") + f"  ({_pct(m.get('kospi',{}).get('change_pct'))})",
        _v("kosdaq",  "close",      "코스닥", "pt") + f"  ({_pct(m.get('kosdaq',{}).get('change_pct'))})",
        _v("usd_krw", "close",      "원/달러", "원") + f"  ({_pct(m.get('usd_krw',{}).get('change_pct'))})",
        "",
        "[ 미국 지수 ]",
        _v("sp500",   "close",      "S&P 500") + f"  ({_pct(m.get('sp500',{}).get('change_pct'))})",
        _v("nasdaq",  "close",      "나스닥")  + f"  ({_pct(m.get('nasdaq',{}).get('change_pct'))})",
        _v("dow",     "close",      "다우존스")+ f"  ({_pct(m.get('dow',{}).get('change_pct'))})",
        "",
        "[ 매크로 ]",
        us10y_str,
        _v("wti",     "close",      "WTI 유가", "$") + f"  ({_pct(m.get('wti',{}).get('change_pct'))})",
    ]

    sectors = stock_data.get("sectors", {})
    if sectors:
        try:
            from config.watchlist import get_all_tickers
            ticker_map = {t["name"]: t for t in get_all_tickers()}
        except Exception:
            ticker_map = {}

        kr_lines: list[str] = []
        us_lines: list[str] = []
        for name, data in sectors.items():
            chg = data.get("change_pct")
            chg_str = f"{chg:+.2f}%" if chg is not None else "N/A"
            line = f"{name}: {data.get('close','N/A')} ({chg_str})"
            if ticker_map.get(name, {}).get("market") == "US":
                us_lines.append(line)
            else:
                kr_lines.append(line)

        if kr_lines:
            lines += ["", "[ 국내 섹터 종목 ]"] + kr_lines
        if us_lines:
            lines += ["", "[ 해외 섹터 종목 ]"] + us_lines

    return "\n".join(lines)


def _build_news_block(stock_data: dict) -> str:
    """news_ko list → 텍스트 블록."""
    news = stock_data.get("news_ko", [])
    if not news:
        return "뉴스 데이터 없음"
    return "\n".join(f"- {n.get('title','')}" for n in news)


def _build_prompt(stock_data: dict) -> str:
    return STOCK_ANALYSIS_PROMPT.format(
        market_block=_build_market_block(stock_data),
        news_block=_build_news_block(stock_data),
    )


# ── LLM 호출 ──────────────────────────────────────────────────────────────────

def _call_llm(prompt: str) -> str:
    """설정된 LLM 으로 프롬프트 전송. 실패 시 빈 문자열 반환."""
    import time
    from core.shared.alerts import send_llm_failure_alert, is_model_error, gha_warning
    provider = LLM_PROVIDER.lower()

    def _try_gemini() -> str:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        config = types.GenerateContentConfig(max_output_tokens=2000, temperature=0.3)
        # 재시도 3회 (2s / 4s / 8s)
        models_to_try = [GEMINI_MODEL_FULL]
        if GEMINI_MODEL_FULL == "gemini-3.5-flash":
            models_to_try.append("gemini-2.5-flash")

        for model in models_to_try:
            for attempt in range(3):
                try:
                    resp = client.models.generate_content(
                        model=model, contents=prompt, config=config,
                    )
                    return resp.text.strip().replace('\r\n', '\n').replace('\r', '\n')
                except Exception as e:
                    err_str = str(e)
                    if is_model_error(e):
                        if model == models_to_try[-1]:
                            send_llm_failure_alert("gemini", model, e, context="stock analyzer")
                            raise
                        else:
                            gha_warning(f"Gemini {model} 치명적 오류, 폴백 모델 시도: {err_str[:80]}")
                            break
                    is_retryable = any(k in err_str for k in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))
                    if is_retryable and attempt < 2:
                        wait = 2 ** (attempt + 1)
                        gha_warning(f"Gemini {model} 과부하 재시도 ({attempt+1}/3): {err_str[:80]}")
                        time.sleep(wait)
                    else:
                        if model == models_to_try[-1]:
                            send_llm_failure_alert("gemini", model, e, context="stock analyzer")
                            raise
                        else:
                            gha_warning(f"Gemini {model} 과부하 최종 실패, 폴백 모델 시도: {err_str[:80]}")
                            break
        return ""

    try:
        if provider == "gemini":
            return _try_gemini()

        elif provider == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            msg    = client.messages.create(
                model=CLAUDE_MODEL_FULL,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip().replace('\r\n', '\n').replace('\r', '\n')

        else:  # gpt
            from openai import OpenAI
            client   = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=GPT_MODEL_FULL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip().replace('\r\n', '\n').replace('\r', '\n')

    except Exception as e:
        logger.error(f"[stock_analyzer] LLM 호출 최종 실패: {e}")
        return ""


# ── LLM 출력 파싱 ──────────────────────────────────────────────────────────────

def _parse_section(text: str, header: str) -> str:
    """## {header} 섹션 내용 추출. 헤더 뒤 추가 텍스트(굵게, 공백 등) 허용."""
    m = re.search(
        rf'## {re.escape(header)}[^\n]*\n([\s\S]*?)(?=\n## |\Z)',
        text,
    )
    return m.group(1).strip() if m else ""


def _parse_temperature(text: str) -> tuple[str, str]:
    """
    ## 시장 온도계 섹션에서 (온도값, 근거) 추출.
    온도값: "리스크오프" | "중립" | "리스크온"
    """
    block = _parse_section(text, "시장 온도계")
    temp  = "중립"
    for opt in TEMPERATURE_OPTIONS:
        if opt in block:
            temp = opt
            break
    # "근거: XXX" 추출
    reason_m = re.search(r'근거:\s*(.+)', block)
    reason   = reason_m.group(1).strip() if reason_m else block.split("\n")[0].strip()
    return temp, reason


def _parse_sectors(text: str) -> list[dict]:
    """
    ## 4. 섹터별 영향 분석 파싱 → list[{name, symbol, direction, point, market}].
    ### 🇰🇷 국내 / ### 🇺🇸 해외 서브섹션 기준으로 market 태깅.
    3열 구형 포맷도 호환.
    """
    block          = _parse_section(text, "4. 섹터별 영향 분석")
    sectors        = []
    current_market = "KR"

    for line in block.splitlines():
        ls = line.strip()
        if "🇰🇷" in ls or ("국내" in ls and "###" in ls):
            current_market = "KR"
            continue
        if "🇺🇸" in ls or ("해외" in ls and "###" in ls):
            current_market = "US"
            continue

        # 4열: 섹터 | 대표종목 | 방향 | 핵심포인트
        m4 = re.match(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', ls)
        if m4:
            name = m4.group(1).strip()
            if not name or "---" in name or name.startswith(":") or name == "섹터":
                continue
            sectors.append({
                "name":      name,
                "symbol":    m4.group(2).strip(),
                "direction": m4.group(3).strip(),
                "point":     m4.group(4).strip(),
                "market":    current_market,
            })
            continue

        # 3열 구형: 섹터 | 방향 | 핵심포인트
        m3 = re.match(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', ls)
        if m3:
            name = m3.group(1).strip()
            if not name or "---" in name or name.startswith(":") or name == "섹터":
                continue
            sectors.append({
                "name":      name,
                "symbol":    "",
                "direction": m3.group(2).strip(),
                "point":     m3.group(3).strip(),
                "market":    current_market,
            })

    return sectors


def analyze_stock(stock_data: dict) -> dict:
    """
    stock_data → LLM 분석 → 섹션별 파싱 dict 반환.

    반환 키:
      summary, domestic_issues, global_macro,
      keywords, sectors(list), lt_comment,
      temperature, temperature_reason, temperature_display,
      combined (전체 원문)
    """
    prompt   = _build_prompt(stock_data)
    raw_text = _call_llm(prompt)

    if not raw_text:
        logger.warning("[stock_analyzer] LLM 응답 없음 — 빈 분석 반환")
        return {k: "" for k in [
            "summary","domestic_issues","global_macro","keywords",
            "lt_comment","temperature","temperature_reason","temperature_display","combined",
        ]} | {"sectors": []}

    temp, reason = _parse_temperature(raw_text)
    temp_display = f"{TEMPERATURE_EMOJI.get(temp,'🟡')} {temp}"

    return {
        "summary":             _parse_section(raw_text, "■ 핵심 요약 (3줄)"),
        "domestic_issues":     _parse_section(raw_text, "주요 이슈 (국내)"),
        "global_macro":        _parse_section(raw_text, "매크로 (글로벌)"),
        "keywords":            _parse_section(raw_text, "3. 핵심 키워드 TOP 5"),
        "sectors":             _parse_sectors(raw_text),
        "lt_comment":          _parse_section(raw_text, "6. 장기투자 관점 코멘트"),
        "temperature":         temp,
        "temperature_reason":  reason,
        "temperature_display": temp_display,
        "combined":            raw_text,
    }
