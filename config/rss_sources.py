# config/rss_sources.py
# 카테고리별 RSS 피드 — lang 필드로 한국어/영어 분리 처리

RSS_FEEDS = {

    "global_news": {
        "lang": "en",
        "label": "글로벌 종합",
        "feeds": [
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://feeds.skynews.com/feeds/rss/world.xml",
        ],
    },

    "technology": {
        "lang": "en",
        "label": "기술",
        "feeds": [
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.theverge.com/rss/index.xml",
            "https://techcrunch.com/feed/",
        ],
    },

    "economy": {
        "lang": "en",
        "label": "경제·금융",
        "feeds": [
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        ],
    },

    "ai_ml": {
        "lang": "en",
        "label": "AI·ML",
        "feeds": [
            "https://venturebeat.com/category/ai/feed/",
            "https://www.artificialintelligence-news.com/feed/",
        ],
    },

    "korean_news": {
        "lang": "ko",
        "label": "국내 종합",
        "feeds": [
            "https://www.yonhapnewstv.co.kr/category/news/headline/feed/",
            "https://rss.etnews.com/Section901.xml",
        ],
    },

    "korean_economy": {
        "lang": "ko",
        "label": "국내 경제",
        "feeds": [
            "https://www.hankyung.com/feed/economy",
            #"https://rss.mt.co.kr/news/rssView.php?pCodeList=rss001",
        ],
    },
}
