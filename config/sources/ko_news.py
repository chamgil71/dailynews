# config/sources/ko_news.py
# 한국어 뉴스 RSS 소스 목록
# 사용법: rss_sources.py에서 원하는 카테고리만 import

KO_GENERAL = {
    "korean_general": {
        "lang": "ko",
        "label": "국내 종합",
        "feeds": [
            "https://www.yonhapnewstv.co.kr/category/news/headline/feed/",  # 연합뉴스TV
            "https://rss.koreaherald.com/rss/category/national/",            # 코리아헤럴드
            "https://www.hani.co.kr/rss/",                                   # 한겨레
            "https://www.khan.co.kr/rss/rssdata/khanAllNews.xml",            # 경향신문
            "https://www.ohmynews.com/rss/ohmynews.xml",                     # 오마이뉴스
        ],
    },
}

KO_ECONOMY = {
    "korean_economy": {
        "lang": "ko",
        "label": "국내 경제",
        "feeds": [
            "https://www.hankyung.com/feed/economy",                         # 한국경제
            "https://www.edaily.co.kr/rss/rss_economy.xml",                  # 이데일리
            "https://biz.chosun.com/rss/rss.htm",                            # 조선비즈
            "https://www.mk.co.kr/rss/40300001/",                            # 매일경제 경제
            "https://news.einfomax.co.kr/rss/allArticle.xml",                # 연합인포맥스
        ],
    },
}

KO_STOCK = {
    "korean_stock": {
        "lang": "ko",
        "label": "국내 증권·투자",
        "feeds": [
            "https://www.mk.co.kr/rss/40300003/",                            # 매일경제 증권
            "https://www.hankyung.com/feed/finance",                         # 한국경제 금융
            "https://www.sedaily.com/RSS/S0601",                             # 서울경제 증권
            "https://stock.mk.co.kr/rss/40300003/",                         # MK 주식
        ],
    },
}

KO_TECH = {
    "korean_tech": {
        "lang": "ko",
        "label": "국내 IT·기술",
        "feeds": [
            "https://rss.etnews.com/Section901.xml",                         # 전자신문 IT
            "https://www.aitimes.com/rss/allArticle.xml",                    # AI타임스
            "https://zdnet.co.kr/rss/?t=a",                                  # ZDNet Korea
            "https://www.itworld.co.kr/rss/feed",                            # ITWorld
            "https://www.bloter.net/feed",                                   # 블로터
        ],
    },
}

KO_REAL_ESTATE = {
    "korean_realestate": {
        "lang": "ko",
        "label": "국내 부동산",
        "feeds": [
            "https://land.naver.com/news/rss.nhn",                           # 네이버 부동산
            "https://www.hankyung.com/feed/realestate",                      # 한국경제 부동산
            "https://www.mk.co.kr/rss/50200011/",                            # 매일경제 부동산
        ],
    },
}

KO_POLITICS = {
    "korean_politics": {
        "lang": "ko",
        "label": "국내 정치",
        "feeds": [
            "https://www.hani.co.kr/rss/politics/",                          # 한겨레 정치
            "https://www.khan.co.kr/rss/rssdata/politics.xml",               # 경향 정치
            "https://www.mk.co.kr/rss/30100041/",                            # 매일경제 정치
        ],
    },
}

KO_INTERNATIONAL = {
    "korean_international": {
        "lang": "ko",
        "label": "국제 (한국어)",
        "feeds": [
            "https://www.hani.co.kr/rss/international/",                     # 한겨레 국제
            "https://www.yonhapnews.co.kr/rss/international.xml",            # 연합뉴스 국제
            "https://www.mk.co.kr/rss/30200030/",                            # 매일경제 국제
        ],
    },
}
