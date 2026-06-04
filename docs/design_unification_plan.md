# 디자인 통일화 계획

> 상태: 검토 완료 / 단계적 진행 중  
> 작성: 2026-06-04  
> 목적: 현황 파악 → 방향 결정 → 조금씩 구현

---

## 1. 파일 역할 지도 (정확한 버전)

### 아카이브 페이지 — 생성 경로가 다름!

| 실제 파일 | 생성 방법 | 디자인 |
|-----------|----------|--------|
| `publish/archive.html` | `themes/editorial.py::render_archive()` → **Python f-string 직접 생성** | 신문 마스트헤드 스타일 (72px 제목, 탭 3개) |
| `publish/stock/archive.html` | `themes/base.py::render_stock_archive()` → `templates/web_stock_archive.html` Jinja2 | 단순 카드 리스트 |

> **핵심**: `templates/web_archive.html`은 editorial 테마에서 **사용하지 않음**.  
> editorial.py가 Python으로 직접 HTML을 만들기 때문. `web_archive.html`은 classic/ink/forest 등 base 테마용.

### 서브페이지 (개별 날짜 파일)

| 템플릿 | 생성 결과 | 빌드 스크립트 |
|--------|----------|--------------|
| `templates/web_news.html` | `publish/news/YYYY-MM-DD.html` | `build_site.py` |
| `templates/web_stock.html` | `publish/stock/YYYY-MM-DD.html` | `build_stock_site.py` |
| `templates/web_archive.html` | *editorial 테마에서는 미사용* | — |
| `templates/web_stock_archive.html` | `publish/stock/archive.html` | `build_stock_site.py` |

### SPA (뉴스 메인 인덱스)

| 파일 | 역할 |
|------|------|
| `publish/app.html` | **직접 편집하는 SPA 원본** |
| `publish/index.html` | `build_site.py` 실행 시 app.html에서 자동 생성 |
| `publish/stock/index.html` | `build_stock_site.py`가 별도 생성하는 주식 인덱스 |

---

## 2. Q&A (정확한 답변)

### Q1. SPA는 런타임 테마 전환이 되는데 서브페이지는 왜 안 되나?

**SPA (index.html):**
- `build_site.py`가 실행될 때 6개 테마 CSS 블록을 **모두** `/* DYNAMIC_THEME_CSS */` 플레이스홀더에 삽입함
- 각 테마 CSS는 `[data-theme="editorial"] :root { ... }` 형태로 selector가 걸림
- JS가 `document.documentElement.dataset.theme = "terminal"` 으로 속성 변경하면 즉시 전환
- **결론: 6개 CSS가 모두 파일 안에 있으므로 런타임 전환 가능**

**서브페이지 (news/YYYY-MM-DD.html 등):**
- `build_site.py` 실행 시 선택된 테마 하나만 `:root { ... }`로 주입됨
- 다른 테마 CSS는 파일 안에 없음 → 런타임 전환 불가
- **결론: 테마를 바꾸려면 다른 THEME_NEWS_DEFAULT 설정 후 재빌드 필요**

**만약 서브페이지에도 런타임 전환을 원한다면:**  
→ 6개 테마 CSS를 서브페이지에도 모두 삽입하고 JS 추가 (C안, 아래 참조)

---

### Q2. publish/archive.html vs publish/stock/archive.html — 왜 다르게 보이나?

**두 파일의 실제 차이:**

| | `publish/archive.html` | `publish/stock/archive.html` |
|---|---|---|
| 생성 | editorial.py Python 코드 | web_stock_archive.html 템플릿 |
| 디자인 | 신문 마스트헤드 (72px 이탤릭 제목, IBM Plex Mono) | 단순 카드 리스트 (헤더 navbar) |
| 탭 | ✅ 뉴스/주식/AI이슈 탭 있음 | ❌ 없음 (주식 목록만) |
| 홈 링크 | `location.href='/'` ← **버그** | `location.href='/'` ← **버그** |

**중요 발견: `publish/archive.html`은 이미 탭이 있음!**  
뉴스/주식/AI이슈 세 탭이 있고 JS로 전환됨. 이것이 유저가 원하는 "통합 아카이브"에 가장 가까움.

**"`web_archive.html`을 `web_stock_archive.html`로 덮어쓰면 같아지나?"**  
→ **아니요.** `publish/archive.html`은 `web_archive.html` 템플릿에서 오는 게 아님.  
editorial.py Python 코드가 직접 HTML을 만들기 때문에 템플릿 교체로는 영향 없음.  
→ 바꾸고 싶으면 `themes/editorial.py::render_archive()` 함수를 수정해야 함.

---

### Q3. 헤더 이름이 "AI News Brief" vs "AI News Daily"로 다른 이유?

**현재 상태 (미통일):**

| 파일 | 이름 | 홈 링크 |
|------|------|---------|
| `publish/app.html` (SPA 원본) | **AI News Brief** | `window.location.reload()` |
| `templates/web_news.html` | **AI News Daily** | `'../'` ← 이전 세션에서 수정 |
| `templates/web_stock.html` | **AI News Daily** | `'../'` ← 이전 세션에서 수정 |
| `templates/web_archive.html` | **AI News Daily** | `'/'` ← **버그 (GitHub Pages)** |
| `templates/web_stock_archive.html` | **AI News Daily** | `'/'` ← **버그 (GitHub Pages)** |
| `publish/stock/index.html` (생성) | **AI News Daily** | `'/'` ← **버그 (GitHub Pages)** |
| `themes/editorial.py` `_layout()` | **AI News Brief** | `/` ← **버그** |

이전 세션에서는 **href만 `'../'`로 수정**했고 이름 통일은 안 했음.

**→ 통일 방향: 모두 "AI News Brief"로 (SPA 기준)**

---

## 3. 사용자 비전 — 탭별 색상 테마

**원하는 구조:**
```
[ 📰 AI News Brief ]  [📰뉴스] [🤖AI이슈] [📊주식] [📚아카이브]
```
- 헤더 네비게이션 구조: 모든 페이지 동일
- 뉴스 탭 활성화 시: 파란색 계열 (`--color-navy: #1e3a5f`)
- AI이슈 탭 활성화 시: 보라/청록 계열
- 주식 탭 활성화 시: 현재 editorial 갈색/와인 계열 (유지)
- 아카이브: 통합 탭 (뉴스/AI이슈/주식 분류)

**현재 editorial.py 아카이브가 이미 탭 3개를 가짐** → 이것을 다듬는 것이 우선

---

## 4. 통일 방향 — 채택: C안 변형 (탭별 색상 테마)

A안 (SPA 스타일로 서브페이지 맞추기)은 **제외** — editorial 고유 디자인 포기하는 것이므로.

### 채택 방향: 점진적 통일 (B+C 혼합)

**1단계 — 즉시 가능 (버그 수정 + 이름 통일)**
- 모든 파일에서 로고 이름 → "AI News Brief"
- 아카이브 템플릿 홈 링크 `'/'` → `'../'` 수정
- editorial.py `_layout()` 홈 링크도 수정

**2단계 — 탭별 색상 토큰 시스템**
- 각 탭(뉴스/AI이슈/주식)별 CSS 변수 세트 정의
- 서브페이지는 `THEME_NEWS_DEFAULT`, `THEME_STOCK_DEFAULT` 등으로 구분 빌드
- 같은 구조이지만 다른 색상 → `:root` 변수값만 교체

**3단계 — 통합 아카이브 개선**
- `themes/editorial.py::render_archive()` 에 검색 기능 추가
- 탭 전환 시 URL hash 동기화 (직접 링크 가능하도록)
- 리스트 클릭 시 해당 서브페이지로 자연스럽게 이동

---

## 5. 구현 순서 (우선순위)

### 🔴 1단계: 버그 수정 (즉시)

- [ ] `templates/web_archive.html` 로고 이름 "AI News Brief", 홈 링크 `'/'` → `'../'`
- [ ] `templates/web_stock_archive.html` 동일 수정
- [ ] `themes/editorial.py` `_layout()` 로고 이름/홈 링크 수정
- [ ] `publish/stock/index.html` 생성하는 `build_stock_site.py` 에서 로고 이름/홈 링크 수정

### 🟡 2단계: 탭별 색상 분리

- [ ] `config/theme_config.py` 에 `THEME_NEWS_DEFAULT`, `THEME_AI_DEFAULT`, `THEME_STOCK_DEFAULT` 명시
- [ ] 뉴스 서브페이지 테마 → classic navy 계열로 변경 (검토)
- [ ] 주식 서브페이지 테마 → 현재 editorial 유지
- [ ] AI이슈 서브페이지 테마 → 별도 색상 지정

### 🟢 3단계: 통합 아카이브 고도화

- [ ] `editorial.py::render_archive()` 검색 기능 추가 (`<input>` + JS filter)
- [ ] 아카이브 탭 전환 시 URL hash 저장 (`#news`, `#stock`, `#ai`)
- [ ] 각 탭 항목 클릭 → 해당 서브페이지로 이동 (이미 동작, 경로 점검)
- [ ] `publish/stock/archive.html` 을 `publish/archive.html#stock` 으로 리다이렉트 고려

### ⚪ 나중에

- [ ] 헤더 탭 중앙 정렬 (넓은 화면 개선)
- [ ] 주식 인덱스 모바일 대응
- [ ] `web_archive.html` + `web_stock_archive.html` 파라미터 통합 (base 테마용)

---

## 6. 현재 테마 적용 현황

| 페이지 | 테마 | 런타임 전환 |
|--------|------|------------|
| 뉴스 인덱스 (SPA) | editorial (기본) + 6종 전환 가능 | ✅ |
| 뉴스 서브페이지 | editorial | ❌ |
| 주식 인덱스 | editorial | ❌ |
| 주식 서브페이지 | editorial | ❌ |
| AI이슈 서브페이지 | editorial | ❌ |
| 아카이브 (뉴스) | editorial (Python 생성, 탭 있음) | ❌ |
| 아카이브 (주식) | editorial (Jinja2, 탭 없음) | ❌ |
| 이메일 | classic | — |

---

## 7. 핵심 발견사항 요약

1. **`publish/archive.html`이 이미 3탭 구조** — editorial.py Python 코드가 뉴스/주식/AI이슈 탭을 직접 생성. 이것을 발전시키는 게 가장 빠른 경로.

2. **`web_archive.html` 템플릿은 editorial에서 미사용** — 편집해도 publish/archive.html에 반영 안 됨. `themes/editorial.py::render_archive()` 수정이 필요.

3. **두 archive 페이지의 디자인이 다른 이유** — 생성 방식이 다름 (Python vs Jinja2), 같은 CSS를 쓰는 게 아님.

4. **홈 링크 버그 미완성** — 아카이브 템플릿 2개와 editorial.py `_layout()` 아직 `'/'` 그대로. 다음 작업에서 수정 필요.
