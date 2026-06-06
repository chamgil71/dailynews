# 환경변수 명세서 (Environment Variable Specification)

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
| 🔄 Phase 2 | Supabase 구독 시스템 구현 시 추가 |
| ⚠️ Phase 2 대체예정 | Supabase 전환 후 제거 예정 |

---

## 1. LLM API

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `LLM_PROVIDER` | ✅ 필수 | 사용할 LLM 선택 | — | `gemini` \| `claude` \| `gpt` |
| `GEMINI_API_KEY` | ✅ 필수 (gemini) | Gemini API 인증 키 | [Google AI Studio](https://aistudio.google.com/apikey) | `AIzaSy...` |
| `ANTHROPIC_API_KEY` | ✅ 필수 (claude) | Claude API 인증 키 | [Anthropic Console](https://console.anthropic.com/) | `sk-ant-api03-...` |
| `OPENAI_API_KEY` | ✅ 필수 (gpt) | OpenAI API 인증 키 | [OpenAI Platform](https://platform.openai.com/api-keys) | `sk-proj-...` |

> **현재 기본값**: `LLM_PROVIDER=gemini`  
> 3개 키 모두 GitHub Secrets에 등록 권장 (provider 전환 시 즉시 대응)

---

## 2. 이메일 (Gmail SMTP)

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `GMAIL_USER` | ✅ 필수 | 발송 계정 + 관리자 알림 수신 | Google 계정 | `yourname@gmail.com` |
| `GMAIL_APP_PASSWORD` | ✅ 필수 | Gmail 앱 비밀번호 (계정 비번 아님) | Google 계정 → 보안 → 앱 비밀번호 | `xxxx xxxx xxxx xxxx` |
| `RECIPIENT_EMAILS` | ✅ 필수 | 현재 구독자 목록 (쉼표 구분) | 직접 입력 | `a@gmail.com,b@gmail.com` |
| `TEST_RECIPIENT_EMAILS` | 🔄 Phase 2 | 테스트 모드 수신자 (개발·검증용) | 직접 입력 | `dev@gmail.com` |
| `UNSUBSCRIBE_SECRET` | ⚠️ Phase 2 대체예정 | 구독취소 HMAC 서명 키 | 임의 32자 문자열 생성 | `abcdef1234567890abcdef1234567890` |

> **역할 구분 (현재)**
> - `GMAIL_USER`: 발신자 + Phase 1 분석실패 관리자 알림 수신
> - `RECIPIENT_EMAILS`: 모든 뉴스레터 수신 (현재 서비스 구독자)
>
> **역할 구분 (Phase 2 전환 후)**
> - `GMAIL_USER`: 발신자 + 관리자 알림 전용
> - `TEST_RECIPIENT_EMAILS`: test 모드 수신 (개발 검증)
> - `RECIPIENT_EMAILS`: ⚠️ Supabase로 이전 후 제거 예정

---

## 3. 사이트 / Vercel

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `SITE_BASE_URL` | ✅ 필수 | 배포된 사이트 URL (링크 생성용) | Vercel 대시보드 → Domains | `https://your-project.vercel.app` |
| `SITE_TITLE` | ⬜ 선택 | 사이트 타이틀 (기본값 있음) | 직접 입력 | `AI News Brief` |
| `SUBSCRIBE_URL` | ⬜ 선택 | 구독 폼 URL | `SITE_BASE_URL/subscribe` | `https://your-project.vercel.app/subscribe` |
| `VERCEL_TOKEN` | ⬜ 선택 | Vercel 수동 배포용 토큰 | Vercel → Account → Tokens | `vercel_...` |
| `VERCEL_ORG_ID` | ⬜ 선택 | Vercel 조직 ID | Vercel → Project → Settings | `team_...` |
| `VERCEL_PROJECT_ID` | ⬜ 선택 | Vercel 프로젝트 ID | Vercel → Project → Settings | `prj_...` |

> Vercel 3개는 Git Integration 사용 시 불필요 (현재 비활성화 상태)

---

## 4. GitHub

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `GH_CONTENTS_TOKEN` | ⚠️ Phase 2 대체예정 | 구독취소 파일 읽기/쓰기용 PAT | GitHub → Settings → Developer settings → PAT | `ghp_...` |
| `GITHUB_REPOSITORY` | ⚠️ Phase 2 대체예정 | 저장소 경로 (구독취소 파일 위치) | 직접 입력 | `chamgil71/dailynews` |

> Phase 2에서 Supabase로 대체되면 두 변수 모두 제거 예정

---

## 5. 네이버 API

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `NAVER_CLIENT_ID` | ✅ 필수 (주식) | 네이버 검색 API 클라이언트 ID | [네이버 개발자센터](https://developers.naver.com/) | `ABC123...` |
| `NAVER_CLIENT_SECRET` | ✅ 필수 (주식) | 네이버 검색 API 시크릿 | 동상 | `xyz789...` |

> 주식 시황 수집 시 네이버 금융 뉴스 크롤링에 사용

---

## 6. Notion

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `NOTION_API_KEY` | 🔶 권장 | Notion Internal Integration 토큰 | [Notion 개발자 포털](https://www.notion.so/profile/integrations) → 신규 연결 → 액세스 토큰 | `ntn_...` |
| `NOTION_DATABASE_ID_NEWS` | 🔶 권장 | 뉴스 DB 고유 ID | Notion DB 열기 → URL에서 추출 (`notion.so/.../{ID}?`) | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `NOTION_DATABASE_ID_STOCK` | 🔶 권장 | 주식 DB 고유 ID | 동상 | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `NOTION_DATABASE_ID_AI_ISSUE` | 🔶 권장 | AI 이슈 DB 고유 ID | 동상 | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

> **연결 필수**: Notion 개발자 포털에서 생성한 Integration을 각 DB에 연결해야 함  
> DB URL 형식: `https://www.notion.so/workspace/{DB_ID}?v=...`  
> Notion DB ID 추출: URL에서 마지막 경로 32자리 (하이픈 제외)

---

## 7. 텔레그램

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | 🔶 권장 | 텔레그램 봇 토큰 | Telegram → @BotFather → /newbot | `1234567890:ABCdef...` |
| `TELEGRAM_CHAT_ID` | 🔶 권장 | 뉴스·AI이슈 채널 ID | @userinfobot 또는 채널 ID | `-1001234567890` |
| `TELEGRAM_CHAT_ID_STOCK` | 🔶 권장 | 주식 전용 채널 ID (@msstockbrief) | 동상 | `-1009876543210` |

> 채널 ID: 채널에 봇 추가 후 `@userinfobot` 에 포워드하거나 Telegram API로 확인

---

## 8. SNS 카드뉴스 (Instagram / Twitter·X)

> **카드뉴스 파이프라인**: `build_cardnews.py` → `generate_cardnews_images.py` → `post_cardnews.py`  
> 출력: `publish/cardnews/{news|ai-issue|stock}/YYYY-MM-DD-{N}.png` (1080×1080)  
> 워크플로우: `cardnews.yml` — 각 채널 완료 후 자동 트리거

### Instagram

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | 🔶 권장 | Meta Graph API 장기 액세스 토큰 (60일) | Meta for Developers → Graph API Explorer → `instagram_content_publish` 권한 요청 | `EAAxxxxx...` |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | 🔶 권장 | Instagram Business 계정 숫자 ID | Meta Business Suite → 계정 설정 또는 Graph API `/me?fields=instagram_business_account` | `123456789012345` |

> **주의**: 액세스 토큰은 60일마다 만료. 만료 전 Graph API Explorer에서 갱신 필요.  
> 필요 앱 권한: `instagram_content_publish`, `instagram_manage_comments`(선택)

### Twitter / X

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `TWITTER_API_KEY` | 🔶 권장 | Twitter Developer App API Key | [developer.twitter.com](https://developer.twitter.com/) → Projects & Apps → 키 생성 | `xxxxxxxxxx...` |
| `TWITTER_API_SECRET` | 🔶 권장 | Twitter Developer App API Key Secret | 동상 | `xxxxxxxxxx...` |
| `TWITTER_ACCESS_TOKEN` | 🔶 권장 | OAuth 1.0a 액세스 토큰 | 동상 → Keys and Tokens → Generate | `xxxxxxxxxx...` |
| `TWITTER_ACCESS_TOKEN_SECRET` | 🔶 권장 | OAuth 1.0a 액세스 토큰 시크릿 | 동상 | `xxxxxxxxxx...` |

> **API 티어**: Free 티어는 읽기 전용. 트윗 작성은 **Basic 이상** 필요 (월 $100).  
> 미디어 업로드는 v1.1 API (`tweepy.API`), 트윗 게시는 v2 API (`tweepy.Client`) 사용.

---

## 10. Supabase (Phase 2 — 미구현)

| 변수명 | 필요여부 | 설명 | 획득처 | 형식 예시 |
|---|---|---|---|---|
| `SUPABASE_URL` | 🔄 Phase 2 | Supabase 프로젝트 URL | Supabase 대시보드 → Project Settings → API | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | 🔄 Phase 2 | 서비스 롤 키 (RLS 우회, 서버 전용) | Supabase 대시보드 → Project Settings → API | `eyJ...` |
| `SUPABASE_ANON_KEY` | 🔄 Phase 2 | 익명 공개 키 (프론트엔드 구독 폼용) | 동상 | `eyJ...` |

> **보안 주의**: `SUPABASE_SERVICE_ROLE_KEY`는 서버(GitHub Actions, Vercel 서버리스)에서만 사용  
> 절대 프론트엔드 코드에 포함 금지

---

## 11. 테마 / 표시 설정 (선택)

| 변수명 | 필요여부 | 설명 | 선택지 | 기본값 |
|---|---|---|---|---|
| `SITE_THEME` | ⬜ 선택 | 전체 사이트 기본 테마 | `classic` \| `minimal` \| `ink` \| `forest` \| `editorial` \| `terminal` | `classic` |
| `THEME_NEWS` | ⬜ 선택 | 뉴스 브리핑 개별 테마 | 동상 | `SITE_THEME` 상속 |
| `THEME_STOCK` | ⬜ 선택 | 주식 시황 개별 테마 | 동상 | `SITE_THEME` 상속 |
| `THEME_EMAIL` | ⬜ 선택 | 이메일 개별 테마 | 동상 | `classic` |
| `THEME_CARDNEWS` | ⬜ 선택 | 텔레그램 카드뉴스 테마 | `glass_dark` \| `neon_cyber` \| `minimal_light` | `glass_dark` |

---

## 12. 기타 / 내부용

| 변수명 | 필요여부 | 설명 | 비고 |
|---|---|---|---|
| `GITHUB_ACTIONS` | — | GitHub Actions 자동 주입 | 코드 내부 환경 감지용, 직접 설정 불필요 |
| `FOOTER_GENERATOR` | ⬜ 선택 | 푸터 생성 방식 | 미사용 (예비) |
| `FOOTER_REPO` | ⬜ 선택 | 푸터 저장소 경로 | 미사용 (예비) |

---

## GitHub Secrets 등록 현황 체크리스트

```
필수 (현재 서비스 운영)
✅ LLM_PROVIDER
✅ GEMINI_API_KEY
□  ANTHROPIC_API_KEY        (claude 전환 시 필요)
□  OPENAI_API_KEY           (gpt 전환 시 필요)
✅ GMAIL_USER
✅ GMAIL_APP_PASSWORD
✅ RECIPIENT_EMAILS
✅ UNSUBSCRIBE_SECRET
✅ SITE_BASE_URL
✅ NAVER_CLIENT_ID
✅ NAVER_CLIENT_SECRET
✅ NOTION_API_KEY
✅ NOTION_DATABASE_ID_NEWS
✅ NOTION_DATABASE_ID_STOCK
□  NOTION_DATABASE_ID_AI_ISSUE   (AI 이슈 기능 사용 시)
✅ TELEGRAM_BOT_TOKEN
✅ TELEGRAM_CHAT_ID
✅ TELEGRAM_CHAT_ID_STOCK

SNS 카드뉴스 (PR #19 병합 후 필요)
□  INSTAGRAM_ACCESS_TOKEN
□  INSTAGRAM_BUSINESS_ACCOUNT_ID
□  TWITTER_API_KEY
□  TWITTER_API_SECRET
□  TWITTER_ACCESS_TOKEN
□  TWITTER_ACCESS_TOKEN_SECRET

Phase 2 예정 (미등록)
□  TEST_RECIPIENT_EMAILS
□  SUPABASE_URL
□  SUPABASE_SERVICE_ROLE_KEY
□  SUPABASE_ANON_KEY

Phase 2 대체 후 삭제 예정
□  GH_CONTENTS_TOKEN        (현재 미사용 상태)
□  GITHUB_REPOSITORY        (현재 미사용 상태)
```

---

## 콘텐츠별 필요 환경변수 요약

| 기능 | 필요 변수 |
|---|---|
| **뉴스 수집·분석** | `LLM_PROVIDER` + 해당 LLM 키 |
| **뉴스 이메일 발송** | `GMAIL_USER`, `GMAIL_APP_PASSWORD`, `RECIPIENT_EMAILS` |
| **텔레그램 발송** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| **Notion 동기화** | `NOTION_API_KEY`, `NOTION_DATABASE_ID_NEWS` |
| **주식 수집** | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` + LLM 키 |
| **주식 이메일 발송** | Gmail 3개 변수 |
| **AI 이슈** | LLM 키 + Gmail + Telegram + `NOTION_DATABASE_ID_AI_ISSUE` |
| **사이트 빌드·배포** | `SITE_BASE_URL` |
| **구독취소 (현재)** | `UNSUBSCRIBE_SECRET`, `GH_CONTENTS_TOKEN`, `GITHUB_REPOSITORY` |
| **구독취소 (Phase 2)** | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| **카드뉴스 Instagram 발송** | `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID` |
| **카드뉴스 Twitter 발송** | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN_SECRET` |
| **카드뉴스 Telegram 발송** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (기존 재사용) |
