# 테마 및 디자인 시스템 가이드

> **최종 업데이트**: 2026-05-25
> **상태**: 현행 아키텍처 반영본
> **대상**: 개발자 및 UI 디자이너

---

## 1. 현재 테마 시스템 구조

프로젝트는 **두 가지 독립적인 렌더링 경로**를 운용한다.

```
[원본 Markdown 파일]
       │
       ├─► (경로 A: 서버 빌드)
       │     themes/*.py  TOKENS
       │       └─► build_site.py
       │              └─► publish/news/YYYY-MM-DD.html  (테마 완전 반영)
       │
       └─► (경로 B: SPA)
             app.html  (빌드 시 DYNAMIC 플레이스홀더 교체)
               └─► index.html  →  브라우저에서 JSON lazy-fetch
```

### 경로 A — 서버 빌드

`scripts/build_site.py`가 `themes/{name}.py` 의 `TOKENS` 딕셔너리를 읽어 CSS 변수·폰트·칩을 HTML에 직접 주입하고, 날짜별 정적 파일(`publish/news/YYYY-MM-DD.html`)을 생성한다.

### 경로 B — SPA

`app.html`에는 빌드 전 `<!-- DYNAMIC_* -->` / `/* DYNAMIC_* */` / `/* BUILD_* */` 마커가 삽입되어 있다. `build_site.py`가 이 마커들을 테마 데이터로 교체한 결과물이 `index.html`로 배포된다. 브라우저는 `index.html` 하나를 로드한 뒤 JSON을 lazy-fetch해 날짜별 콘텐츠를 렌더링한다.

---

## 2. 설정 파일: `config/theme_config.py`

테마를 바꾸려면 이 파일의 `SECTION_THEMES` 딕셔너리만 수정하면 된다.

```python
SECTION_THEMES = {
    "news":  "editorial",  # 뉴스브리핑 기본 테마
    "stock": "classic",    # 주식시황 기본 테마
    "email": "classic",    # 이메일 기본 테마
}
```

이 값 하나를 바꾸고 빌드·커밋·푸시하면 서버 빌드 HTML, SPA 기본값, 이메일 스타일이 모두 자동으로 반영된다. 다른 파일을 건드릴 필요가 없다.

---

## 3. 빌드 파이프라인 (`build_site.py`가 하는 일)

`build_site.py`는 `app.html` 안의 마커를 찾아 아래 순서로 교체한 뒤 `publish/index.html`을 생성한다.

| 마커 | 교체 내용 |
|---|---|
| `<!-- DYNAMIC_THEME_FONTS -->` | 현재 news 테마의 Google Fonts `@import` 태그 |
| `/* DYNAMIC_THEME_CSS */` | 현재 news 테마의 CSS 변수 블록 (`--bg`, `--card` 등) |
| `<!-- DYNAMIC_THEME_CHIPS -->` | 사용 가능한 테마 칩 목록 HTML (news 테마가 active) |
| `/* BUILD_SECTION_DEFAULTS */` | JS `SECTION_DEFAULTS` 상수 (섹션별 기본 테마명 JSON) |
| `<body data-theme="...">` | news 테마명으로 교체 |

또한 날짜별 뉴스 목록을 `publish/news/YYYY-MM-DD.json`으로 분리 저장한다(lazy-load용).

---

## 4. SPA 섹션별 테마 동작

### 상태 관리

```javascript
// 초기화 (페이지 로드 시)
state.newsTheme  = localStorage.getItem("theme-news")  || SECTION_DEFAULTS.news;
state.stockTheme = localStorage.getItem("theme-stock") || SECTION_DEFAULTS.stock;
```

`SECTION_DEFAULTS`는 빌드 시 `config/theme_config.py`의 `SECTION_THEMES`에서 읽어 주입된 JS 상수다.

### 함수 역할 분리

| 함수 | 역할 |
|---|---|
| `_applyThemeDOM(theme)` | DOM의 `data-theme`·칩 active만 변경 (저장 없음) — 섹션 전환 내부용 |
| `applyTheme(theme)` | 칩 클릭 시 호출. 현재 섹션의 localStorage에 저장 후 `_applyThemeDOM` 호출 |
| `switchSection(section)` | 섹션 전환 시 해당 섹션의 저장된 테마를 `_applyThemeDOM`으로 즉시 적용 |
| `resetTheme()` | `localStorage` 삭제 → `SECTION_DEFAULTS`로 즉시 복원 |

### 동작 흐름

- **뉴스 탭 → 주식 탭**: `switchSection("stock")` → `state.stockTheme` 로드 → `_applyThemeDOM` 호출
- **칩 클릭**: `applyTheme("editorial")` → `localStorage.setItem("theme-news", "editorial")` → DOM 변경
- **초기화 버튼**: `resetTheme()` → localStorage 항목 삭제 → `SECTION_DEFAULTS` 값으로 DOM 복원

---

## 5. 테마 변경 방법 (3가지 케이스)

### 케이스 1: 내 브라우저만 바꾸기

사이트 우측 상단 🎨 패널에서 테마 칩을 클릭한다. `localStorage`에 저장되므로 나만 적용되고 다른 방문자에게는 영향 없다.

### 케이스 2: 모든 방문자의 기본값 바꾸기

1. `config/theme_config.py`의 `SECTION_THEMES` 수정
2. `python scripts/build_site.py --all` 실행
3. `git add`, `git commit`, `git push`
4. Vercel 자동 배포 완료 후 확인

새로 접속하는 방문자는 변경된 테마를 보게 된다.

### 케이스 3: 기존 방문자에게 강제 적용

불가능하다. `localStorage`가 우선하기 때문에 서버 기본값이 바뀌어도 이미 방문한 사람에게는 반영되지 않는다. 본인 브라우저는 🎨 패널의 "사이트 기본값으로 초기화" 버튼으로 해결한다.

---

## 6. 신규 테마 추가 체크리스트

### Step 1: `themes/새테마.py` 파일 생성

```python
TOKENS = {
    "meta": {
        "name": "새테마",
        "font_cdn": "https://fonts.googleapis.com/css2?family=...",
    },
    "colors": {
        "bg":         "#ffffff",
        "card":       "#f8f8f8",
        "text":       "#111111",
        "muted":      "#888888",
        "navy":       "#1a2744",
        "blue":       "#2563eb",
        "blue_light": "#60a5fa",
        "border":     "#e5e7eb",
        "green":      "#16a34a",
        "orange":     "#ea580c",
        "code_bg":    "#f1f5f9",
    },
    "typography": {
        "font_sans": "'새폰트', sans-serif",
    },
}
```

### Step 2: 자동 감지 확인

`build_site.py`가 `themes/*.py`를 자동 스캔한다. 별도 등록이 필요 없다. 파일만 생성하면 칩 목록에 자동 추가된다.

### Step 3: `config/theme_config.py`에 적용

```python
SECTION_THEMES = {
    "news":  "새테마",
    ...
}
```

### Step 4: 빌드 및 확인

```bash
python scripts/build_site.py --all
# 브라우저에서 publish/index.html 열어 테마 확인
```

---

## 7. 이메일 테마

`SECTION_THEMES["email"]` 값을 `core/shared/mailer.py`의 `_get_email_theme()`가 읽어 이메일 렌더링에 적용한다.

- `templates/email_news.html` 템플릿이 `c.navy`, `c.blue`, `c.bg`, `c.border`, `c.muted`, `c.green` 등을 인라인 스타일로 주입한다.
- 웹폰트(`font_cdn`)는 웹메일 클라이언트(Gmail, Outlook 등)의 외부 CSS 차단 정책으로 로드되지 않을 수 있다. 색상은 인라인으로 삽입되므로 정상 적용된다.
- `colors` 키가 완비된 테마라면 `editorial`, `classic` 등 어느 테마든 이메일에 적용 가능하다.

---

## 8. 토큰 매핑 표

`themes/*.py`의 `colors` / `typography` 키가 SPA CSS 변수 및 이메일 템플릿 변수와 어떻게 연결되는지 정리한 표다.

| `themes/*.py` colors 키 | SPA CSS 변수 | 이메일 템플릿 변수 | 역할 |
|---|---|---|---|
| `bg` | `--bg` | `c.bg` | 페이지 배경 |
| `card` | `--card` | — | 카드 배경 |
| `text` | `--text` | — | 기본 텍스트 |
| `muted` | `--muted` | `c.muted` | 보조 텍스트 |
| `navy` | `--navy` | `c.navy` | 헤더/강조 |
| `blue` | `--blue` | `c.blue` | 링크/액센트 |
| `blue_light` | — | `c.blue_light` | 헤더 서브텍스트 |
| `border` | `--border` | `c.border` | 구분선 |
| `green` | `--green` | `c.green` | KO 링크 |
| `orange` | `--orange` | `c.orange` | 키워드 섹션 |
| `code_bg` | — | — | 코드 배경 |
| `typography.font_sans` | `--font-family` | `t.font_sans` | 폰트 패밀리 |

---

## 9. 참고: 현재 적용 중인 테마 파일 목록

| 파일 | 테마명 | 특징 |
|---|---|---|
| `themes/classic.py` | classic | Classic Navy. 진한 네이비 계열. 기본 레이아웃 |
| `themes/editorial.py` | editorial | 신문 스타일. Noto Serif KR + 미색 배경 + 적갈색 accent |
| `themes/terminal.py` | terminal | 개발자 터미널. 딥블랙 배경 + 그린 텍스트 + IBM Plex Mono |
| `themes/ink.py` | ink | 잉크 신문 스타일. 붉은 accent |
| `themes/forest.py` | forest | 핀테크 그린. 에메랄드 accent |
| `themes/minimal.py` | minimal | 넓은 여백, Pretendard 기반 |

---

## 10. 아카이브 페이지 통합 및 기능 동기화

2026-06-09 리팩토링을 통해 모든 테마의 아카이브 페이지(`archive.html`)가 기능적으로 통일되었습니다.

### 주요 기능 사양
- **3개 채널 탭 메뉴**: 뉴스 브리핑, 주식 시황, AI이슈에 대한 탭이 모든 테마에서 제공되며 클릭 시 부드럽게 목록이 교체됩니다.
- **실시간 통합 검색**: 상단 검색 입력창과 체크박스 필터를 사용해 3개 카테고리의 모든 리포트를 실시간으로 조회하고 키워드 하이라이팅을 제공합니다.
- **상세 리포트 이동**: 검색 결과 목록에서 기사 출처 링크(`h.art.link`)가 없을 경우, 당일 로컬 리포트 상세 페이지(`h.report_url`)로 안전하게 폴백(fallback)하여 정상적인 상세 이동을 보장합니다.

### 테마별 구현 방식
1. **표준 테마 (Classic, Ink, Forest)**:
   - `themes/base.py`에서 `stock_items`와 `ai_items`를 Jinja2 컨텍스트에 추가 주입합니다.
   - `templates/web_archive.html` 공통 템플릿 파일 하나에 UI 마크업과 JS 로직을 구현하여 테마별 CSS 토큰과 매핑합니다.
2. **커스텀 테마 (Editorial, Minimal, Terminal)**:
   - 각 테마 클래스(`themes/editorial.py`, `themes/minimal.py`, `themes/terminal.py`)의 `render_archive(ctx)` 메소드 내에 해당 테마 고유의 비주얼 스타일로 마크업과 JS 코드를 내장합니다.
   - **주의**: Python f-string 기반의 레이아웃 코드로 구성되어 있으므로, 템플릿 내 자바스크립트용 단일 중괄호(`{}`)는 반드시 이중 중괄호(`{{`, `}}`)로 이스케이프하여 빌드 타임에 컴파일 에러가 발생하지 않도록 해야 합니다.

