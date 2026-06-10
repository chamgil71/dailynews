# SNS 카드뉴스 발송 디자인 가이드

> 작성: 2026-06-10 | 대상 파일: `scripts/post_cardnews.py`, `scripts/post_instagram.py`

---

## 1. 플랫폼별 발송 방식 비교

| 플랫폼 | 이미지 표시 | 링크 방식 | 인라인 버튼 | 채널 분기 |
|--------|-----------|---------|-----------|---------|
| **Instagram** | 좌우 스와이프 카루셀 | 캡션 내 🔗 텍스트 | ❌ API 미지원 | 단일 계정 |
| **Facebook** | 세로 나열 (Grid) | 캡션 내 🔗 텍스트 | ❌ | 단일 페이지 |
| **Threads** | 카루셀 (Instagram과 동일) | 캡션 내 🔗 텍스트 | ❌ | 단일 계정 |
| **Telegram** | 미디어 그룹 | 인라인 버튼 🔘 | ✅ | 채널별 분기 |
| **Twitter/X** | 이미지 스레드 (최대 4장) | 트윗 텍스트 내 🔗 | ❌ | 단일 계정 |

---

## 2. 플랫폼별 발송 구조

### 2-1. Instagram (카루셀)

```
[슬라이드 1] 커버 이미지
  └─ 캡션: 날짜 + 채널 브리핑 + 이슈 TOP 3 + 원사이트 링크 + 해시태그
[슬라이드 2] 이슈 1 상세
[슬라이드 3] 이슈 2 상세
[슬라이드 4] 이슈 3 상세
[슬라이드 5] 트렌드/키워드 카드
```

**API 흐름:**
1. 이미지별 미디어 컨테이너 생성 (`is_carousel_item=true`)
2. 카루셀 컨테이너 생성 (children 목록)
3. FINISHED 상태 확인 후 `media_publish`

**제약:** 최대 10장 / 캡션 2,200자 / 첫 장에만 캡션 붙음

---

### 2-2. Facebook Page (멀티 사진)

```
[본문] 날짜 + 채널 브리핑 + 이슈 TOP 3 + 원사이트 링크 + 해시태그
[이미지 1] 커버
[이미지 2] 이슈 1
[이미지 3] 이슈 2
...
(피드에서 이미지가 세로로 이어져 표시)
```

**API 흐름:**
1. 각 이미지 비공개 업로드 → photo_id 수집
2. `/feed` 엔드포인트에 `attached_media` 배열로 멀티 사진 포스트

**제약:** 이미지 개수 제한 없음 / 첫 이미지 썸네일이 링크 미리보기에 사용됨

---

### 2-3. Threads (카루셀)

```
[텍스트] 날짜 + 채널 브리핑 + 이슈 TOP 3 + 원사이트 링크 + 해시태그
[이미지] 카루셀 형식 (Instagram과 동일 스와이프)
```

**API 흐름 (Instagram과 동일 구조):**
1. 이미지별 아이템 컨테이너 생성 (`is_carousel_item=true`)
2. 카루셀 컨테이너 생성 (`text`에 캡션 포함)
3. FINISHED 확인 후 `threads_publish`

**제약:** 최대 20장 / 텍스트 500자 / 링크 미리보기 별도 지원 안 함

---

### 2-4. Telegram (미디어 그룹 + 버튼)

```
[미디어 그룹] 이미지 N장
  └─ 첫 이미지에 캡션: 날짜 + 채널 브리핑 + 이슈 TOP 3 + 원사이트 링크

[버튼 메시지] "📖 {채널} 카드뉴스 전체 보기"
  └─ [🌐 웹에서 보기]  [📂 전체 아카이브]
```

**채널 분기:**
- `channel == 'stock'` → `TELEGRAM_CHAT_ID_STOCK` (주식 전용 채널)
- `channel == 'news'` or `'ai-issue'` → `TELEGRAM_CHAT_ID` (뉴스·AI이슈 채널)

**제약:** 미디어 그룹 최대 10장 / 캡션 1,024자

---

### 2-5. Twitter/X (이미지 스레드)

```
[트윗] 날짜 + 채널 브리핑 + 이슈 TOP 3 + 원사이트 링크 (280자 제한)
  └─ 첨부 이미지: 최대 4장
```

**API 흐름:**
1. 이미지 업로드 → `media_id` 수집 (tweepy v1.1 API)
2. `create_tweet` with `media_ids` (tweepy v2 API)

**제약:** 트윗 280자 / 이미지 최대 4장 / 영상 1개

---

## 3. 캡션 공통 구조

모든 플랫폼 캡션은 `_build_caption()` 함수로 생성 (플랫폼별 분기 없음):

```
📰 {연도}년 {월}월 {일}일 ({요일}) {채널} 브리핑

🔥 {이슈 제목 1}
📢 {이슈 제목 2}
💡 {이슈 제목 3}

🔗 ms-dailynews.vercel.app/cardnews/{channel}/{date}.html

#AI뉴스 #테크뉴스 #데일리뉴스 #인공지능 #AINews #TechNews
```

**채널별 해시태그:**
- `news`: `#AI뉴스 #테크뉴스 #데일리뉴스 #인공지능 #AINews #TechNews`
- `ai-issue`: `#AI이슈 #테크트렌드 #인공지능 #AINews`
- `stock`: `#주식 #시황 #코스피 #투자`

---

## 4. 이미지 소스

모든 플랫폼이 **GitHub Raw URL**을 이미지 소스로 사용:

```
https://raw.githubusercontent.com/chamgil71/dailynews/main/publish/cardnews/{channel}/{date}-{n}.png
```

→ PNG가 git push 후 즉시 사용 가능. API가 URL로 직접 가져가므로 별도 업로드 서버 불필요.

---

## 5. 발송 플로우 (cardnews.yml)

```
news.yml / stock_build.yml / ai_issue.yml 완료
  ↓ (workflow_run 트리거)
cardnews.yml
  ├─ build_cardnews.py     → HTML 생성
  ├─ generate_cardnews_images.py → Playwright → PNG
  ├─ git push (publish/cardnews/)
  └─ post_cardnews.py --platform {platforms}
       ├─ instagram  → post_instagram() → Meta Graph API
       ├─ threads    → post_threads()   → Threads API
       ├─ facebook   → post_facebook()  → Meta Graph API
       ├─ telegram   → post_telegram()  → Telegram Bot API (채널 분기)
       └─ twitter    → post_twitter()   → Twitter API v2
```

---

## 6. 플랫폼 선택 방법

### 워크플로우 수동 실행 시 (`workflow_dispatch`)

| 용도 | platforms 값 |
|------|-------------|
| 전체 발송 (기본) | `instagram,threads,facebook,telegram` |
| Meta 3개만 | `instagram,threads,facebook` |
| Telegram만 | `telegram` |
| Instagram + Telegram | `instagram,telegram` |
| 이미지 빌드만 (SNS 발송 없음) | `build_only = true` |

### 특정 채널 날짜 재발송

```bash
python scripts/post_cardnews.py --type news --platform instagram,threads --date 2026-06-10
```

---

## 7. 환경변수 목록

| 변수명 | 플랫폼 | 비고 |
|--------|--------|------|
| `INSTAGRAM_ACCESS_TOKEN` | Instagram | 장기 토큰, 60일 만료 |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram | 숫자 ID |
| `FACEBOOK_PAGE_ID` | Facebook | 숫자 ID |
| `META_PAGE_ACCESS_TOKEN` | Facebook | Page Access Token |
| `THREADS_USER_ID` | Threads | 숫자 ID |
| `THREADS_ACCESS_TOKEN` | Threads | |
| `TELEGRAM_BOT_TOKEN` | Telegram | 공통 봇 |
| `TELEGRAM_CHAT_ID` | Telegram | 뉴스·AI이슈 채널 |
| `TELEGRAM_CHAT_ID_STOCK` | Telegram | 주식 전용 채널 |
| `TWITTER_API_KEY` / `TWITTER_API_SECRET` | Twitter/X | OAuth 1.0a |
| `TWITTER_ACCESS_TOKEN` / `TWITTER_ACCESS_TOKEN_SECRET` | Twitter/X | |

---

## 8. 주의사항

- **Instagram 토큰 만료**: 60일마다 갱신 필요. Meta Graph API Explorer에서 연장 가능
- **Threads 토큰**: Instagram과 별도 토큰 (Threads API 독자 발급)
- **Facebook Page Token**: 페이지 관리자 권한 필요. 장기 토큰 발급 권장
- **이미지 공개 접근**: GitHub Raw URL이 public이어야 Meta API가 가져갈 수 있음
- **Telegram 채널 ID**: supergroup/채널은 `-100` 접두사 필요 (예: `-1001234567890`)
