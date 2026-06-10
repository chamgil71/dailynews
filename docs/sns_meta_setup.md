# Meta SNS API 토큰 발급 가이드
> Facebook / Instagram / Threads 동시배포용  
> 기준 계정: `chamgil71` / 앱명: `dailynews-broadcast`

---

## 사전 확인 (이미 완료된 것들)

- [x] Instagram 비즈니스 계정 전환 완료
- [x] Facebook 페이지(Ainews) 생성 + Instagram 연결 완료
- [x] Meta Developer 앱(`dailynews-broadcast`) 생성 완료

---

## PART 1 — Meta 앱 권한 설정

### 1-1. 앱 대시보드 접속
👉 https://developers.facebook.com/apps → `dailynews-broadcast` 클릭

### 1-2. 이용 사례별 권한 확인
좌측 메뉴 **이용 사례** → 각 항목 **맞춤 설정** → **권한 및 기능** 탭

아래 권한들이 모두 **"테스트 준비 완료"** 상태인지 확인:

| 이용 사례 | 권한 |
|---|---|
| Instagram API | `instagram_basic` |
| Instagram API | `instagram_content_publish` |
| 페이지 관리 | `pages_manage_posts` |
| 페이지 관리 | `pages_read_engagement` |
| 페이지 관리 | `pages_show_list` |
| Threads API 액세스 | `threads_basic` |
| Threads API 액세스 | `threads_content_publish` |

> 상태가 없고 `+ 추가` 버튼만 보이면 → **옵션 → 이용 사례에 필요** 클릭

---

## PART 2 — Facebook + Instagram 토큰 발급

### 2-1. Graph API Explorer 접속
👉 https://developers.facebook.com/tools/explorer

오른쪽 패널 설정:
- **Meta 앱**: `dailynews-broadcast` 선택
- **사용자 또는 페이지**: `토큰 받기` 선택

### 2-2. 권한 추가
**권한 추가** 드롭다운에서 아래 항목 선택:

**Events Groups Pages** 섹션:
- `business_management`
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_show_list`

**Other** 섹션:
- `instagram_basic`
- `instagram_content_publish`

### 2-3. 토큰 생성
**Generate Access Token** 클릭 → 팝업에서 Facebook 페이지, Instagram 계정 모두 체크 → **저장**

### 2-4. 단기 토큰 → 장기 토큰 변환 (필수)
👉 https://developers.facebook.com/tools/debug/accesstoken

1. 발급된 토큰 붙여넣기 → **디버그** 클릭
2. 페이지 하단 **액세스 토큰 확장** 클릭
3. 새로 생성된 토큰 복사 (약 60일 유효)

### 2-5. 값 수집

**① Facebook Page ID + Page Access Token**  
Graph API Explorer 경로 입력 후 제출:
```
me/accounts
```
응답에서:
```json
{
  "data": [{
    "access_token": "EAABs...",   ← META_PAGE_ACCESS_TOKEN
    "id": "1205910932600535"      ← FACEBOOK_PAGE_ID
  }]
}
```

**② Instagram Business Account ID**  
Graph API Explorer 경로 입력 후 제출:
```
me/accounts?fields=id,name,instagram_business_account
```
응답에서:
```json
"instagram_business_account": {
  "id": "17841453929908469"       ← INSTAGRAM_BUSINESS_ACCOUNT_ID
}
```

> `INSTAGRAM_ACCESS_TOKEN` = 2-4에서 발급한 **장기 토큰**과 동일한 값

---

## PART 3 — Threads 토큰 발급

> Threads는 Meta Graph API와 별도 토큰 체계를 사용합니다.

### 3-1. Threads 테스터 등록
👉 https://developers.facebook.com/apps → `dailynews-broadcast`  
좌측 메뉴 **앱 역할 → 역할**

- **Threads 테스터** 탭 → **사람 추가** → 본인 Threads 계정(`chamgil`) 입력

### 3-2. Threads 앱에서 초대 수락
Threads 앱(모바일):
```
설정 → 계정 → 웹사이트 권한 → 앱 및 웹사이트 → 초대 수락
```
> 역할 목록에서 "대기 중" → 상태 없음으로 바뀌면 완료

### 3-3. Threads 토큰 생성
👉 https://developers.facebook.com/apps → `dailynews-broadcast`  
**이용 사례 → Threads API 액세스 → 설정**

페이지 하단 **사용자 토큰 생성기** 섹션:
- `chamgil` 계정 옆 **액세스 토큰 생성하기** 클릭
- 팝업에서 **복사** 클릭

→ 이 값이 `THREADS_ACCESS_TOKEN`

### 3-4. Threads User ID 확인
브라우저 주소창에 입력 (토큰 교체):
```
https://graph.threads.net/v1.0/me?fields=id,username&access_token=여기에_THREADS_ACCESS_TOKEN
```
응답:
```json
{
  "id": "27088465757470013",     ← THREADS_USER_ID
  "username": "chamgil"
}
```

---

## PART 4 — 환경변수 값 정리

```env
# ── SNS 카드뉴스 — INSTA ──────────────────────────────
INSTAGRAM_ACCESS_TOKEN=        # PART 2-4 장기 토큰
INSTAGRAM_BUSINESS_ACCOUNT_ID= # PART 2-5 ② instagram_business_account.id

# ── SNS 카드뉴스 — Facebook ───────────────────────────
FACEBOOK_PAGE_ID=              # PART 2-5 ① data[0].id
META_PAGE_ACCESS_TOKEN=        # PART 2-5 ① data[0].access_token

# ── SNS 카드뉴스 — Threads ────────────────────────────
THREADS_USER_ID=               # PART 3-4 id
THREADS_ACCESS_TOKEN=          # PART 3-3 생성된 토큰
```

---

## PART 5 — 토큰 만료 관리

| 토큰 | 만료 | 갱신 방법 |
|---|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | 60일 | Access Token Debugger → 액세스 토큰 확장 |
| `META_PAGE_ACCESS_TOKEN` | 무기한* | Page Token은 만료 없음 |
| `THREADS_ACCESS_TOKEN` | 장기 (약 60일) | 앱 대시보드 → 사용자 토큰 생성기 → 재생성 |

> *단, 연결된 사용자 토큰이 만료되면 Page Token도 재발급 필요

### 자동 갱신 (GitHub Actions)
`refresh-meta-token.yml` 워크플로우가 매주 월요일 자동 실행하여  
`INSTAGRAM_ACCESS_TOKEN` 을 갱신하고 GitHub Secrets에 덮어씁니다.

---

## 참고: 현재 확보된 실제 값

| 항목 | 값 |
|---|---|
| Facebook Page ID | `1205910932600535` |
| Instagram Business Account ID | `17841453929908469` |
| Threads User ID | `27088465757470013` |
| Threads Username | `chamgil` |
| Meta App ID | `1018767854003258` |
| Threads App ID | `1382302093717039` |
