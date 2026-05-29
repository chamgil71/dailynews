

## 질의 26-05-22 09:

 c:\ai\dailynews\.github 이 프로젝트의 내용을 깃허브액션을 통해 발행하고 있다. 세가지 문제점이 있어.  1. 뉴스데일리 테마를 'editorial' 으로 변경했는데 사이트 가보면 반영이 되어 있지 않아. 2. 
  뉴스데일리 메일템플릿을 만들고 그걸 적용하고 있어.  메일에서는 하단의 뉴스기사리스트는 안보내고 핵심내용, 키워드 등만 보내려했는데 리스트가 같이 발송돼.  3. 해당 내용은 깃허브페이지에서는 제대로       
  나오는데 vercel로 서비스하는 곳에서는 제대로 표시가 안돼. 주식시황 워크플로우가 달라서 그런가?  원인을 정확하게 판단하고 정리해줘줘 

---

## 답변 26-05-22

세 가지 문제 모두 원인을 정확히 파악했다.

---

### 문제 1: editorial 테마가 사이트에 반영되지 않음

**원인: `stock_build.yml`이 뉴스 사이트를 `THEME_NEWS` 없이 덮어 빌드함**

`news.yml`은 `build_site.py` 실행 시 `THEME_NEWS: editorial`을 명시한다.
```yaml
# news.yml 47~51줄
- name: 사이트 빌드 (MD → HTML)
  run: python scripts/build_site.py
  env:
    THEME_NEWS: editorial   ← editorial 적용
```

그런데 `stock_build.yml`도 `build_site.py`를 실행하는데 **`THEME_NEWS`를 설정하지 않는다.**
```yaml
# stock_build.yml 91~95줄
- name: 뉴스 사이트 HTML 빌드
  run: python scripts/build_site.py
  env:
    SITE_THEME:    ${{ secrets.SITE_THEME }}   ← THEME_NEWS 없음
    SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}
```

`config/theme_config.py`의 우선순위 로직:
```python
SECTION_THEMES["news"] = os.getenv("THEME_NEWS", SITE_THEME)
```
`THEME_NEWS`가 없으면 `SITE_THEME` 시크릿 값(아마도 `classic`)을 사용하므로, `stock_build.yml`이 실행될 때마다 뉴스 HTML이 `classic` 테마로 다시 빌드된다.

**연쇄 흐름:**
1. `news.yml` → `editorial`로 빌드 → git push
2. Claude 루틴이 stock MD를 push → `stock_build.yml` 트리거
3. `stock_build.yml` → `SITE_THEME`(classic)으로 뉴스 재빌드 → `publish/` 덮어씀 → git push

**해결 방법:**  
`stock_build.yml`의 뉴스 빌드 step에 `THEME_NEWS: editorial` 추가
```yaml
- name: 뉴스 사이트 HTML 빌드
  run: python scripts/build_site.py
  env:
    SITE_THEME:    ${{ secrets.SITE_THEME }}
    THEME_NEWS:    editorial                  ← 추가
    SITE_BASE_URL: ${{ secrets.SITE_BASE_URL }}
```
또는 `SITE_THEME` 시크릿 값 자체를 `editorial`로 설정하면 두 워크플로우 모두 통일된다.

---

### 문제 2: 이메일에 뉴스기사 목록이 포함되어 발송됨

**원인: `templates/email_news.html`에 하단 기사 링크 섹션이 존재하며, `_parse_md_for_email()`이 `news_en`·`news_ko` 목록을 파싱해 템플릿에 전달함**

`core/shared/mailer.py`의 `_parse_md_for_email()` 함수(97~111줄)가 MD에서 `## 📋` 섹션의 기사 목록을 파싱해 `news_en`, `news_ko` 리스트로 반환한다.

`templates/email_news.html` 209~276줄에 "하단 기사 링크" 섹션이 있다:
```html
{% if news_en %}
  ...영어 뉴스 목록 렌더링...
{% endif %}
{% if news_ko %}
  ...한국어 뉴스 목록 렌더링...
{% endif %}
```
`news_en`·`news_ko`에 데이터가 있으면 무조건 렌더링하므로 기사 목록이 메일에 포함된다.

**해결 방법 (택1):**
- `templates/email_news.html`에서 해당 "하단 기사 링크" 블록(209~276줄)을 삭제
- 또는 `_parse_md_for_email()`에서 `news_en`, `news_ko`를 빈 리스트(`[]`)로 고정 반환

---

### 문제 3: GitHub Pages에서는 표시되나 Vercel에서는 안 됨

**원인: GitHub Pages와 Vercel의 배포 소스가 다르다**

| | GitHub Pages | Vercel |
|---|---|---|
| **배포 소스** | Actions 아티팩트 (`actions/upload-pages-artifact`) | git 리포지토리의 `publish/` 디렉토리 |
| **사용 파일** | 워크플로우 실행 당시의 빌드 결과물 | git에 커밋된 파일 |

**동작 흐름:**
1. `news.yml` 실행 → `editorial`로 빌드 → GitHub Pages에 `editorial` 아티팩트 배포
2. Claude 루틴이 stock MD push → `stock_build.yml` 실행
3. `stock_build.yml`이 `classic`으로 뉴스 HTML 재빌드 → `publish/` 전체 `git push`
4. GitHub Pages: `news.yml`의 마지막 아티팩트(`editorial`)를 유지
5. Vercel: git 리포지토리의 최신 커밋(`classic` 빌드 파일)을 서비스

결과적으로 GitHub Pages는 `editorial`, Vercel은 `classic`을 표시하게 된다.

**문제 1과 동일한 근본 원인**: `stock_build.yml`이 다른 테마로 뉴스 HTML을 덮어 커밋하기 때문이다.

**해결 방법:**  
문제 1의 해결(THEME_NEWS 통일)이 이 문제도 함께 해결한다.  
`stock_build.yml`에 `THEME_NEWS: editorial`을 추가하면 두 워크플로우가 동일한 테마로 빌드하므로 GitHub Pages와 Vercel 모두 일관되게 표시된다.

---

### 요약

| 번호 | 문제 | 근본 원인 | 해결 파일 |
|---|---|---|---|
| 1 | editorial 테마 미반영 | `stock_build.yml`이 `THEME_NEWS` 없이 뉴스 빌드 | `.github/workflows/stock_build.yml` |
| 2 | 이메일 기사 목록 포함 | `email_news.html` 하단 뉴스 목록 블록 존재 | `templates/email_news.html` |
| 3 | Vercel 표시 불일치 | GitHub Pages(아티팩트)와 Vercel(git 파일) 소스 차이 + 문제 1과 동일 | `.github/workflows/stock_build.yml` |

---

## 추가 질의 26-05-22

깃허브페이지는 stock/폴더에 내용이 기록되는데 vercel에 없는것도 같은이유야?

---

## 추가 답변 26-05-22

**아니다. 이건 다른 원인이다 — `.gitignore` 때문이다.**

`.gitignore` 설정:
```
publish/stock/20??-??-??.html   ← 날짜별 주식 HTML은 git 추적 제외
```

**git 추적 현황 (`git ls-files publish/stock/`):**
```
publish/stock/archive.html     ← 커밋됨 ✓
publish/stock/index.html       ← 커밋됨 ✓
publish/stock/stock-data.json  ← 커밋됨 ✓
publish/stock/2026-05-18.html  ← gitignore로 제외, 커밋 안 됨 ✗
```

**배포 방식의 차이:**

| | GitHub Pages | Vercel |
|---|---|---|
| **파일 소스** | 워크플로우 실행 중 빌드된 워크스페이스 전체 (`path: publish/`) | git에 커밋된 파일만 |
| **날짜별 stock HTML** | `stock_build.yml` 실행 시 빌드 직후 아티팩트 업로드 → 포함됨 ✓ | git에 없으므로 404 ✗ |
| **index.html, archive.html** | 포함됨 ✓ | 커밋되어 있으므로 서비스됨 ✓ |

**정확한 흐름:**
1. `stock_build.yml`이 `build_stock_site.py` 실행 → `publish/stock/2026-05-20.html` 생성 (워크스페이스에만 존재)
2. `git add publish/` → gitignore 때문에 날짜별 HTML은 **커밋 안 됨**
3. GitHub Pages 아티팩트 업로드: `path: publish/` → 워크스페이스 기준이므로 날짜별 HTML **포함됨**
4. Vercel: git 커밋 파일 기준 → 날짜별 HTML **없음 → 404**

**결론:**  
- stock/index.html, archive.html → Vercel에서도 정상 작동해야 함 (커밋되어 있음)  
- `/stock/2026-05-20` 같은 날짜별 개별 페이지 → Vercel에서 404  
- 이 문제는 문제 3(테마 덮어쓰기)과 원인이 다르다. `gitignore + GitHub Pages 아티팩트 업로드 방식`의 차이다.

**해결 방법 (택1):**
- `.gitignore`에서 `publish/stock/20??-??-??.html` 제거하고 `git add -f`로 커밋 → Vercel도 날짜별 페이지 서비스 가능
- 또는 날짜별 개별 페이지 대신 `index.html` (최신 1개만) + `archive.html` 방식으로 운영 (현재 구조 유지)

---

## 추가 질의 26-05-22 (2)

지금 테마를 정의하는 위치가 여러곳인거 같다. 어디어디에서 다루며 어디를 설정하면 확실히 적용되나? 워크플로우 yml에서는 기본사항만 하고 하드코딩적인 요소는 빼야할 것 같다.

---

## 추가 답변 26-05-22 (2)

### 현재 테마가 관여하는 위치 전체 맵

```
[설정층]
  config/theme_config.py         ← 환경변수를 읽어 SECTION_THEMES 딕셔너리 생성
  GitHub Secrets (SITE_THEME)    ← 워크플로우에 전달되는 실제 값

[워크플로우층]  ← 문제 구간
  news.yml                       THEME_NEWS: editorial  (하드코딩 ✗)
  stock_build.yml                SITE_THEME: ${{ secrets.SITE_THEME }}  (3군데)

[빌드 스크립트층]
  scripts/build_site.py          SECTION_THEMES["news"] 사용 ✓
  scripts/build_stock_site.py    SITE_THEME 직접 사용 ✗ (THEME_STOCK 무시)
  core/shared/mailer.py          SECTION_THEMES["email"] 사용 ✓
  themes/__init__.py             SITE_THEME 직접 사용 (fallback 함수, OK)
```

### 우선순위 흐름

```
GitHub Secrets
    SITE_THEME=editorial
         ↓ (workflow env로 전달)
config/theme_config.py
    SITE_THEME = os.getenv("SITE_THEME", "classic")   ← 기본값 "classic"
    SECTION_THEMES = {
        "news":  os.getenv("THEME_NEWS",  SITE_THEME),
        "stock": os.getenv("THEME_STOCK", SITE_THEME),
        "email": os.getenv("THEME_EMAIL", SITE_THEME),
    }
         ↓
build_site.py       → SECTION_THEMES["news"]  사용 ✓
build_stock_site.py → SITE_THEME 직접 사용    ✗  (THEME_STOCK 우회)
mailer.py           → SECTION_THEMES["email"] 사용 ✓
```

### 문제점 3가지

| 위치 | 문제 |
|---|---|
| `news.yml` line 50 | `THEME_NEWS: editorial` 하드코딩 — YML을 바꾸지 않으면 테마를 못 바꿈 |
| `build_stock_site.py` line 165 | `SITE_THEME` 직접 읽음 — `THEME_STOCK` 환경변수 설정해도 무시됨 |
| 두 YML 간 불일치 | `news.yml`은 `THEME_NEWS` 전달, `stock_build.yml`은 `SITE_THEME` 전달 — 기준이 다름 |

### 확실히 적용되는 단일 설정 위치: GitHub Secrets

`SITE_THEME` 시크릿 하나로 전체를 제어하는 것이 가장 명확하다.

**수정 ① `news.yml` — 하드코딩 제거**
```yaml
# 수정 전
- name: 사이트 빌드 (MD → HTML)
  run: python scripts/build_site.py
  env:
    THEME_NEWS: editorial          ← 제거

# 수정 후
- name: 사이트 빌드 (MD → HTML)
  run: python scripts/build_site.py
  env:
    SITE_THEME: ${{ secrets.SITE_THEME }}
```

**수정 ② `build_stock_site.py` line 165 — SECTION_THEMES 사용**
```python
# 수정 전
from config.theme_config import SITE_THEME, SITE_TITLE, SUBSCRIBE_URL
active_theme = theme_name or SITE_THEME

# 수정 후
from config.theme_config import SECTION_THEMES, SITE_THEME, SITE_TITLE, SUBSCRIBE_URL
active_theme = theme_name or SECTION_THEMES.get("stock", SITE_THEME)
```

**수정 ③ GitHub Secrets에 `SITE_THEME=editorial` 설정**

### 수정 후 구조

```
GitHub Secrets: SITE_THEME=editorial
         ↓  (모든 YML step에서 SITE_THEME: ${{ secrets.SITE_THEME }})
config/theme_config.py: SECTION_THEMES 결정
         ↓
build_site.py       → SECTION_THEMES["news"]   → editorial
build_stock_site.py → SECTION_THEMES["stock"]  → editorial
mailer.py           → SECTION_THEMES["email"]  → editorial
```

테마를 바꾸려면 **GitHub Secrets의 `SITE_THEME` 값만 수정**하면 된다.
섹션별로 다른 테마가 필요하면 `THEME_NEWS`, `THEME_STOCK`, `THEME_EMAIL` 시크릿을 추가하면 된다.


## 추가 질의 26-05-22 (3)
- 테마 적용이 제대로 운영되는지 검증해줘.
- 이제 theme_config.py 에서 editorial만 변경하면 모두 적용이 되나?
- 테마 적용할 것이 총 4군데다. 각각 제대로 운영이 되는지 검증하고 수정위치를 알려줘
  - 1. 데일리뉴스홈(archive포함, 상단바) : 메인 진입점. 최상단 AI News Daily을 클릭하면 메인으로 돌아오게 링크 포함
  - 2. 주식시황홈
  - 3. 데일리뉴스 메일링
  - 4. 주식시황 메일링
- vercel도.

---

## 추가 답변 26-05-22 (3)

### 검증 결과 요약

| # | 영역 | 테마 흐름 | 상태 | 문제 |
|---|---|---|---|---|
| 1 | 뉴스홈·아카이브 | `SECTION_THEMES["news"]` → `editorial.render_report/archive()` | ✓ editorial 적용됨 | 제목에 홈 링크 없음 |
| 2 | 주식시황홈 | `SECTION_THEMES["stock"]` → `editorial.render_stock_report()` → **내부에서 classic 강제** | ✗ 항상 classic | editorial.py 333줄 하드코딩 |
| 3 | 뉴스 메일 | `SECTION_THEMES["email"]` → editorial TOKENS → `email_news.html` | ✗ 색상 키 불일치 | email 템플릿이 classic 전용 키 사용 |
| 4 | 주식 메일 | `SECTION_THEMES["email"]` → editorial TOKENS → `email_stock.html` | △ 실질 무관 | 색상 하드코딩, `t.font_sans`만 영향 |

**→ `theme_config.py` 하나만 바꿔서 4곳 전부 적용되지 않는다. 영역별 개별 수정 필요.**

---

### 영역별 상세 원인

**1. 뉴스홈 — editorial 적용됨, 홈 링크만 누락**

`themes/editorial.py::_layout()` 의 masthead 제목:
```html
<!-- 현재: 링크 없음 -->
<h1 class="mh-title">The Daily <em>Brief</em></h1>
```
`site_url`(`ctx["site_url"]`)을 `<a href>` 로 감싸면 해결.

**2. 주식시황홈 — editorial.py 내부에서 classic 강제**

```python
# themes/editorial.py 333~340줄
def render_stock_report(ctx):
    from themes.base import render_stock_report as _base
    return _base(ctx, "classic")   ← 하드코딩

def render_stock_archive(ctx):
    from themes.base import render_stock_archive as _base
    return _base(ctx, "classic")   ← 하드코딩
```
`base.py` 표준 렌더러는 `c["navy"]`, `c["blue"]`, `c["border"]` 등 classic 전용 색상 키를 필요로 한다.
editorial TOKENS에는 이 키들이 없어서 `"classic"` 으로 강제한 것.
editorial 자체 stock 레이아웃이 없으면 editorial TOKENS에 호환 색상을 추가해야 한다.

**3. 뉴스 메일 — color 키 불일치**

`email_news.html`이 사용하는 키: `c.navy`, `c.blue`, `c.blue_light`, `c.blue_50`, `c.green`, `c.green_50`, `c.orange`, `c.orange_50`, `c.border`

editorial TOKENS colors: `bg`, `card`, `text`, `muted`, `accent`, `rule` — **classic 전용 키 없음**

editorial 테마로 이메일을 렌더링하면 색상이 모두 빈 문자열 → 헤더 배경색 없음, 링크색 없음 등 깨짐.

**4. 주식 메일 — 실질적으로 테마 무관**

`email_stock.html`은 색상을 전부 하드코딩(`#1C2333`, `#0f4c81` 등)하고 `{{ t.font_sans }}`만 테마에서 가져온다.
editorial TOKENS의 typography.font_sans(`'Noto Serif KR', Georgia, serif`)가 적용되므로 폰트만 바뀜.

---

### 수정 내용 (총 3건)

**수정 A — 뉴스홈 제목 홈 링크 추가 (`themes/editorial.py`)**
```python
# 수정 전
<h1 class="mh-title">The Daily <em>Brief</em></h1>

# 수정 후
<a href="{site_url}" style="text-decoration:none;color:inherit">
  <h1 class="mh-title">The Daily <em>Brief</em></h1>
</a>
```

**수정 B — 주식시황홈 editorial 색상 보완 (`themes/editorial.py`)**
editorial TOKENS에 stock 렌더러가 요구하는 색상 alias 추가 후 `"classic"` → `"editorial"` 변경.

**수정 C — 뉴스 메일 테마 classic 고정 (`config/theme_config.py`)**
이메일 템플릿(`email_news.html`)은 classic 색상 키 전용으로 설계됨 → email 섹션만 classic 고정.
```python
# 수정 전
"email": os.getenv("THEME_EMAIL", SITE_THEME),

# 수정 후
"email": os.getenv("THEME_EMAIL", "classic"),  # email 템플릿은 classic 컬러키 전용
```

**Vercel**: 위 수정 완료 후 테마 일관성은 해결됨. 날짜별 stock HTML(404) 문제는 별도.

---

### 최종 적용 후 상태

| # | 영역 | 설정 위치 | 결과 |
|---|---|---|---|
| 1 | 뉴스홈·아카이브 | `theme_config.py` SITE_THEME | editorial ✓ + 홈 링크 ✓ |
| 2 | 주식시황홈 | `theme_config.py` SITE_THEME → editorial TOKENS 보완 | editorial ✓ |
| 3 | 뉴스 메일 | `theme_config.py` THEME_EMAIL="classic" 고정 | classic 유지 ✓ |
| 4 | 주식 메일 | 하드코딩 색상, font만 editorial | 실질 무관 ✓ |



## 추가 질의 26-05-26 

`stock_build.yml`을 보니 이미 `update_history.py`와 `reports/history/` 경로가 있네요. 즉 **history 구조는 이미 설계되어 있습니다.**

워크플로우 기준으로 정확히 파악하겠습니다.

---

## 현재 구조 분석 (stock_build.yml 기준)

```
Claude Code 루틴 push
        │
        ▼
stock_build.yml 트리거
  ├─ update_history.py      ← 티커 이력 업데이트 (이미 있음)
  ├─ build_stock_site.py    ← HTML 빌드
  └─ 커밋 대상: reports/stock/ + reports/history/  ← 이미 있음
```

즉 `reports/history/`는 **GitHub Actions에서 `update_history.py`가 생성**하는 구조입니다. Claude Code 루틴은 `reports/stock/stock_YYYY-MM-DD.md`만 push하면 Actions가 나머지를 처리합니다.

---

## 질문 — 루틴에서 history를 직접 쓰는 방식 원하시나요?

두 가지 선택입니다:

| 방식 | 설명 | 장단점 |
|------|------|--------|
| **A. 현재 구조 유지** | 루틴은 stock MD만 push → Actions의 `update_history.py`가 history 처리 | 역할 분리 명확, 루틴 단순 |
| **B. 루틴에서 직접 추가** | 루틴이 `reports/history/종목명.md`에도 오늘 데이터 append 후 함께 커밋 | 루틴 복잡, Actions와 중복 가능성 |

`update_history.py`가 이미 존재한다면 **A가 맞는 구조**입니다. 루틴에서 할 일은 없고, 단지 Step 5 git add에 `reports/history/`를 추가할 필요도 없습니다 (Actions가 커밋하므로).

혹시 `update_history.py`가 아직 **실제로 구현되지 않은 상태**인가요? 그렇다면 루틴에서 직접 처리하는 B 방식으로 설계해 드리겠습니다.

A. 현재 구조 유지루틴은 stock MD만 push → Actions의 update_history.py가 history 처리역할 분리 명확, 루틴 단순

이렇게 하자고 했는데.  실제 작동을 안 하는것 같다(히스토리 폴더에 md파일이 생성되지 않고 업데이트되는지 확인도 안된다. , 현재 비어있음. )

아래 내용과 같은 템플릿을 주입할 수 있나?  연관 기업 링크와 해당 일에 언급된 종목티커별로 누적 업데이트 포함

'''md
---
publish: false
tags:
  - 종목분석

# ── 종목 식별 ──────────────────────────────
ticker: "{{TSLA | 005930}}"         # 미국: 영문티커 / 한국: 6자리 숫자
종목명: "{{종목명}}"
exchange: "{{NASDAQ | NYSE | KOSPI | KOSDAQ}}"
country: "{{US | KR}}"

# ── GICS 분류 ──────────────────────────────
# 섹터 선택 (11개 중 하나):
#   에너지 | 소재 | 산업재 | 경기소비재 | 필수소비재
#   헬스케어 | 금융 | IT | 커뮤니케이션 | 유틸리티 | 부동산
sector: "{{섹터}}"
industry_group: "{{산업그룹}}"       # 예: 반도체장비 | 소프트웨어 | 자동차
themes:
  - "{{테마1}}"                      # 예: AI | 전기차 | 2차전지
  - "{{테마2}}"

# ── 종목 상태 ──────────────────────────────
상태: "{{관심 | 보유중 | 매도완료 | 제외}}"
시가총액규모: "{{대형 | 중형 | 소형}}"  # 대형: 시총 상위 / 중형 / 소형

# ── 메타 ───────────────────────────────────
created: <% tp.file.creation_date("YYYY-MM-DD") %>
modified: <% tp.date.now("YYYY-MM-DD") %>
---

# {{종목명}} ({{ticker}})

## 📊 기본 정보

| 항목 | 내용 |
|------|------|
| 티커 | `{{ticker}}` |
| 거래소 | {{exchange}} |
| 국가 | {{country}} |
| GICS 섹터 | {{sector}} |
| 산업 | {{industry_group}} |
| 주요사업 | {{한 줄 사업 설명}} |
| 상태 | {{상태}} |

## 🎯 투자 포인트

### 강점
- 

### 리스크
- 

## 📈 주요 테마

- **핵심 테마**: [[테마명]]
- **연관 테마**: [[테마명]], [[테마명]]

## 🔗 연관 기업

### 상위 기업 (고객사 / 대주주 / 플랫폼)
- [[기업명]] — 관계: {{관계설명}}

### 하위 기업 (공급업체 / 자회사 / 파트너)
- [[기업명]] — 관계: {{관계설명}}

### 경쟁 기업
- [[기업명]] — 경쟁분야: {{분야}}

## 📰 동향 및 이슈

### <% tp.date.now("YYYY-MM-DD") %> 업데이트
- 

## 💰 재무 정보

> 기준: {{YYYY Q?}} 실적 / 출처: {{공시 | 블룸버그 | 네이버금융}}

| 지표 | 값 | 비고 |
|------|----|------|
| 매출액 | | |
| 영업이익 | | |
| 영업이익률 | | |
| PER | | |
| PBR | | |
| ROE | | |
| 부채비율 | | |

## 🎯 개인 메모

### 매수/매도 기준
- **목표가**:
- **손절가**:
- **매수 사유**:
- **매도 조건**:

### 체크포인트
- [ ] 분기 실적 확인
- [ ] 주요 뉴스 모니터링
- [ ] 테마 동향 점검
- [ ] 연관 기업 동향 점검
- [ ] 환율/금리 영향 점검 (미국주식)

---

## 🔗 관련 링크

<!-- 한국주식 -->
- [네이버금융](https://finance.naver.com/item/main.naver?code={{종목코드}})
- [KRX 공시](http://kind.krx.co.kr/)
- [DART 전자공시](https://dart.fss.or.kr/)

<!-- 미국주식 -->
- [Yahoo Finance](https://finance.yahoo.com/quote/{{ticker}})
- [SEC Edgar](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={{ticker}})
- [회사 IR]({{IR URL}})

## 연결된 노트
- [[{{테마명}}]]
- [[{{상위기업명}}]]
- [[{{하위기업명}}]]
'''
