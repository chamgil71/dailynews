# core/ai_issue/analyzer.py
"""
주간 AI 이슈 브리핑용 AI 분석 모듈.
1. 수집 기사 -> TOP 10 및 TOP 3 심층 분석 (JSON)
2. 수집 기사 -> 주요 AI 기업 동향 (Markdown)
3. 수집 기사 -> 주간 실용 AI 팁 2선 (JSON)
4. cs.AI arXiv 후보 30선 -> 최종 주목 논문 2~3편 (JSON)
5. 종합 -> 차주 전망 (Markdown)
"""
from __future__ import annotations

import logging
import json
import re
import sys
from pathlib import Path

_ROOT = str(Path(__file__).parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.settings import LLM_PROVIDER
from config.ai_issue_prompts import (
    MAIN_ANALYSIS_PROMPT,
    COMPANY_TRENDS_PROMPT,
    WEEKLY_TIP_PROMPT,
    PAPER_PICK_PROMPT,
    OUTLOOK_PROMPT
)
from core.news.analyzer import get_analyzer

logger = logging.getLogger(__name__)


def _unwrap_md_response(raw: str, parsed: dict | list | None) -> str | None:
    """Gemini가 JSON 래퍼로 반환한 마크다운 응답을 텍스트로 변환.
    {"summary":...}, {"report":...}, {"title":..., "points":[...]} 패턴 처리."""
    if not isinstance(parsed, dict):
        return None
    # 단순 텍스트 래퍼
    for key in ("summary", "report"):
        if key in parsed and isinstance(parsed[key], str):
            return parsed[key]
    # {"title": "...", "points": [{"point":"...","commentary":"..."}]} 패턴
    if "points" in parsed and isinstance(parsed["points"], list):
        title = parsed.get("title", "")
        lines = []
        if title:
            lines.append(f"## {title}\n")
        for item in parsed["points"]:
            point = item.get("point", "") if isinstance(item, dict) else str(item)
            commentary = item.get("commentary", "") if isinstance(item, dict) else ""
            if point:
                lines.append(f"- **{point}**")
                if commentary:
                    lines.append(f"  {commentary}")
        return "\n".join(lines) if lines else None
    return None


def _parse_json_block(text: str) -> dict | list | None:
    """LLM 응답에서 ```json ... ``` 블록 또는 순수 JSON 구조를 추출해 안전하게 파싱합니다."""
    m = re.search(r'```json\s*([\s\S]*?)```', text)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # JSON 포맷 오류 시 텍스트 복구 파서
        # 중괄호나 대괄호 시작/끝 지점 강제 검색
        start_idx = text.find('{')
        if start_idx == -1:
            start_idx = text.find('[')
        end_idx = text.rfind('}')
        if end_idx == -1:
            end_idx = text.rfind(']')
            
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(text[start_idx:end_idx+1].strip())
            except json.JSONDecodeError:
                pass
        return None


def _format_articles_text(articles: list[dict]) -> str:
    """분석 대상 일반 기사 목록을 텍스트 블록으로 일관성 있게 정렬합니다."""
    lines = []
    for idx, art in enumerate(articles, 1):
        line = f"[{idx}] 출처: {art.get('source', '미디어')} | 날짜: {art.get('date', '')}\n" \
               f"  제목: {art.get('title', '')}\n" \
               f"  요약: {art.get('summary', '')}\n" \
               f"  링크: {art.get('link', '')}"
        lines.append(line)
    return "\n\n".join(lines)


def _format_papers_text(papers: list[dict]) -> str:
    """1차 스코어링된 cs.AI 논문 목록을 텍스트 블록으로 포맷합니다."""
    lines = []
    for idx, paper in enumerate(papers, 1):
        line = f"[{idx}] 후보 논문 (가중치 점수: {paper.get('score', 0)})\n" \
               f"  제목: {paper.get('title', '')}\n" \
               f"  요약: {paper.get('summary', '')}\n" \
               f"  원문: {paper.get('link', '')}"
        lines.append(line)
    return "\n\n".join(lines)


def analyze_weekly_data(raw_weekly_data: dict) -> dict:
    """수집된 주간 원시 데이터셋을 활용해 각 섹션별 분석을 연쇄 수행하여 종합 보고서용 딕셔너리를 반환합니다."""
    logger.info("=" * 60)
    logger.info("주간 AI 이슈 브리핑 — LLM 종합 분석 시퀀스 가동")
    logger.info("=" * 60)
    
    issue_date = raw_weekly_data["issue_date"]
    period = raw_weekly_data["period"]
    articles = raw_weekly_data["articles"]
    paper_candidates = raw_weekly_data["paper_candidates"]
    stock_snapshots = raw_weekly_data["stock_snapshots"]
    
    articles_text = _format_articles_text(articles[:40]) # 토큰 용량 안정성을 위해 최대 40개 기사로 필터링
    papers_text = _format_papers_text(paper_candidates[:25]) # 상위 25개 논문 후보군 포맷
    
    # 공통 통합 뉴스레터 애널리저 인스턴스 획득
    analyzer = get_analyzer()
    
    # ── [A+B] 이번 주 TOP 10 & 3대 심층 분석 (JSON) ──
    # TOP 10은 보고서의 핵심 본문. JSON 파싱이 실패(주로 토큰 한도 초과로 인한 잘림)하면
    # top10이 비어 이메일·HTML이 공란이 되므로, 재시도 후에도 비면 명확히 실패시킨다.
    logger.info("[LLM 1/5] TOP 10 및 TOP 3 심층 분석 연산 중...")
    top10_detail_data = {"top10": [], "top3_detail": []}
    prompt_main = MAIN_ANALYSIS_PROMPT.format(articles_text=articles_text)
    for attempt in range(1, 4):  # 최대 3회 재시도
        try:
            raw_res = analyzer._call(prompt_main, len(articles[:40]))
            parsed = _parse_json_block(raw_res)
            if parsed and isinstance(parsed, dict) and parsed.get("top10"):
                top10_detail_data = parsed
                logger.info(f"  → TOP 10 선별 완료 (선별 건수: {len(top10_detail_data.get('top10', []))}개, 시도 {attempt})")
                break
            logger.error(f"  ❌ [오류] TOP 10 JSON 파싱 실패 또는 top10 공란 (시도 {attempt}/3)")
        except Exception as e:
            logger.error(f"  ❌ [오류] TOP 10 분석 실패 (시도 {attempt}/3): {e}")

    if not top10_detail_data.get("top10"):
        # 부분(잘린) 보고서를 저장/발송하지 않도록 전체 실행을 중단시킨다.
        raise RuntimeError(
            "TOP 10 분석 결과가 비어 있습니다. 잘린/불완전 보고서 저장을 방지하기 위해 중단합니다."
        )
        
    # ── [C] 주요 AI 기업 동향 (Markdown) ──
    logger.info("[LLM 2/5] 주요 AI 기업 주간 동향 마크다운 생성 중...")
    company_trends_md = "## 🏢 주요 AI 기업 및 서비스 동향\n_데이터 수집 지연으로 요약을 생략합니다._"
    try:
        prompt_comp = COMPANY_TRENDS_PROMPT.format(articles_text=articles_text)
        raw_res = analyzer._call(prompt_comp, len(articles[:40]))
        if raw_res and len(raw_res.strip()) > 50:
            parsed = _parse_json_block(raw_res)
            unwrapped = _unwrap_md_response(raw_res, parsed)
            if unwrapped:
                company_trends_md = unwrapped
                logger.info("  → 주요 기업 동향: JSON 래퍼에서 텍스트 추출")
            else:
                company_trends_md = raw_res.strip()
            logger.info("  → 주요 기업 동향 분석 완료")
    except Exception as e:
        logger.error(f"  ❌ [오류] 기업 동향 분석 에러: {e}")
        
    # ── [D] 주간 AI 실용 팁 (JSON) ──
    logger.info("[LLM 3/5] 업무용 실용 AI 팁 2선 도출 중...")
    weekly_tips_data = []
    try:
        prompt_tip = WEEKLY_TIP_PROMPT
        # 팁 도출의 참신성을 위해 수집 기사 텍스트 일부 제공
        prompt_tip = prompt_tip + f"\n\n[수집 참고 정보]\n{articles_text[:4000]}"
        raw_res = analyzer._call(prompt_tip, len(articles[:40]))
        parsed = _parse_json_block(raw_res)
        if parsed and isinstance(parsed, list):
            weekly_tips_data = parsed
            logger.info(f"  → 실용 AI 팁 도출 완료 ({len(weekly_tips_data)}개 도출)")
        else:
            logger.error("  ❌ [오류] 실용 팁 JSON 파싱 실패")
    except Exception as e:
        logger.error(f"  ❌ [오류] 실용 팁 도출 에러: {e}")
        
    # ── [F] cs.AI 논문 엄선 3선 (JSON) ──
    logger.info("[LLM 4/5] arXiv cs.AI 논문 최종 2~3편 엄선 중...")
    paper_picks_data = []
    try:
        prompt_paper = PAPER_PICK_PROMPT.format(papers_text=papers_text)
        raw_res = analyzer._call(prompt_paper, len(paper_candidates[:25]))
        parsed = _parse_json_block(raw_res)
        if parsed and isinstance(parsed, list):
            paper_picks_data = parsed
            logger.info(f"  → 주목 논문 최종 엄선 완료 ({len(paper_picks_data)}편 선별)")
        else:
            logger.error("  ❌ [오류] 논문 엄선 JSON 파싱 실패")
    except Exception as e:
        logger.error(f"  ❌ [오류] 논문 분석 에러: {e}")
        
    # ── [H] 차주 전망 및 모니터링 포인트 (Markdown) ──
    logger.info("[LLM 5/5] 차주 AI 시장 전망 및 방향성 예측 중...")
    outlook_md = "## 🔮 차주 AI 모니터링 포인트 및 전망\n_데이터 수집 지연으로 전망을 생략합니다._"
    try:
        prompt_out = OUTLOOK_PROMPT.format(articles_text=articles_text)
        raw_res = analyzer._call(prompt_out, len(articles[:40]))
        if raw_res and len(raw_res.strip()) > 50:
            parsed = _parse_json_block(raw_res)
            unwrapped = _unwrap_md_response(raw_res, parsed)
            if unwrapped:
                outlook_md = unwrapped
                logger.info("  → 차주 전망: JSON 래퍼에서 텍스트 추출")
            else:
                outlook_md = raw_res.strip()
            logger.info("  → 차주 전망 분석 완료")
    except Exception as e:
        logger.error(f"  ❌ [오류] 전망 분석 에러: {e}")
        
    # ── [G] 이슈 카테고리 통계 (Category Stats) ──
    category_list = [item.get("category", "기타") for item in top10_detail_data.get("top10", [])]
    category_counts = {}
    for cat in ["model", "service", "research", "policy", "industry", "infra", "investment"]:
        category_counts[cat] = category_list.count(cat)
        
    logger.info("=" * 60)
    logger.info("주간 AI 이슈 브리핑 — 모든 LLM 분석 작업 성공적 완료")
    logger.info("=" * 60)
    
    return {
        "issue_date": issue_date,
        "period": period,
        "top10": top10_detail_data.get("top10", []),
        "top3_detail": top10_detail_data.get("top3_detail", []),
        "company_trends": company_trends_md,
        "weekly_tips": weekly_tips_data,
        "stock_snapshots": stock_snapshots,
        "paper_picks": paper_picks_data,
        "category_stats": category_counts,
        "next_week_outlook": outlook_md,
    }


if __name__ == "__main__":
    # 로컬 수집기 연계 간이 테스트
    from core.ai_issue.collector import collect_weekly_raw_data
    raw = collect_weekly_raw_data()
    res = analyze_weekly_data(raw)
    print("Combined test completed.")
