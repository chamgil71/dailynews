# config/rss_sources.py
# ──────────────────────────────────────────────────────────────────────────────
# 사용할 소스를 아래에서 주석/해제로 선택하세요.
# 소스 상세 목록: config/sources/ko_news.py / config/sources/en_news.py
# ──────────────────────────────────────────────────────────────────────────────

from config.sources.ko_news import (
    KO_GENERAL,
    KO_ECONOMY,
    KO_TECH,
    KO_STOCK,
    # KO_REAL_ESTATE,   # 필요 시 주석 해제
    # KO_POLITICS,      # 필요 시 주석 해제
    # KO_INTERNATIONAL, # 필요 시 주석 해제
)

# from config.sources.en_news import (
#     EN_GENERAL,
#     EN_TECH,
#     EN_AI,
#     EN_ECONOMY,
#     EN_STARTUP,
# )

# ── 최종 사용할 피드 조합 ─────────────────────────────────────────────────────
RSS_FEEDS = {
    **KO_GENERAL,
    **KO_ECONOMY,
    **KO_TECH,
    **KO_STOCK,
    # **KO_REAL_ESTATE,
    # **KO_POLITICS,
    # **KO_INTERNATIONAL,
    # **EN_GENERAL,
    # **EN_TECH,
    # **EN_AI,
    # **EN_ECONOMY,
    # **EN_STARTUP,
}
