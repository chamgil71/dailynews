# Google Sheets 연동 설정 가이드

뉴스 DB를 Google Sheets에 자동 저장하기 위한 설정 절차입니다.
GitHub Actions에서 서비스 계정을 사용하므로 1회 설정 후 완전 자동화됩니다.

---

## 1단계 — Google Cloud 프로젝트 설정

1. [console.cloud.google.com](https://console.cloud.google.com) 접속 후 로그인
2. 상단 프로젝트 선택 → **새 프로젝트 만들기**
   - 프로젝트 이름: `dailynews` (자유)
   - 만들기 클릭 후 해당 프로젝트 선택

---

## 2단계 — API 활성화

좌측 메뉴 **API 및 서비스 → 라이브러리**에서 아래 두 API를 각각 검색 후 **사용 설정**:

- `Google Sheets API`
- `Google Drive API`

---

## 3단계 — 서비스 계정 생성

1. 좌측 메뉴 **IAM 및 관리자 → 서비스 계정 → 서비스 계정 만들기**
2. 이름: `dailynews-bot` / 설명: `뉴스 DB 자동 저장용`
3. **만들고 계속하기** → 역할 부여 없이 **완료**

---

## 4단계 — JSON 키 다운로드

1. 생성된 서비스 계정 클릭 → **키** 탭
2. **키 추가 → 새 키 만들기 → JSON** 선택 → 만들기
3. JSON 파일이 자동 다운로드됨 (예: `dailynews-bot-xxxx.json`)
4. 파일 내용 전체를 복사해 둠 (GitHub Secret에 등록 예정)

> 이 JSON 파일은 절대 git에 커밋하지 않습니다.

---

## 5단계 — Google Spreadsheet 생성 및 공유

1. [sheets.google.com](https://sheets.google.com) → 새 스프레드시트 생성
2. 제목: `AI News DB` (자유)
3. URL에서 스프레드시트 ID 복사:
   ```
   https://docs.google.com/spreadsheets/d/ [여기가 ID] /edit
   ```
4. 우측 상단 **공유** 버튼 클릭
5. 서비스 계정 이메일 추가 (편집자 권한):
   ```
   dailynews-bot@[프로젝트명].iam.gserviceaccount.com
   ```
   - 이메일은 서비스 계정 목록 화면에서 확인 가능
6. **알림 전송 체크 해제** 후 공유

---

## 6단계 — GitHub Secrets 등록

GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|-------------|-----|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON 파일 전체 내용 (텍스트 그대로 붙여넣기) |
| `GOOGLE_SPREADSHEET_ID` | 5단계에서 복사한 ID 문자열 |

---

## 7단계 — 코드 구현 (설정 완료 후 진행)

설정이 완료되면 아래 작업을 진행합니다:

### 추가할 패키지 (`requirements.txt`)
```
gspread==6.1.4
google-auth==2.36.0
```

### 신규 파일: `core/sheets.py`
- Google Sheets에 매일 수집된 뉴스 행을 append
- 시트 구조: 날짜 / 카테고리 / 출처라벨 / 언어 / 제목 / 링크 / 발행일시 / 요약
- 링크 기준 중복 방지 (재실행 시 동일 기사 중복 추가 안 됨)

### `main.py` 변경
- Step 4 (현재 xlsx 저장) → Google Sheets append로 교체
- xlsx는 백업용으로 `storage/news_db.xlsx`에 병행 저장 유지

### `news.yml` 변경
```yaml
env:
  GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
  GOOGLE_SPREADSHEET_ID:       ${{ secrets.GOOGLE_SPREADSHEET_ID }}
```

### 기존 데이터 마이그레이션
`scripts/init_sheets.py` 스크립트로 `storage/news_db.xlsx`의 2,319건을
Google Sheets에 1회 일괄 업로드

---

## 현재 상태 체크리스트

- [ ] Google Cloud 프로젝트 생성
- [ ] Sheets API / Drive API 활성화
- [ ] 서비스 계정 생성 및 JSON 키 다운로드
- [ ] 스프레드시트 생성 및 서비스 계정에 공유
- [ ] GitHub Secret 2개 등록 (`GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SPREADSHEET_ID`)
- [ ] 코드 구현 (`core/sheets.py`, `main.py`, `news.yml`, `requirements.txt`)
- [ ] 기존 데이터 마이그레이션 (`scripts/init_sheets.py`)

---

## 참고

- `gspread` 공식 문서: https://docs.gspread.org
- Google Cloud Console: https://console.cloud.google.com
- 서비스 계정 이메일 확인: Cloud Console → IAM → 서비스 계정 목록
