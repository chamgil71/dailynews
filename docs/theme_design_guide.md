# 🎨 테마 및 디자인 시스템 연동 가이드라인
> **작성일**: 2026-05-24  
> **상태**: 최종 확정  
> **대상**: 개발자 및 UI 디자이너용 디자인 가이드북

본 문서는 일주일 넘게 디자인 테마(`editorial`, `terminal` 등)가 메인 사이트에 제대로 반영되지 않고 깨졌던 문제를 완전히 종식하고, 향후 신규 테마를 누구나 에러 없이 3분 만에 추가할 수 있도록 돕는 **이중 렌더링 시스템 통합 테마 가이드라인**입니다.

---

## 1. 이중 테마 렌더링 구조의 이해

현재 사이트는 **서버사이드 정적 페이지 생성(Jinja2)**과 **클라이언트사이드 SPA 동적 생성(JSON Fetch)**이라는 완전히 별개의 두 가지 렌더링 경로를 채택하고 있습니다. 

```
[원본 Markdown 파일]
       │
       ├─► (경로 A: 서버 빌더) ──► themes/{name}.py 로드 ──► publish/{date}.html (테마 완벽 반영!)
       │
       └─► (경로 B: SPA 사이트) ──► reports-data.json ──► index.html (SPA 자바스크립트가 classic 테마로 강제 재렌더링 ❌)
```

- **Jinja2 서버 빌드**: `scripts/build_site.py`가 돌면서 `themes/editorial.py` 등의 파이썬 파일 내 `TOKENS`와 `_CSS`를 바인딩하여 완벽한 스타일을 입힌 독립 HTML을 완성합니다.
- **클라이언트 SPA**: 메인 `index.html`은 `publish/reports-data.json`에서 순수 텍스트만 fetch한 뒤, **SPA 내부에 하드코딩된 자체 CSS 변수군**만 적용해 화면을 강제로 classic 테마로 고정해 그립니다.
- **해결 핵심**: 서버사이드 파이썬 테마 파일(`themes/{name}.py`)에 정의된 디자인 토큰들을 **클라이언트 SPA(`app.html`)의 CSS 변수 및 스타일시트로 완벽히 이식하여 정렬**해야만 이 미스매치가 완전히 종결됩니다.

---

## 2. 테마별 디자인 토큰(Design Tokens) 정렬 규정

서버 테마 모듈(`themes/*.py`)에 선언된 디자인 토큰과 SPA(`app.html`) CSS 변수 간의 매핑 규칙입니다. 새로운 테마를 정의할 때는 반드시 이 변수 쌍을 일치시켜야 합니다.

| 파이썬 토큰 Key (`themes/*.py`) | CSS 변수명 (`app.html` `:root`) | 역할 및 권장 스타일 가이드 |
| :--- | :--- | :--- |
| `colors.bg` | `--bg` | 전체 페이지 배경색 (부드러운 HSL/Hex 권장) |
| `colors.card` | `--card` | 뉴스 기사 카드의 배경색 |
| `colors.text` | `--text` | 기본 텍스트 색상 (가독성을 위한 고대비 컬러) |
| `colors.muted` | `--muted` | 날짜, 카테고리 등 보조 텍스트 색상 |
| `colors.accent` | `--blue` (또는 `--accent`) | 브랜드 핵심 액센트 컬러 (하이라이트, 링크, 버튼) |
| `colors.rule` | `--border` | 섹션 구분선 및 테두리 색상 |
| `meta.font_cdn` | `@import url(...)` | Google Fonts 연결 CDN 주소 |
| `meta.font_family` | `font-family` | 본문에 적용될 타이포그래피 우선순위 폰트 스택 |

---

## 3. SPA 내 테마 CSS 완벽 이식 규격 (Phase 3 적용본)

1주일 동안 테마가 깨졌던 문제를 완전히 해결하기 위해, SPA(`app.html`) 내부 `<style>` 태그 안에 **`editorial`과 `terminal` 테마의 디자인 토큰을 CSS Selector 규격으로 선언**해야 합니다.

### 3-1. Editorial (신문 스타일) 디자인 스키마
```css
/* SPA 내 Editorial 테마 정의 */
[data-theme="editorial"] {
  --bg:       #f4ede0; /* 부드러운 미색 신문지 톤 */
  --card:     #ece2cf; 
  --text:     #1a1612; /* 잉크 느낌의 다크 그레이 */
  --muted:    #8a7e6f; 
  --border:   #2b231a; /* 강한 신문 경계선 */
  --blue:     #8b2a1f; /* 적갈색 신문 액센트 */
  --accent:   #8b2a1f;
  font-family: 'Noto Serif KR', Georgia, serif !important;
}

/* Editorial 전용 추가 장식 클래스 (가이드라인) */
[data-theme="editorial"] .report-card {
  border-top: 6px solid var(--border) !important;
  border-bottom: 1px solid var(--border) !important;
  border-left: none !important;
  border-right: none !important;
  border-radius: 0px !important; /* 각진 신문 그리드 */
}
```

### 3-2. Terminal Dark (개발자 터미널 스타일) 디자인 스키마
```css
/* SPA 내 Terminal Dark 테마 정의 */
[data-theme="terminal"] {
  --bg:       #0c0f12; /* 완전한 딥 블랙 */
  --card:     #161b22; 
  --text:     #00ff66; /* 빈티지 모노크롬 그린 */
  --muted:    #58a6ff; /* 사이버 펑크 블루 */
  --border:   #30363d; 
  --blue:     #00ff66;
  --accent:   #00ff66;
  font-family: 'IBM Plex Mono', 'Courier New', monospace !important;
}

[data-theme="terminal"] .report-card {
  border: 1px solid var(--blue) !important;
  box-shadow: 0 0 10px rgba(0, 255, 102, 0.2) !important;
}
```

---

## 4. 서버-클라이언트 테마 동기화 구현 방안 (선택 가이드)

테마 동기화를 영구적으로 견고하게 유지하기 위한 **2가지 기술적 대안**입니다. 아키텍처적 유연성을 고려하여 선택 이식합니다.

### 💡 대안 A. 정적 HTML Fetch 주입 방식 (추천)
SPA가 데이터를 JSON으로 받아 파싱하는 대신, 이미 완벽한 테마 스타일이 입혀져 저장되어 있는 **날짜별 정적 HTML 파일 자체를 Fetch하여 DOM에 바로 심어버리는 구조**입니다.
* **장점**: 서버사이드 테마 모듈(`themes/*.py`) 하나만 고치면 SPA 코드 수정 없이 웹사이트 테마도 100% 실시간 자동 정렬됩니다.
* **JS 구현 핵심 가이드**:
  ```javascript
  async function selectDate(date) {
    state.activeDate = date;
    const reportArea = document.getElementById("reportArea");
    try {
      // 1. 서버가 빌드해놓은 완벽한 테마 HTML을 직접 가져옴
      const res = await fetch(`${date}.html`);
      if (!res.ok) throw new Error();
      const rawHtml = await res.text();
      
      // 2. HTML 내부의 본문 영역(#reportArea 또는 body 내용)만 파싱하여 주입
      const parser = new DOMParser();
      const doc = parser.parseFromString(rawHtml, 'text/html');
      const bodyContent = doc.querySelector('.wrap').innerHTML;
      reportArea.innerHTML = bodyContent;
    } catch {
      // 실패 시 JSON 데이터를 기반으로 한 기본 fallback 렌더링
      reportArea.innerHTML = renderReportFallback(state.reports.find(r=>r.date===date));
    }
  }
  ```

### 💡 대안 B. SPA 내 스타일 시트 동적 맵 바인딩 방식
서버 빌드 시 사용한 테마 정보를 JSON 메타데이터에 담아 보내고, SPA 자바스크립트가 바디 태그의 `data-theme` 값을 인젝션하는 방식입니다.
* **장점**: 전통적인 SPA 탭 전환 시의 고속 렌더링 속도가 유지됩니다.
* **단점**: 신규 테마 추가 시 파이썬과 `app.html` 양쪽에 디자인 CSS를 둘 다 선언해 주어야 합니다.

---

## 5. 신규 테마 추가를 위한 Step-by-Step 체크리스트

향후 새로운 테마(예: `midnight_purple`)를 프로젝트에 추가할 때는 반드시 다음 체크리스트 순서대로 수행해야 시스템 꼬임이 방지됩니다.

- [ ] **Step 1: 서버 테마 파일 생성**
  - `themes/midnight_purple.py` 파일을 생성하고 `TOKENS` 딕셔너리(colors, typography)를 기술합니다.
- [ ] **Step 2: 테마 로더 등록**
  - `config/theme_config.py` 파일의 `DESIGN_TEMPLATES` 리스트에 새로운 테마의 식별키(`midnight_purple`)와 한글 설명을 추가하여 웹 UI에 표시되도록 설정합니다.
- [ ] **Step 3: SPA CSS 정의 (대안 B 채택 시)**
  - `publish/app.html` 파일 내부 스타일 선언 단락에 `[data-theme="midnight_purple"]` CSS 선택자를 열고, 1대1 매핑되는 컬러 변수(테이블 2장 참조)들을 선언해 줍니다.
- [ ] **Step 4: Vercel 빌드 확인**
  - 로컬 테스트 및 깃 푸시 후 Vercel 프리뷰 채널에 들어가 테마 선택 드롭다운 박스에서 신규 테마가 깨짐 없이 아주 유려하게 로딩되는지 육안 확인합니다.
