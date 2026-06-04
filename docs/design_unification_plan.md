# 디자인 통일화 계획 메모

> 상태: 검토 중 (미착수)  
> 작성: 2026-06-04  
> 목적: 뉴스 인덱스 / 주식 시황 페이지 간 디자인 차이 원인 파악 및 통일 방향 검토

---

## 1. 현재 파일 역할 지도

### 템플릿 (Jinja2 — 정적 서브페이지 생성용)

| 파일 | 생성 결과 | 빌드 스크립트 |
|------|----------|--------------|
| `templates/web_news.html` | `publish/news/YYYY-MM-DD.html` | `build_site.py` |
| `templates/web_stock.html` | `publish/stock/YYYY-MM-DD.html` | `build_stock_site.py` |
| `templates/web_archive.html` | `publish/archive.html` | `build_site.py` |
| `templates/web_stock_archive.html` | `publish/stock/archive.html` | `build_stock_site.py` |

### SPA 원본 (뉴스 인덱스)

| 파일 | 역할 |
|------|------|
| `publish/app.html` | **직접 편집하는 SPA 원본** |
| `publish/index.html` | `build_site.py` 실행 시 app.html에서 자동 생성 |
| `publish/stock/index.html` | `build_stock_site.py`가 별도 생성하는 주식 인덱스 |

### 테마 주입 경로

```
themes/
  editorial.py  → TOKENS (색상, 폰트) + render_report() 직접 구현
  terminal.py   → TOKENS + render_report() 직접 구현
  classic.py    → TOKENS만 (렌더링은 base.py가 담당)
  minimal.py    → TOKENS만
  ink.py        → TOKENS만
  forest.py     → TOKENS만
  base.py       → 위 테마 토큰을 읽어 web_*.html 템플릿에 CSS 주입

config/theme_config.py → 섹션별 기본 테마 (현재 모두 editorial)

build_site.py → app.html 플레이스홀더 3곳에 런타임 주입
  ├─ <!-- DYNAMIC_THEME_FONTS -->   Google Fonts CDN
  ├─ /* DYNAMIC_THEME_CSS */        6개 테마 CSS 변수 블록
  └─ <!-- DYNAMIC_THEME_CHIPS -->   테마 선택 UI 칩
```

---

## 2. 디자인이 다른 근본 원인

뉴스 인덱스(`index.html`)와 주식 시황 페이지(`stock/*.html`)는 **구조 자체가 다릅니다.**

| 항목 | 뉴스 인덱스 (app.html → index.html) | 주식/뉴스 서브페이지 (*.html) |
|------|-----------------------------------|-----------------------------|
| **타입** | 동적 SPA (Single-Page App) | 정적 HTML |
| **CSS 변수명** | `--blue`, `--navy`, `--bg`, `--card` | `--ink`, `--paper`, `--rule`, `--accent` |
| **헤더 Nav** | `.hnav-tab` (탭 + 하단 밑줄) | 단순 `nav a` (font-weight 토글) |
| **테마 전환** | 런타임 6종 전환 가능 | 불가 (빌드 시 1종 고정) |
| **모바일 대응** | 명시적 `@media` 처리 | 미처리 |
| **Z-index** | 200 | 100 |
| **폰트** | 테마별 동적 | Noto Serif KR 고정 |

**같은 editorial 테마라도 다르게 보이는 이유**: CSS 변수 이름 체계가 달라서입니다.
- SPA: `var(--navy)`, `var(--blue)` → Classic Navy 기준 변수명
- 서브페이지: `var(--ink)`, `var(--paper)` → Editorial 고유 변수명

---

## 3. 자주 묻는 질문 (Q&A)

### Q1. 주식 서브페이지에 다른 테마를 적용하는 방법은?

**가능합니다.** `config/theme_config.py`의 `THEME_STOCK_DEFAULT`를 바꾸면 됩니다.

```python
# config/theme_config.py
THEME_STOCK_DEFAULT = "terminal"  # editorial → terminal로 변경
```

이후 `python scripts/build_stock_site.py` 실행하면 전체 주식 페이지가 해당 테마로 재빌드됩니다.  
단, **런타임 전환은 불가** — 한 번에 하나의 테마만 적용됩니다.  
런타임 전환을 원한다면 → 아래 C안 참고.

---

### Q2. web_archive.html과 web_stock_archive.html — 2개로 둘 필요 있나?

**사실상 동일한 파일**입니다. 차이점:

| | web_archive.html | web_stock_archive.html |
|---|---|---|
| 제목 | `전체 목록` | `주식시황 목록` |
| 링크 경로 | `news/{{ item.date }}.html` | `{{ item.date }}.html` |
| 항목 라벨 | `📄 ... 리포트` | `📊 ... 시황` |
| CSS | 완전 동일 | 완전 동일 |

→ **하나로 통합 가능합니다.** 파라미터(제목, 링크 prefix, 라벨 이모지)를 Jinja2 변수로 추출하면 템플릿 1개로 양쪽 모두 처리 가능합니다.

```jinja2
{# 통합된 단일 archive 템플릿 예시 #}
<title>{{ archive_title | default("전체 목록") }}</title>
<a href="{{ item_prefix | default("news/") }}{{ item.date }}.html">
  {{ item_icon | default("📄") }} {{ item.display }}
</a>
```

→ **TODO: 통합 시 web_archive.html 하나로 줄이기** (우선순위 낮음)

---

### Q3. stock/archive.html 디자인을 살리면서 테마 토큰만 주입할 수 있나?

**가능합니다.** `web_stock_archive.html`(또는 통합 템플릿)에 테마 CSS 변수를 Jinja2로 주입하면 됩니다.

현재 `web_archive.html` / `web_stock_archive.html`의 CSS는 `var(--color-navy)`, `var(--color-blue-light)` 등을 이미 사용하고 있습니다.  
빌드 스크립트에서 선택된 테마의 토큰을 `{{ css_root }}` 블록으로 전달하면 됩니다.

```python
# build_stock_site.py 에서
theme = load_theme(THEME_STOCK_DEFAULT)
css_root = theme.render_css_root()  # :root { --color-navy: ...; }
html = tpl.render(css_root=css_root, items=items)
```

→ **TODO: archive 페이지에 테마 토큰 주입 추가**

---

### Q4. 상단바(헤더 네비게이션) — 뉴스 인덱스 vs 주식 인덱스 차이

#### 현재 구조 비교

**뉴스 인덱스 (app.html/index.html):**
```
[📰 AI News Brief]  [📰뉴스] [🤖AI이슈] [📊주식] [📚아카이브]   ... [🎨] [GitHub]
  ← 로고 고정        ← 탭 메뉴 (flex:1, 좌측 정렬)            → 우측 액션버튼
```
- 탭 클래스: `.hnav-tab` (하단 밑줄 active 표시)
- 모바일(<600px): `.tab-label` 숨김 → 이모지만 표시
- 문제: **넓은 화면에서 탭이 좌측으로 몰려 우측 공간이 비어 보임**

**주식 인덱스 (stock/index.html):**
```
[📰 AI News Daily]                        [뉴스] [주식] [아카이브]
  ← 로고                                         ← 단순 nav a (우측 정렬)
```
- 헤더: `justify-content: space-between` → 로고 좌, 메뉴 우
- 클래스: 단순 `nav a` (font-weight 토글)
- 모바일 대응: 없음

#### 개선 방향 검토

**현재 문제점:**
1. 뉴스 인덱스: 넓은 화면에서 탭이 왼쪽으로 치우침 (flex:1 컨테이너가 넓어짐)
2. 주식 인덱스: 메뉴가 오른쪽으로 치우침, 모바일 미대응
3. 이름이 다름: "AI News Brief" vs "AI News Daily"

**권장 통일 레이아웃 (미착수):**
```
[로고]  —————중앙 정렬된 탭 메뉴————  [우측 액션]
justify-content: space-between + margin: auto 조합
```

```css
header { display: flex; align-items: center; justify-content: space-between; }
.header-nav { position: absolute; left: 50%; transform: translateX(-50%); }
/* 또는 */
.logo { flex: 1; }
.header-nav { flex: 0; }
.header-actions { flex: 1; display: flex; justify-content: flex-end; }
```

→ **TODO: 상단바 중앙 정렬 + 이름 통일 ("AI News Brief" 또는 "AI News Daily" 하나로)**

---

## 4. 통일 방향 옵션 (A/B/C안 상세 비교)

### A안 — 정적 서브페이지를 SPA 스타일로 맞추기

**무엇을 바꾸나**: `templates/web_stock.html`, `templates/web_news.html`의 CSS 변수명을 SPA와 동일하게 교체

```
변경 전 (현재):   --ink, --paper, --rule, --accent
변경 후 (A안):    --blue, --navy, --bg, --card (SPA 기준)
```

**실제로 어떻게 보이나**: 주식 시황 개별 페이지가 SPA(뉴스 인덱스)와 동일한 Classic Navy 색상 체계가 됨. 지금의 따뜻한 베이지/갈색 editorial 느낌이 파란색 계열로 바뀜.

**작업량**: 중간 (템플릿 CSS 수정 + 전체 재빌드)  
**장점**: 구현 단순, SPA와 시각적 일관성  
**단점**: editorial 테마 고유의 신문 느낌 사라짐  
**적합한 경우**: 전체 사이트를 깔끔한 단일 톤으로 통일하고 싶을 때

---

### B안 — SPA 안에서 모두 처리 (서브페이지 폐지)

**무엇을 바꾸나**: 개별 `stock/YYYY-MM-DD.html`, `news/YYYY-MM-DD.html` 파일 생성을 중단하고, SPA(index.html) 안에서 모든 콘텐츠를 렌더링

**실제로 어떻게 보이나**: 
- `https://site.com/news/2026-06-04.html` 같은 URL이 사라짐
- `https://site.com/#news-2026-06-04` 형태로 변경되거나, URL은 유지하되 내용만 SPA에서 동적 로드
- 모든 페이지가 동일한 SPA UI (사이드바, 탭 메뉴 등) 안에서 표시됨

**작업량**: 대규모 (SPA JS 대폭 수정, URL 라우팅 추가, SEO 대응 필요)  
**장점**: 완전한 통일, 유지보수 단일화  
**단점**: 공유 링크가 SPA 라우팅 방식으로 바뀜, SEO 악화 가능, 이메일에 심은 링크 깨짐  
**적합한 경우**: 장기적으로 풀스택 앱으로 발전시키려 할 때

---

### C안 — 서브페이지에 테마 전환 UI 추가

**무엇을 바꾸나**: `web_stock.html`, `web_news.html` 정적 페이지에 SPA의 테마 스위처 JS/CSS를 복사해 넣음

**실제로 어떻게 보이나**:
- 주식/뉴스 개별 페이지에도 우측 상단에 🎨 테마 전환 버튼이 생김
- 사용자가 editorial → terminal 등으로 바꿀 수 있음 (localStorage 저장)
- SPA와 서브페이지 모두 동일한 6종 테마 선택 경험

**작업량**: 중간 (템플릿에 JS 블록 추가 + 빌드 시 6개 테마 CSS 모두 삽입)  
**장점**: 두 세계의 장점 유지 (서브페이지 독립성 + SPA와 동일한 UX)  
**단점**: 중복 코드 (JS/CSS가 각 정적 파일에 반복 삽입되어 파일 크기 증가)  
**적합한 경우**: 현재 구조를 최대한 유지하면서 UX만 통일하고 싶을 때

---

### 옵션 비교 한눈에 보기

| 기준 | A안 | B안 | C안 |
|------|:---:|:---:|:---:|
| 작업량 | 중간 | 대규모 | 중간 |
| URL 구조 변경 | 없음 | 있음 | 없음 |
| editorial 느낌 유지 | ❌ | ✅ | ✅ |
| 런타임 테마 전환 | ❌ | ✅ | ✅ |
| SEO 영향 | 없음 | 있음 | 없음 |
| 코드 중복 | 적음 | 없음 | 많음 |
| 이메일 링크 호환 | ✅ | ❌ | ✅ |

---

## 5. 우선순위별 TODO 목록

> 아래 항목들은 모두 미착수입니다. 우선순위는 주관적 판단 기준입니다.

### 🔴 높음 (헤더/네비게이션 통일)
- [ ] 로고 이름 통일: "AI News Brief" vs "AI News Daily" 중 하나로
- [ ] 뉴스 인덱스 헤더 탭 중앙 정렬 (넓은 화면에서 탭이 왼쪽으로 쏠리는 문제)
- [ ] 주식 인덱스 헤더 모바일 대응 추가
- [ ] 두 인덱스 헤더 구조 통일 (`.hnav-tab` 방식 또는 `nav a` 방식 중 선택)

### 🟡 중간 (아카이브 통합)
- [ ] `web_archive.html` + `web_stock_archive.html` 파라미터로 통합 (템플릿 1개)
- [ ] 아카이브 페이지에 테마 토큰 주입 추가

### 🟢 낮음 (전체 디자인 통일 — A/B/C안 중 하나 선택 후 진행)
- [ ] **방향 결정**: A안(CSS 변수 통일) / B안(SPA 통합) / C안(서브페이지 테마 전환) 중 하나
- [ ] 결정 후 현재 정적 HTML 전체 백업
- [ ] 선택한 방향으로 템플릿 수정 + 전체 재빌드

---

## 6. 현재 상태 스냅샷 (2026-06-04 기준)

### 적용 중인 테마
- 뉴스 인덱스 (SPA): editorial (기본), 런타임 6종 전환 가능
- 뉴스 서브페이지: editorial 고정
- 주식 인덱스: editorial 고정
- 주식 서브페이지: editorial 고정
- 이메일: classic

### 파일 수
- 뉴스 서브페이지: ~84개 (`publish/news/*.html`)
- 주식 서브페이지: 14개 (`publish/stock/*.html`)
- 템플릿: 4개 web, 3개 email

### 백업 위치
- `docs/backup/` — 기존 작업 백업 보관 위치
