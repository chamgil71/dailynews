# config/settings.py
import os

# ── LLM 설정 ──────────────────────────────────────────────────────────────────
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "gpt")   # "gpt" | "claude" | "gemini"
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY", "")

# 조건부 모델 다운그레이드: 뉴스 건수가 적으면 mini 사용
GPT_MODEL_FULL      = "gpt-4o"
GPT_MODEL_MINI      = "gpt-4o-mini"
GPT_MINI_THRESHOLD  = 20          # 뉴스 ≤ 20건이면 mini 자동 선택

# ── 수집 설정 ─────────────────────────────────────────────────────────────────
MAX_ENTRIES_PER_FEED    = 5       # 피드당 최대 기사 수
MAX_TITLES_TO_ANALYZE   = 35      # AI에 전송할 최대 제목 수 (토큰 절감)
RSS_TIMEOUT_SECONDS     = 10

# ── 캐시 설정 (중복 기사 제거) ────────────────────────────────────────────────
CACHE_ENABLED   = True
CACHE_FILE      = ".cache/last_urls.json"
CACHE_TTL_HOURS = 23

# ── 이메일 설정 ───────────────────────────────────────────────────────────────
RESEND_API_KEY  = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM      = "news@resend.dev"
EMAIL_TO        = [e.strip() for e in os.getenv("RECIPIENT_EMAIL", "").split(",") if e.strip()]
EMAIL_SUBJECT   = "📰 Daily News Brief — {date}"

# ── 리포트 ────────────────────────────────────────────────────────────────────
REPORTS_DIR     = "reports"
REPORT_FILENAME = "news_{date}.md"
