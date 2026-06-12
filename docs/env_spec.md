# 환경변수 명세서 (Environment Variable Specification)

> **최종 업데이트**: 2026-06-12
> **관리 원칙**
> - `.env` — 로컬 개발 실제값 (`.gitignore` 적용, 절대 커밋 금지)
> - `.env.example` — 키 이름과 설명만 git 추적 (실제값 없음)
> - **GitHub Secrets** — GitHub Actions CI/CD 운영값 (Settings → Secrets and variables → Actions)
> - **Vercel 환경변수** — Vercel 서버리스 함수(`/api/*.py`) 운영값 (Vercel 대시보드 → Settings → Environment Variables)
> - ⚠️ GitHub Secrets ≠ Vercel 환경변수 — 서로 공유되지 않음, 별도 등록 필요

---

## 범례

| 기호 | 의미 |
|---|---|
| ✅ 필수 | 없으면 해당 기능 동작 안 함 |
| 🔶 권장 | 없으면 제한적 동작 또는 경고 |
| ⬜ 선택 | 기본값 있음, 없어도 무방 |
| 🗑️ 레거시 | 현재 미사용, 삭제 대상 |

---

## 1. LLM API

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `LLM_PROVIDER` | ✅ 필수 | 사용할 LLM (`gemini`\|`claude`\|`gpt`) | 직접 입력 |
| `GEMINI_API_KEY` | ✅ 필수 | Gemini API 인증 키 | [Google AI Studio](https://aistudio.google.com/apikey) → **Create API Key** |
| `GEMINI_MODEL_FULL` | ⬜ 선택 | 고성능 분석 모델 재정의 | 직접 입력 (기본: `gemini-2.5-pro`) |
| `GEMINI_MODEL_MINI` | ⬜ 선택 | 경량 모델 재정의 | 직접 입력 (기본: `gemini-2.0-flash-lite`) |
| `GEMINI_MODEL_FALLBACK` | ⬜ 선택 | 과부하 시 백업 모델 | 직접 입력 (기본: `gemini-2.5-flash`) |
| `ANTHROPIC_API_KEY` | ⬜ 선택 | Claude API 키 | [Anthropic Console](https://console.anthropic.com/) → **API Keys** |
| `OPENAI_API_KEY` | ⬜ 선택 | OpenAI API 키 | [OpenAI Platform](https://platform.openai.com/api-keys) → **Create new secret key** |

---

## 2. 이메일 (Gmail SMTP)

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `GMAIL_USER` | ✅ 필수 | 발송 Gmail 주소 | 직접 입력 |
| `GMAIL_APP_PASSWORD` | ✅ 필수 | Gmail 앱 비밀번호 (16자리) | ① Google 계정 → 보안 → **2단계 인증 ON** → ② **앱 비밀번호** → 앱: 메일, 기기: 기타 → 생성 ※ 일반 로그인 비밀번호 아님 |
| `RECIPIENT_EMAILS` | 🔶 권장 | Supabase 장애 시 비상 폴백 수신자 (쉼표 구분) | 직접 입력 |
| `UNSUBSCRIBE_SECRET` | 🔶 권장 | 이메일 구독취소 링크 위변조 방지 HMAC 서명값 | 직접 생성: `python -c "import secrets; print(secrets.token_hex(16))"` ※ GitHub Secrets · Vercel 환경변수 모두 동일 값 사용 |

---

## 3. 사이트 / Vercel 배포

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `SITE_BASE_URL` | ✅ 필수 | 배포 사이트 URL (끝에 `/` 포함) | 직접 입력: `https://ms-dailynews.vercel.app/` |
| `SITE_TITLE` | ⬜ 선택 | 사이트 타이틀 | 직접 입력 (기본값: `AI News Brief`) |
| `SUBSCRIBE_URL` | ⬜ 선택 | 구독 폼 URL | 직접 입력 (기본값: `{SITE_BASE_URL}/subscribe`) |

---

## 4. Supabase (구독 시스템)

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `SUPABASE_URL` | ✅ 필수 | 프로젝트 REST URL | [Supabase 대시보드](https://supabase.com/dashboard) → 프로젝트 → **Settings → API** → "Project URL" |
| `SUPABASE_SERVICE_KEY` | ✅ 필수 | 서비스 역할 키 (RLS 우회, 서버 전용) | 동일 페이지 → **"service_role"** 행 → 눈 아이콘 클릭 ※ "anon" 키(`VITE_SUPABASE_ANON_KEY`) 아님 |

> **⚠️ 중요**: `SUPABASE_SERVICE_KEY`는 두 곳에 별도 등록해야 합니다.
> - **GitHub Secrets** → GitHub Actions 워크플로우에서 사용
> - **Vercel 환경변수** → `/api/subscribe`, `/api/unsubscribe` 등 서버리스 함수에서 사용
>
> 한쪽만 등록하면 나머지 환경에서 **401 Unauthorized** 오류 발생

### Vercel 환경변수 등록 방법
```
Vercel 대시보드 → 프로젝트 선택 → Settings → Environment Variables
→ "Add New" → 변수명/값 입력 → Save
```
Vercel에 등록해야 하는 최소 변수:
```
SUPABASE_SERVICE_KEY   = eyJhbGci... (service_role 키)
UNSUBSCRIBE_SECRET     = (위 생성값)
```

---

## 5. GitHub (레거시)

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `GH_CONTENTS_TOKEN` | 🗑️ 레거시 | 구 구독취소 파일 API용 — Supabase 전환으로 미사용 | GitHub → Settings → **Developer settings** → Personal access tokens → Fine-grained → 권한: Contents(Read & Write), Metadata(Read) |
| `GITHUB_REPOSITORY` | 🗑️ 레거시 | 구 구독취소 저장소 경로 | 직접 입력: `chamgil71/dailynews` |

---

## 6. 네이버 API

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `NAVER_CLIENT_ID` | 🔶 권장 | 네이버 검색 API 클라이언트 ID | [네이버 개발자센터](https://developers.naver.com/apps) → 애플리케이션 등록 → **사용 API: "검색" 체크** → Client ID 복사 |
| `NAVER_CLIENT_SECRET` | 🔶 권장 | 네이버 검색 API 시크릿 | 동일 앱 → Client Secret 복사 |

> 미설정 시 주식 국내뉴스 보완 건너뜀 (주식 분석 자체는 정상 진행)

---

## 7. Notion

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `NOTION_API_KEY` | 🔶 권장 | Internal Integration 토큰 | [notion.so/my-integrations](https://www.notion.so/my-integrations) → **+ New integration** → Internal → Submit → "Internal Integration Secret" 복사 (`ntn_`으로 시작) |
| `NOTION_DATABASE_ID_NEWS` | 🔶 권장 | 뉴스 브리핑 DB ID | 노션 DB 페이지 열기 → 주소창 URL → `notion.so/xxx/`**여기서 32자리**`?v=...` |
| `NOTION_DATABASE_ID_STOCK` | 🔶 권장 | 주식 시황 DB ID | 동일 방법 |
| `NOTION_DATABASE_ID_AI_ISSUE` | 🔶 권장 | AI 주간 이슈 DB ID | 동일 방법 |

> ⚠️ DB를 Integration에 연결해야 사용 가능: DB 우상단 `...` → **Connections** → 해당 Integration 추가

---

## 8. 텔레그램

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ 필수 | 봇 인증 토큰 | 텔레그램 앱 → **@BotFather** → `/newbot` → 이름/아이디 입력 → 토큰 발급 (`숫자:문자열` 형식) |
| `TELEGRAM_CHAT_ID` | ✅ 필수 | 뉴스·AI이슈 채널 ID | ① 채널에 봇을 관리자로 추가 → ② `api.telegram.org/bot{토큰}/getUpdates` 호출 후 `chat.id` 확인 또는 **@userinfobot**에 채널 포워딩 ③ 채널·슈퍼그룹은 반드시 `-100` 접두사 (예: `-1001234567890`) |
| `TELEGRAM_CHAT_ID_STOCK` | ✅ 필수 | 주식 전용 채널 ID (@msstockbrief) | 동일 방법 |

---

## 9. SNS 카드뉴스

> **파이프라인**: `build_cardnews.py` → `generate_cardnews_images.py` → `post_cardnews.py`

### Instagram

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | ✅ 필수 | Meta Graph API 장기 토큰 (60일 유효) | ① [Meta for Developers](https://developers.facebook.com) → 앱 → **Graph API Explorer** → `instagram_content_publish` 권한 체크 → Generate Access Token → ② 단기 토큰을 장기 토큰으로 교환: `GET /oauth/access_token?grant_type=fb_exchange_token&...` |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ✅ 필수 | Instagram Business 계정 숫자 ID | `GET /me/accounts` → `instagram_business_account.id` 값 (`17841...` 형식) |

> ⚠️ 60일마다 만료 — 만료 전 Graph API Explorer에서 재발급 필요

### Facebook Page

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `FACEBOOK_PAGE_ID` | ✅ 필수 | Facebook 페이지 숫자 ID | `GET /v21.0/me/accounts?access_token={장기토큰}` → `data[0].id` |
| `META_PAGE_ACCESS_TOKEN` | ✅ 필수 | Facebook Page Access Token | 동일 응답 → `data[0].access_token` |

### Threads

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `THREADS_USER_ID` | ✅ 필수 | Threads 사용자 숫자 ID | Graph API Explorer → Threads API 앱 → `threads_content_publish` 권한 → `GET /me?fields=id` |
| `THREADS_ACCESS_TOKEN` | ✅ 필수 | Threads API 액세스 토큰 | 동일 앱에서 토큰 생성 ※ Instagram 토큰과 별도 발급 |

### Twitter / X

| 변수명 | 필요여부 | 설명 | 획득 방법 |
|---|---|---|---|
| `TWITTER_API_KEY` | ⬜ 선택 | Developer App API Key | [developer.twitter.com](https://developer.twitter.com) → 프로젝트 → App → **Keys and Tokens** |
| `TWITTER_API_SECRET` | ⬜ 선택 | API Key Secret | 동일 |
| `TWITTER_ACCESS_TOKEN` | ⬜ 선택 | OAuth 1.0a 액세스 토큰 | 동일 → "Access Token and Secret" 생성 |
| `TWITTER_ACCESS_TOKEN_SECRET` | ⬜ 선택 | 액세스 토큰 시크릿 | 동일 |

> ⚠️ 트윗 작성은 **Basic 이상** 필요 (월 $100). Free 티어는 읽기 전용

---

## 10. 테마 설정 (선택)

| 변수명 | 필요여부 | 설명 | 기본값 |
|---|---|---|---|
| `SITE_THEME` | ⬜ 선택 | 전체 사이트 기본 테마 | `classic` |
| `THEME_NEWS` | ⬜ 선택 | 뉴스 브리핑 개별 테마 | `editorial` |
| `THEME_STOCK` | ⬜ 선택 | 주식 시황 개별 테마 | `SITE_THEME` 상속 |
| `THEME_EMAIL` | ⬜ 선택 | 이메일 개별 테마 | `classic` |

> 선택지: `classic` \| `minimal` \| `ink` \| `forest` \| `editorial` \| `terminal`

---

## 등록 위치별 현황 (2026-06-12 기준)

### GitHub Secrets (Actions CI/CD용)

```
LLM
  ✅ LLM_PROVIDER
  ✅ GEMINI_API_KEY
  ✅ OPENAI_API_KEY           (폴백용)

이메일
  ✅ GMAIL_USER
  ✅ GMAIL_APP_PASSWORD
  ✅ RECIPIENT_EMAILS         (Supabase 폴백)
  ✅ UNSUBSCRIBE_SECRET       (레거시 HMAC 호환)

사이트
  ✅ SITE_BASE_URL

Supabase
  ✅ SUPABASE_SERVICE_KEY

GitHub (레거시)
  ✅ GH_CONTENTS_TOKEN        (향후 제거 예정)

네이버
  ✅ NAVER_CLIENT_ID
  ✅ NAVER_CLIENT_SECRET

Notion
  ✅ NOTION_API_KEY
  ✅ NOTION_DATABASE_ID_NEWS
  ✅ NOTION_DATABASE_ID_STOCK
  ✅ NOTION_DATABASE_ID_AI_ISSUE

텔레그램
  ✅ TELEGRAM_BOT_TOKEN
  ✅ TELEGRAM_CHAT_ID
  ✅ TELEGRAM_CHAT_ID_STOCK

SNS — Instagram
  ✅ INSTAGRAM_ACCESS_TOKEN
  ✅ INSTAGRAM_BUSINESS_ACCOUNT_ID

SNS — Facebook
  ✅ FACEBOOK_PAGE_ID
  ✅ META_PAGE_ACCESS_TOKEN

SNS — Threads
  ✅ THREADS_USER_ID
  ✅ THREADS_ACCESS_TOKEN

SNS — Twitter/X (미발급)
  □  TWITTER_API_KEY / TWITTER_API_SECRET
  □  TWITTER_ACCESS_TOKEN / TWITTER_ACCESS_TOKEN_SECRET

레거시 (GitHub Secrets에서 삭제 권장)
  ⚠️ RECIPIENT_EMAIL         (단수형, RECIPIENT_EMAILS로 대체)
  ⚠️ RESEND_API_KEY          (Gmail SMTP 전환으로 폐기)
```

### Vercel 환경변수 (서버리스 함수 /api/*.py 용)

> Vercel 대시보드 → 프로젝트 → Settings → Environment Variables

```
  ✅ SUPABASE_SERVICE_KEY     ← 반드시 등록 (미등록 시 /api/unsubscribe 401 오류)
  🔶 UNSUBSCRIBE_SECRET       ← 레거시 HMAC 구독취소 호환성 유지 시 필요
  ⬜ SUPABASE_URL             ← _supabase.py에 기본값 하드코딩, 없어도 됨
```

---

## 기능별 필요 환경변수 요약

| 기능 | 필요 변수 |
|---|---|
| 뉴스 수집·분석 | `LLM_PROVIDER` + LLM 키 |
| 이메일 발송 | `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `SUPABASE_SERVICE_KEY` (폴백: `RECIPIENT_EMAILS`) |
| 뉴스 텔레그램 발송 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| 주식 수집 | `NAVER_CLIENT_ID/SECRET` + LLM 키 |
| 주식 텔레그램 발송 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID_STOCK` |
| Notion 동기화 | `NOTION_API_KEY`, `NOTION_DATABASE_ID_*` |
| 구독 API (Vercel) | `SUPABASE_SERVICE_KEY` (Vercel 환경변수에 등록) |
| 카드뉴스 Instagram | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID` |
| 카드뉴스 Facebook | `FACEBOOK_PAGE_ID`, `META_PAGE_ACCESS_TOKEN` |
| 카드뉴스 Threads | `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN` |
| 카드뉴스 Telegram | `TELEGRAM_BOT_TOKEN` + 채널별 CHAT_ID (stock은 `_STOCK` 자동 분기) |
| 카드뉴스 Twitter | `TWITTER_API_KEY/SECRET`, `TWITTER_ACCESS_TOKEN/SECRET` |
