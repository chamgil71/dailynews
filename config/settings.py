# config/settings.py
import os

# ── LLM 설정 ──────────────────────────────────────────────────────────────────
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "gemini")   # "gpt" | "claude" | "gemini"
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")

# ── GPT 모델 설정 ─────────────────────────────────────────────────────────────
GPT_MODEL_FULL     = "gpt-4o"
GPT_MODEL_MINI     = "gpt-4o-mini"
GPT_MINI_THRESHOLD = 20          # 뉴스 ≤ 20건이면 mini 자동 선택

# ── Claude 모델 설정 ──────────────────────────────────────────────────────────
CLAUDE_MODEL_FULL  = "claude-opus-4-5"
CLAUDE_MODEL_MINI  = "claude-haiku-4-5-20251001"
CLAUDE_MINI_THRESHOLD = 20

# ── Gemini 모델 설정 ──────────────────────────────────────────────────────────
GEMINI_MODEL_FULL  = "gemini-3.1-flash-lite-preview"
GEMINI_MODEL_MINI  = "gemini-3.1-flash-lite-preview"
GEMINI_MINI_THRESHOLD = 40

# ── 수집 설정 ─────────────────────────────────────────────────────────────────
MAX_ENTRIES_PER_FEED    = 8
MAX_TITLES_TO_ANALYZE   = 40
RSS_TIMEOUT_SECONDS     = 10

# ── 캐시 설정 ─────────────────────────────────────────────────────────────────
CACHE_ENABLED   = True
CACHE_FILE      = ".cache/last_urls.json"
CACHE_TTL_HOURS = 23

# ── 이메일 설정 ───────────────────────────────────────────────────────────────
RESEND_API_KEY       = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM           = "onboarding@resend.dev"
RECIPIENT_EMAILS     = [e.strip() for e in os.getenv("RECIPIENT_EMAILS", "").split(",") if e.strip()]
EMAIL_SUBJECT        = "📰 Daily News Brief — {date}"
UNSUBSCRIBE_SECRET   = os.getenv("UNSUBSCRIBE_SECRET", "")
SITE_BASE_URL        = os.getenv("SITE_BASE_URL", "").rstrip("/")

# ── GitHub Contents API (구독 취소 기록용) ────────────────────────────────────
GH_CONTENTS_TOKEN    = os.getenv("GH_CONTENTS_TOKEN", "")
GITHUB_REPOSITORY    = os.getenv("GITHUB_REPOSITORY", "")   # "owner/repo" 형식

# ── 리포트 ────────────────────────────────────────────────────────────────────
REPORTS_DIR     = "reports"
REPORT_FILENAME = "news_{date}.md"
