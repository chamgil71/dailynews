# core/ai_issue/collector.py
"""
주간 AI 이슈 브리핑용 데이터 수집 모듈.
1. AI 전문 블로그/미디어 RSS 피드 수집 (최근 7일간)
2. 일일 뉴스레터 아카이브(publish/news/*.json) 내 AI 뉴스 2차 필터링 및 병합
3. arXiv cs.AI/cs.LG/cs.CL 논문 수집 및 키워드 가중치 기반 1차 스코어링 (30개 후보 압축)
4. yfinance 연동을 통한 주요 AI 빅테크 주간 등락 취합 및 예외 완벽 복구
"""
from __future__ import annotations

import logging
import re
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
import time

import feedparser
import requests
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_ROOT = str(Path(__file__).parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from config.ai_issue_sources import (
    SCORING_KEYWORDS,
    AI_BLOG_SOURCES,
    AI_MEDIA_SOURCES,
    ARXIV_SOURCES,
    DOMESTIC_SOURCES,
    FUNDING_SOURCES
)

logger = logging.getLogger(__name__)

# yfinance 임포트 (없으면 pip install)
try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf


def _normalize_url(url: str) -> str:
    """URL의 중복 판정을 위해 쿼리 파라미터 및 프로토콜을 정규화합니다."""
    url = url.strip().split("?")[0].split("#")[0]
    url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    if url.endswith("/"):
        url = url[:-1]
    return url


def _parse_pubdate(entry) -> datetime:
    """feedparser 엔트리에서 발행 날짜를 안전하게 파싱하여 timezone-aware KST datetime으로 변환합니다."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        # UTC 타임스탬프로 변환 후 KST(UTC+9) 타임존 적용
        utc_dt = datetime(*parsed[:6], tzinfo=timezone.utc)
        return utc_dt.astimezone(timezone(timedelta(hours=9)))
    
    # 파싱 실패 시 현재 시간 KST 반환
    return datetime.now(timezone(timedelta(hours=9)))


def fetch_rss_articles(sources: dict[str, str], start_date: datetime, end_date: datetime) -> list[dict]:
    """지정된 RSS 소스들로부터 발행 범위(start_date ~ end_date) 내의 기사를 수집합니다."""
    articles = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    for name, url in sources.items():
        try:
            logger.info(f"[RSS 수집] '{name}' 피드 긁어오는 중...")
            res = requests.get(url, headers=headers, timeout=12, verify=False)
            if res.status_code != 200:
                logger.warning(f"[RSS 수집] '{name}' HTTP 에러 {res.status_code}")
                continue
            
            feed = feedparser.parse(res.text)
            feed_cnt = 0
            
            for entry in feed.entries:
                pub_date = _parse_pubdate(entry)
                
                # 날짜 범위 체크 (KST 기준)
                if start_date <= pub_date <= end_date:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    summary = entry.get("summary", entry.get("description", "")).strip()
                    # HTML 태그 제거
                    summary = re.sub(r"<[^>]*>", "", summary)
                    
                    if title and link:
                        articles.append({
                            "title": title,
                            "link": link,
                            "summary": summary[:200],
                            "source": name,
                            "date": pub_date.strftime("%Y-%m-%d"),
                            "pub_date": pub_date
                        })
                        feed_cnt += 1
                        
            logger.info(f"  → '{name}'에서 범위 내 기사 {feed_cnt}개 수집 완료")
        except Exception as e:
            logger.warning(f"  ⚠ '{name}' 수집 중 에러 발생: {e}")
            
    return articles


def filter_daily_news_archives(start_date: datetime, end_date: datetime) -> list[dict]:
    """과거 일일 뉴스레터 아카이브(publish/news/*.json)에서 AI 키워드가 매칭된 기사들을 2차 필터링 및 병합합니다."""
    filtered_articles = []
    publish_news_dir = Path(_ROOT) / "publish" / "news"
    
    if not publish_news_dir.exists():
        logger.info(f"[아카이브 필터] publish/news 디렉토리가 없어 아카이브 재활용을 건너뜁니다.")
        return []
    
    # 7일간의 날짜 목록 순회
    current = start_date
    ai_pattern = re.compile(
        r"\b(AI|LLM|GPT|Claude|Gemini|Transformer|RAG|인공지능|머신러닝|딥러닝|엔비디아|NVIDIA)\b",
        re.IGNORECASE
    )
    
    while current <= end_date:
        date_str = current.strftime("%Y-%m-%d")
        json_path = publish_news_dir / f"{date_str}.json"
        
        if json_path.exists():
            try:
                import json
                data = json.loads(json_path.read_text(encoding="utf-8"))
                news_items = data.get("news_en", []) + data.get("news_ko", [])
                matched_cnt = 0
                
                for item in news_items:
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    
                    # 제목 또는 요약에 AI 관련 주요 키워드가 매칭되는 경우 수집 대상화
                    if ai_pattern.search(title) or ai_pattern.search(summary):
                        filtered_articles.append({
                            "title": title,
                            "link": item.get("link", ""),
                            "summary": summary,
                            "source": f"Daily News ({item.get('label', 'General')})",
                            "date": date_str,
                            "pub_date": current
                        })
                        matched_cnt += 1
                if matched_cnt > 0:
                    logger.info(f"[아카이브 필터] {date_str}에서 AI 뉴스레터 기사 {matched_cnt}건 확보")
            except Exception as e:
                logger.warning(f"[아카이브 필터] {date_str} 파싱 중 에러: {e}")
                
        current += timedelta(days=1)
        
    return filtered_articles


def collect_paper_candidates(start_date: datetime, end_date: datetime, top_n: int = 30) -> list[dict]:
    """arXiv cs.AI/cs.LG/cs.CL 소스로부터 논문들을 긁어와 키워드 가중치 스코어링을 통해 최적의 30개 후보군으로 수축시킵니다."""
    logger.info("=" * 60)
    logger.info(f"arXiv cs.AI/cs.LG/cs.CL 논문 수집 및 1차 스코어링 필터링 시작 (목표: {top_n}선)")
    logger.info("=" * 60)
    
    raw_papers = fetch_rss_articles(ARXIV_SOURCES, start_date, end_date)
    
    if not raw_papers:
        logger.warning("cs.AI 수집된 논문이 존재하지 않아 논문 픽 단계를 생략합니다.")
        return []
    
    scored_papers = []
    seen_normalized_links = set()
    
    for paper in raw_papers:
        norm_url = _normalize_url(paper["link"])
        if norm_url in seen_normalized_links:
            continue
        seen_normalized_links.add(norm_url)
        
        # 스코어링 연산 (제목 + 요약문 내 대소문자 무관 키워드 가중치 합산)
        score = 0
        search_text = f"{paper['title']} {paper['summary']}".lower()
        
        for kw, weight in SCORING_KEYWORDS.items():
            # 단어 경계(\b)를 고려한 정규식으로 정확히 일치하는 단어에 대해서 가중치 부여
            pattern = re.compile(rf"\b{re.escape(kw.lower())}\b")
            matches = len(pattern.findall(search_text))
            score += matches * weight
            
        paper["score"] = score
        scored_papers.append(paper)
        
    # 높은 스코어순, 점수가 같으면 최신순 정렬
    scored_papers.sort(key=lambda x: (x["score"], x["pub_date"]), reverse=True)
    
    # 상위 N개 후보 최종 추출
    final_candidates = scored_papers[:top_n]
    logger.info(f"arXiv 전수 수집 {len(scored_papers)}건 중 1차 키워드 채점을 통해 {len(final_candidates)}개 후보군 압축 완료")
    
    for i, p in enumerate(final_candidates[:5], 1):
        logger.info(f"  [Top Scored Paper #{i}] 점수: {p['score']} | {p['title'][:65]}...")
        
    return final_candidates


def collect_stock_snapshots() -> list[dict]:
    """주요 AI 관련 테마 주식 5종(NVDA, MSFT, GOOGL, META, AMD)의 주간 등락 수치를 수집 및 안전 수집 처리합니다."""
    logger.info("[Stock 수집] 주요 AI 종목 주간 변동 데이터 취합 중...")
    tickers = {
        "NVDA": "엔비디아",
        "MSFT": "마이크로소프트",
        "GOOGL": "알파벳(구글)",
        "META": "메타",
        "AMD": "AMD"
    }
    
    snapshots = []
    for ticker_symbol, name in tickers.items():
        try:
            # 안전하게 Ticker 정보 획득
            t = yf.Ticker(ticker_symbol)
            # 최근 7일(주간) 가격 히스토리 가져오기
            hist = t.history(period="7d")
            
            if hist.empty or len(hist) < 2:
                logger.warning(f"  ⚠ {ticker_symbol} 주가 히스토리 부족. 전 거래일 기준 폴백 시도...")
                snapshots.append({
                    "ticker": ticker_symbol,
                    "name": name,
                    "weekly_change_pct": 0.0,
                    "note": "데이터 일시 지연 (N/A)"
                })
                continue
                
            close_prices = hist["Close"].tolist()
            open_price = close_prices[0]
            close_price = close_prices[-1]
            
            # 주간 누적 등락률 연산
            change_pct = ((close_price - open_price) / open_price) * 100
            
            snapshots.append({
                "ticker": ticker_symbol,
                "name": name,
                "weekly_change_pct": round(change_pct, 2),
                "note": f"종가: ${close_price:.2f} (주간 시작 ${open_price:.2f})"
            })
            logger.info(f"  📈 {ticker_symbol} ({name}) 주간 등락: {change_pct:+.2f}% 취합 완료")
            
        except Exception as e:
            logger.error(f"  ❌ {ticker_symbol} 주가 데이터 수집 에러 (Urgent Fallback): {e}")
            snapshots.append({
                "ticker": ticker_symbol,
                "name": name,
                "weekly_change_pct": 0.0,
                "note": "수집 에러로 데이터 일시 누락"
            })
            
    return snapshots


def collect_weekly_raw_data(target_date: str | None = None) -> dict:
    """주간 AI 동향 분석용 기사, 논문 후보, 빅테크 주가 정보를 일체 취합하여 딕셔너리로 반환합니다."""
    if not target_date:
        # 기본값: 오늘 KST 날짜
        target_date = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d")
        
    try:
        # 발행 기준일(일요일) KST 타임존 날짜 획득
        issue_date = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone(timedelta(hours=9)))
    except ValueError:
        issue_date = datetime.now(timezone(timedelta(hours=9)))
        
    # 수집 기준 범위: 일요일 00:00 KST ~ 토요일 23:59 KST (직전 7일)
    # KST 기준 날짜 연산
    end_date = issue_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    start_date = (end_date - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    logger.info("=" * 60)
    logger.info(f"주간 수집 범위 확정: {start_date.strftime('%Y-%m-%d %H:%M KST')} ~ {end_date.strftime('%Y-%m-%d %H:%M KST')}")
    logger.info("=" * 60)
    
    # 1. AI 전문 블로그 RSS 수집
    blog_articles = fetch_rss_articles(AI_BLOG_SOURCES, start_date, end_date)
    
    # 2. AI 전문 미디어 RSS 수집
    media_articles = fetch_rss_articles(AI_MEDIA_SOURCES, start_date, end_date)
    
    # 3. 국내 AI 미디어 RSS 수집
    domestic_articles = fetch_rss_articles(DOMESTIC_SOURCES, start_date, end_date)
    
    # 4. 투자/펀딩 RSS 수집
    funding_articles = fetch_rss_articles(FUNDING_SOURCES, start_date, end_date)
    
    # 5. 기존 데일리 뉴스 아카이브 내 AI 뉴스 필터링
    archive_articles = filter_daily_news_archives(start_date, end_date)
    
    # 6. cs.AI 논문 후보군 1차 필터 스코어링 수집 (arXiv cs.AI)
    paper_candidates = collect_paper_candidates(start_date, end_date, top_n=30)
    
    # 7. yfinance 주가 변동 스냅샷 취합
    stock_snapshots = collect_stock_snapshots()
    
    # ── 전체 수집 기사 일체 병합 및 정규화 중복 제거 ──
    all_articles = blog_articles + media_articles + domestic_articles + funding_articles + archive_articles
    
    seen_normalized_links = set()
    deduplicated_articles = []
    
    for art in all_articles:
        norm_url = _normalize_url(art["link"])
        if norm_url in seen_normalized_links:
            continue
        seen_normalized_links.add(norm_url)
        # datetime 객체 제거 (JSON 직렬화 목적)
        art_clean = {k: v for k, v in art.items() if k != "pub_date"}
        deduplicated_articles.append(art_clean)
        
    logger.info("=" * 60)
    logger.info(f"수집 최종 통합 완료:")
    logger.info(f"  - 중복 제거된 총 일반 기사 수: {len(deduplicated_articles)}개")
    logger.info(f"  - 1차 채점 압축된 arXiv cs.AI 논문 후보 수: {len(paper_candidates)}개")
    logger.info(f"  - yfinance 빅테크 연계 수: {len(stock_snapshots)}종")
    logger.info("=" * 60)
    
    # datetime 객체 제거한 cs.AI 후보군 JSON 직렬화 클렌징
    cleaned_paper_candidates = []
    for paper in paper_candidates:
        cleaned_paper_candidates.append({k: v for k, v in paper.items() if k != "pub_date"})
        
    return {
        "issue_date": target_date,
        "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
        "articles": deduplicated_articles,
        "paper_candidates": cleaned_paper_candidates,
        "stock_snapshots": stock_snapshots
    }


if __name__ == "__main__":
    # 로컬 테스트용
    data = collect_weekly_raw_data()
    print(f"Test run completed: {len(data['articles'])} articles found.")
