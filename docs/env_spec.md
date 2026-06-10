# 환경변수 명세서 (Environment Variable Specification)

> **최종 업데이트**: 2026-06-10  
> **관리 원칙**
> - `.env.example` — 키 이름과 설명만 git 추적 (실제값 없음)
> - `.env` — 로컬 개발 실제값 (`.gitignore` 적용, 절대 커밋 금지)
> - **GitHub Secrets** — CI/CD 운영값 (Settings → Secrets and variables → Actions)
> - 본 문서 — 각 변수의 목적·획득방법·사용처 명세

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

| 변수명 | 필요여부 | 설명 | 획득처 |
|---|---|---|---|
| `LLM_PROVIDER` | ✅ 필수 | 사용할 LLM (`gemini`\|`claude`\|`gpt`) | 직접 입력 |
| `GEMINI_API_KEY` | ✅ 필수 (gemini) | Gemini API 인증 키 | [Google AI Studio](https://aistudio.google.com/apikey) |
| `ANTHROPIC_API_KEY` | ⬜ 선택 | Claude API 인증 키 | [Anthropic Console](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | ⬜ 선택 | OpenAI API 인증 키 | [OpenAI Platform](https://platform.openai.com/api-keys) |

> 현재 기본값: `LLM_PROVIDER=gemini`. 폴백 모델: `GEMINI_MODEL_FALLBACK=gemini-2.5-flash`

---

## 2. 이메일 (Gmail SMTP)

| 변수명 | 필요여부 | 설명 |
|---|---|---|
| `GMAIL_USER` | ✅ 필수 | 발송 계정 이메일 |
| `GMAIL_APP_PASSWORD` | ✅ 필수 | Gmail 앱 비밀번호 (계정 비번 아님) |
| `RECIPIENT_EMAILS` | 🔶 권장 | Supabase 조회 실패 시 비상 폴백 수신자 목록 |
| `UNSUBSCRIBE_SECRET` | 🔶 권장 | 레거시 HMAC 구독취소 링크 검증 키 |

> `RECIPIENT_EMAILS`는 Supabase 구독 시스템 전환 후 비상 폴백으로만 유지됨

---

## 3. 사이트 / Vercel

| 변수명 | 필요여부 | 설명 |
|---|---|---|
| `SITE_BASE_URL` | ✅ 필수 | 배포 사이트 URL (`https://ms-dailynews.vercel.app`) |
| `SITE_TITLE` | ⬜ 선택 | 사이트 타이틀 (기본값: `AI News Brief`) |
| `SUBSCRIBE_URL` | ⬜ 선택 | 구독 폼 URL (기본값: `{SITE_BASE_URL}/subscribe`) |

---

## 4. Supabase (구독 시스템 — 구현 완료)

| 변수명 | 필요여부 | 설명 | 획득처 |
|---|---|---|---|
| `SUPABASE_URL` | ✅ 필수 | Supabase 프로젝트 URL | 대시보드 → Settings → API |
| `SUPABASE_SERVICE_KEY` | ✅ 필수 | 서비스 롤 키 (RLS 우회, 서버 전용) | 대시보드 → Settings → API → `service_role` |

> **보안 주의**: `SUPABASE_SERVICE_KEY`는 절대 프론트엔드에 노출 금지  
> RLS 활성화 상태 — anon 키로는 테이블 접근 불가  
> 구독자 테이블: `subscribers` (email, channels JSONB, status, is_admin)

---

## 5. GitHub

| 변수명 | 필요여부 | 설명 |
|---|---|---|
| `GH_CONTENTS_TOKEN` | 🗑️ 레거시 | 구 구독취소 파일 API용 — Supabase 전환으로 미사용 |
| `GITHUB_REPOSITORY` | 🗑️ 레거시 | 구 구독취소 저장소 경로 — 동일 |

---

## 6. 네이버 API

| 변수명 | 필요여부 | 설명 | 사용처 |
|---|---|---|---|
| `NAVER_CLIENT_ID` | 🔶 권장 | 네이버 검색 API 클라이언트 ID | `core/stock/collector.py::collect_news_ko()` |
| `NAVER_CLIENT_SECRET` | 🔶 권장 | 네이버 검색 API 시크릿 | 동일 |

> 미설정 시 주식 국내뉴스 보완 건너뜀 (주식 분석 자체는 정상 진행)

---

## 7. Notion

| 변수명 | 필요여부 | 설명 |
|---|---|---|
| `NOTION_API_KEY` | 🔶 권장 | Notion Internal Integration 토큰 |
| `NOTION_DATABASE_ID_NEWS` | 🔶 권장 | 뉴스 브리핑 DB ID |
| `NOTION_DATABASE_ID_STOCK` | 🔶 권장 | 주식 시황 DB ID |
| `NOTION_DATABASE_ID_AI_ISSUE` | 🔶 권장 | AI 주간 이슈 DB ID |

---

## 8. 텔레그램

| 변수명 | 필요여부 | 설명 | 사용처 |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ 필수 | 텔레그램 봇 토큰 (@chamgil_news_bot) | 모든 텔레그램 발송 |
| `TELEGRAM_CHAT_ID` | ✅ 필수 | 뉴스·AI이슈 채널 ID | 뉴스/AI이슈 브리핑 + 카드뉴스 |
| `TELEGRAM_CHAT_ID_STOCK` | ✅ 필수 | 주식 전용 채널 ID (@msstockbrief) | 주식 브리핑 + 주식 카드뉴스 |

> `post_cardnews.py::post_telegram()` — channel='stock'이면 `TELEGRAM_CHAT_ID_STOCK`, 그 외 `TELEGRAM_CHAT_ID`

---

## 9. SNS 카드뉴스

> **파이프라인**: `build_cardnews.py` → `generate_cardnews_images.py` → `post_cardnews.py`  
> **워크플로우**: `cardnews.yml` — `--platform` 인자로 플랫폼 선택  
> **이미지 소스**: GitHub Raw URL (push 후 즉시 사용 가능)

### Instagram

| 변수명 | 필요여부 | 설명 | 발송 방식 |
|---|---|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | ✅ 필수 | Meta Graph API 장기 토큰 (60일) | 좌우 스와이프 카루셀 |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | ✅ 필수 | Instagram Business 계정 숫자 ID (`17841453929908469`) | — |

> 획득: Meta for Developers → Graph API Explorer → `instagram_content_publish` 권한  
> ⚠️ 60일마다 만료 — 갱신 필요

### Facebook Page

| 변수명 | 필요여부 | 설명 | 발송 방식 |
|---|---|---|---|
| `FACEBOOK_PAGE_ID` | ✅ 필수 | Facebook 페이지 ID (`1205910932600535`, "Ainews") | 이미지 세로 나열 |
| `META_PAGE_ACCESS_TOKEN` | ✅ 필수 | Facebook Page Access Token | — |

> 획득: `graph.facebook.com/v21.0/me/accounts?access_token={long_lived_token}`

### Threads

| 변수명 | 필요여부 | 설명 | 발송 방식 |
|---|---|---|---|
| `THREADS_USER_ID` | ✅ 필수 | Threads 사용자 ID (`27088465757470013`) | 카루셀 (Instagram과 동일) |
| `THREADS_ACCESS_TOKEN` | ✅ 필수 | Threads API 액세스 토큰 | — |

> 획득: Meta for Developers → Threads API  
> Instagram 토큰과 별도 발급 필요

### Twitter / X

| 변수명 | 필요여부 | 설명 |
|---|---|---|
| `TWITTER_API_KEY` | ⬜ 선택 | Twitter Developer App API Key |
| `TWITTER_API_SECRET` | ⬜ 선택 | API Key Secret |
| `TWITTER_ACCESS_TOKEN` | ⬜ 선택 | OAuth 1.0a 액세스 토큰 |
| `TWITTER_ACCESS_TOKEN_SECRET` | ⬜ 선택 | 액세스 토큰 시크릿 |

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

## GitHub Secrets 등록 현황 (2026-06-10 기준)

```
LLM
✅ LLM_PROVIDER
✅ GEMINI_API_KEY
✅ OPENAI_API_KEY           (gemini 폴백용)

이메일
✅ GMAIL_USER
✅ GMAIL_APP_PASSWORD
✅ RECIPIENT_EMAILS         (Supabase 폴백용)
✅ UNSUBSCRIBE_SECRET       (레거시 HMAC 호환)

사이트
✅ SITE_BASE_URL

Supabase (구독 시스템)
✅ SUPABASE_SERVICE_KEY

GitHub (레거시)
✅ GH_CONTENTS_TOKEN        (레거시, 향후 제거 예정)

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

SNS 카드뉴스 — Instagram
✅ INSTAGRAM_ACCESS_TOKEN
✅ INSTAGRAM_BUSINESS_ACCOUNT_ID

SNS 카드뉴스 — Facebook
✅ FACEBOOK_PAGE_ID
✅ META_PAGE_ACCESS_TOKEN

SNS 카드뉴스 — Threads
✅ THREADS_USER_ID
✅ THREADS_ACCESS_TOKEN

SNS 카드뉴스 — Twitter/X (미발급)
□  TWITTER_API_KEY
□  TWITTER_API_SECRET
□  TWITTER_ACCESS_TOKEN
□  TWITTER_ACCESS_TOKEN_SECRET

레거시 (삭제 권장)
⚠️ RECIPIENT_EMAIL         (단수, RECIPIENT_EMAILS로 대체됨)
⚠️ RESEND_API_KEY          (Gmail SMTP 전환으로 완전 폐기)
```

---

## 기능별 필요 환경변수 요약

| 기능 | 필요 변수 |
|---|---|
| 뉴스 수집·분석 | `LLM_PROVIDER` + LLM 키 |
| 뉴스 이메일 발송 | `GMAIL_*`, Supabase (폴백: `RECIPIENT_EMAILS`) |
| 뉴스 텔레그램 발송 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| 주식 수집 | `NAVER_CLIENT_ID/SECRET` + LLM 키 |
| 주식 텔레그램 발송 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID_STOCK` |
| Notion 동기화 | `NOTION_API_KEY`, `NOTION_DATABASE_ID_*` |
| 구독 시스템 | `SUPABASE_SERVICE_KEY` + `SUPABASE_URL` + Gmail |
| 카드뉴스 Instagram | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID` |
| 카드뉴스 Facebook | `FACEBOOK_PAGE_ID`, `META_PAGE_ACCESS_TOKEN` |
| 카드뉴스 Threads | `THREADS_USER_ID`, `THREADS_ACCESS_TOKEN` |
| 카드뉴스 Telegram | `TELEGRAM_BOT_TOKEN` + 채널별 CHAT_ID (자동 분기) |
| 카드뉴스 Twitter | `TWITTER_API_KEY/SECRET`, `TWITTER_ACCESS_TOKEN/SECRET` |
