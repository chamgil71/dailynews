# scripts/validate_ai_issue_sources.py
"""
AI Issue Weekly Report용 RSS 소스 유효성 검증 스크립트 (Windows 콘솔 인코딩 & SSL 안정화 버전).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Windows 콘솔 cp949 이모지 및 한글 출력 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

_ROOT = str(Path(__file__).parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import feedparser
import requests
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("validate_sources")

SOURCES = {
    # ── AI 기업 공식 블로그 ──
    "OpenAI News": "https://openai.com/news/rss",
    "Anthropic News": "https://www.anthropic.com/news/rss",
    "Google DeepMind": "https://deepmind.google/blog/rss/",
    "Google AI Blog": "https://blog.google/technology/ai/rss",
    "Meta AI Blog": "https://ai.meta.com/blog/rss/",
    "Microsoft AI": "https://blogs.microsoft.com/ai/feed/",
    "Mistral AI": "https://mistral.ai/news/rss",
    "Cohere Blog": "https://cohere.com/blog/rss",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    
    # ── AI 전문 미디어 ──
    "The Decoder": "https://the-decoder.com/feed/",
    "AI News": "https://www.artificialintelligence-news.com/feed/",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/index",
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/ai/feed/",
    "The Verge AI": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "MIT Tech Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    
    # ── 연구·논문 (arXiv/HF) ──
    "arXiv cs.AI": "https://arxiv.org/rss/cs.AI",
    "arXiv cs.LG": "https://arxiv.org/rss/cs.LG",
    "arXiv cs.CL": "https://arxiv.org/rss/cs.CL",
    "HF Daily Papers": "https://huggingface.co/papers/rss",
    "Papers With Code": "https://paperswithcode.com/latest/rss",
    
    # ── 국내 AI/IT 미디어 ──
    "AI타임스": "https://www.aitimes.com/rss/allArticle.xml",
    "전자신문": "https://rss.etnews.com/Section901.xml",
    "ZDNet Korea": "https://zdnet.co.kr/rss/news.xml",
    "Bloter": "https://www.bloter.net/feed",
    
    # ── 투자·펀딩 ──
    "TechCrunch Funding": "https://techcrunch.com/tag/funding/feed/",
    "VentureBeat Funding": "https://venturebeat.com/category/deals/feed/",
}

def check_source(name: str, url: str) -> tuple[bool, int, str]:
    """해당 URL 피드가 정상 응답하는지 및 글의 개수를 체크합니다."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    try:
        # verify=False 를 활용해 로컬 프록시/보안 프로그램 SSL 오동작 방지
        res = requests.get(url, headers=headers, timeout=12, verify=False)
        if res.status_code != 200:
            return False, 0, f"HTTP Error {res.status_code}"
        
        feed = feedparser.parse(res.text)
        
        if feed.bozo:
            exc = feed.bozo_exception
            err_msg = str(exc) if exc else "XML Parsing Warning"
            if len(feed.entries) > 0:
                return True, len(feed.entries), f"Parsed with warning: {err_msg[:60]}"
            return False, 0, f"Parsing Failed: {err_msg[:60]}"
            
        return True, len(feed.entries), "Success"
        
    except requests.exceptions.Timeout:
        return False, 0, "Connection Timeout"
    except Exception as e:
        return False, 0, f"Error: {str(e)[:60]}"

def main():
    logger.info("=" * 70)
    logger.info("AI Issue Weekly RSS 소스 유효성 검증 시작 (KST)")
    logger.info("=" * 70)
    
    success_count = 0
    failure_count = 0
    
    for idx, (name, url) in enumerate(SOURCES.items(), 1):
        logger.info(f"[{idx}/{len(SOURCES)}] '{name}' 연결 확인 중...")
        ok, entry_cnt, msg = check_source(name, url)
        
        if ok:
            logger.info(f"  [SUCCESS] 아이템 개수: {entry_cnt}개 | 상태: {msg}")
            success_count += 1
        else:
            logger.warning(f"  [FAILURE] 상태: {msg} | URL: {url}")
            failure_count += 1
            
    logger.info("=" * 70)
    logger.info(f"검증 완료: 총 {len(SOURCES)}개 중 성공: {success_count}개 | 실패: {failure_count}개")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
