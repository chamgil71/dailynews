# config/sources/en_news.py
# 영어 뉴스 RSS 소스 목록

EN_GENERAL = {
    "global_news": {
        "lang": "en",
        "label": "글로벌 종합",
        "feeds": [
            "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",     # NYT
            "https://feeds.bbci.co.uk/news/rss.xml",                         # BBC
            "https://feeds.skynews.com/feeds/rss/world.xml",                 # Sky News
            "https://www.theguardian.com/world/rss",                         # Guardian
            "https://feeds.npr.org/1001/rss.xml",                            # NPR
            "https://www.aljazeera.com/xml/rss/all.xml",                     # Al Jazeera
        ],
    },
}

EN_TECH = {
    "technology": {
        "lang": "en",
        "label": "글로벌 기술",
        "feeds": [
            "https://feeds.arstechnica.com/arstechnica/index",               # Ars Technica
            "https://www.theverge.com/rss/index.xml",                        # The Verge
            "https://techcrunch.com/feed/",                                  # TechCrunch
            "https://www.technologyreview.com/feed/",                        # MIT Tech Review
            "https://www.zdnet.com/news/rss.xml",                            # ZDNet
            # feeds.wired.com — HTML 반환으로 접근 불가 (제거)
            "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",  # Google News Tech
        ],
    },
}

EN_AI = {
    "ai_ml": {
        "lang": "en",
        "label": "AI·ML",
        "feeds": [
            "https://venturebeat.com/category/ai/feed/",                            # VentureBeat AI
            "https://www.artificialintelligence-news.com/feed/",                    # AI News
            "https://aiweekly.co/issues.rss",                                       # AI Weekly
            "https://www.technologyreview.com/topic/artificial-intelligence/feed/", # MIT Tech Review AI
            "https://www.wired.com/feed/tag/ai/latest/rss",                         # Wired AI
            # DeepLearning.AI The Batch — 404 (제거)
            # Stanford HAI — 404 (제거)
            # OECD.AI — 404 (제거)
            "https://news.google.com/rss/search?q=artificial+intelligence+LLM&hl=en-US&gl=US&ceid=US:en",  # Google News AI
        ],
    },
}

EN_ECONOMY = {
    "economy": {
        "lang": "en",
        "label": "글로벌 경제",
        "feeds": [
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",         # CNBC
            "https://feeds.bloomberg.com/markets/news.rss",                  # Bloomberg
            "https://www.ft.com/rss/home/us",                                # Financial Times
            "https://feeds.reuters.com/reuters/businessNews",                # Reuters Business
        ],
    },
}

EN_STARTUP = {
    "startup": {
        "lang": "en",
        "label": "스타트업·VC",
        "feeds": [
            "https://techcrunch.com/category/startups/feed/",                # TechCrunch Startups
            "https://venturebeat.com/category/business/feed/",               # VentureBeat Business
            "https://www.crunchbase.com/rss/home.rss",                       # Crunchbase
        ],
    },
}
