# 데이터소스 표준화 및 사이트 빌드·상단바 통일 구현 계획서

## 1. 개요 및 목표
본 계획서는 프로젝트의 데이터 파편화를 해소하고, 뉴스·주식·AI이슈 세 채널의 웹사이트 빌드/배포 프로세스의 일관성을 확보하며, 메인 페이지와 정적 서브페이지 간의 상단바(헤더) 디자인을 통일하여 탭별 테마 색상이 올바르게 연동되도록 개선하기 위해 수립되었습니다.

---

## 2. 현황 진단 및 개선 목표

### 2-1. 데이터소스(JSON) 파편화 진단
- **현상**: 뉴스는 루트의 `reports-data.json`, 주식은 `stock/stock-data.json`, AI이슈는 `ai-issue/ai-issue-data.json`을 사용하여 인덱스 파일명과 위치가 제각각입니다. 또한 상세 데이터 로드 방식도 뉴스는 `news/{date}.json`을 불러오지만 주식은 상세 JSON이 아예 존재하지 않습니다.
- **개선 목표**: 모든 채널의 정형 데이터를 아래 구조로 정규화합니다.
  - 통합 인덱스: `publish/{channel}/data.json` (예: `publish/news/data.json`, `publish/stock/data.json`)
  - 날짜별 상세 데이터: `publish/{channel}/{date}.json` (주식 채널도 날짜별 정형 JSON으로 분할 추출하도록 개선)

### 2-2. 사이트 빌더 및 배포 일관성 결여 진단
- **현상**: 웹 컴파일러가 `build_site.py`, `build_stock_site.py`, `build_ai_issue_site.py`로 분할되어 코드(Markdown 분석, Context 조립)가 중복되고, 테마 적용 절차가 불일치합니다. GitHub Actions 또한 세 워크플로우로 찢겨 개별 실행됩니다.
- **개선 목표**:
  - 통합 빌더 도입: `scripts/build_all.py`를 통해 모든 채널 빌드를 조율하고, 마크다운 분석 유틸은 `core/shared/builder.py`로 모듈화하여 단일화합니다.
  - 테마 렌더링 일원화: `themes/base.py` 및 `themes/editorial.py`에서 채널별 공통 인터페이스(`render_report`, `render_archive`)를 일관성 있게 준수하도록 리팩토링합니다.

### 2-3. 상단바(헤더) 디자인 불일치 진단 (핵심 검토 사항)
- **현상**: 
  - 메인 페이지([index.html](file:///c:/ai/dailynews/publish/index.html))는 **탭 메뉴 스타일(뉴스, AI이슈, 주식, 아카이브)과 테마 선택 버튼**이 장착된 반응형 최신 상단바를 사용합니다.
  - 반면 주식 상세 리포트([stock/2026-06-08.html](file:///c:/ai/dailynews/publish/stock/2026-06-08.html)) 등의 서브페이지는 `templates/web_stock.html`에 하드코딩된 구버전 텍스트 링크 형태의 좁은 상단바를 렌더링하고 있어 완전히 다른 사이트처럼 보입니다.
- **원인**: 
  - 메인 index.html은 SPA 전용으로 `publish/app.html`을 복사해 직접 빌드되는 반면, 개별 상세 페이지는 Jinja2 템플릿(`web_stock.html` 등)을 거쳐 정적으로 생성되고 있어 상단바 마크업 소스가 이원화되어 있기 때문입니다.
- **개선 목표**:
  - 상단바 디자인의 단일 템플릿화: 헤더 마크업과 테마 선택 로직을 **`templates/header.html`**로 완전 분리합니다.
  - 모든 메인 및 서브페이지 빌드 시 Jinja2 include(`{% include 'header.html' %}`) 혹은 렌더러 주입 방식을 사용하여 동일한 디자인의 상단바를 불러오도록 일원화합니다.
  - **탭별 테마 색상 연동**: 상단바에 정의된 메뉴 탭 중 현재 활성화된 채널 탭에 맞추어 CSS 액센트 변수(`--accent`) 및 테마 컬러 토큰이 동적으로 적용되도록 헤더 디자인 시스템을 개선합니다 (뉴스=Blue, AI이슈=Purple, 주식=Green).

---

## 3. Proposed Changes (제안되는 변경 사항)

### 3-1. Configuration & Templates
#### [NEW] [header.html](file:///c:/ai/dailynews/templates/header.html)
- 3채널 탭 메뉴, 홈 로고 및 런타임 테마 설정 버튼(🎨)을 포함하는 공통 상단바 HTML 템플릿 정의.
- 현재 선택된 탭 정보(`active_tab`)와 색상 토큰을 바인딩 가능하도록 마크업 분리.

#### [MODIFY] [web_news.html](file:///c:/ai/dailynews/templates/web_news.html) / [web_stock.html](file:///c:/ai/dailynews/templates/web_stock.html)
- 각각 파일 내부에 하드코딩된 구식 `<header>` 마크업을 제거하고, `{% include 'header.html' %}`로 대체.
- 채널별 고유 CSS 변수 및 액센트 색상 스타일 연동.

### 3-2. Core & Themes
#### [MODIFY] [base.py](file:///c:/ai/dailynews/themes/base.py) / [editorial.py](file:///c:/ai/dailynews/themes/editorial.py)
- `render_report` 및 `render_stock_report` 렌더링 시 공통 `header.html` 템플릿 데이터를 참조하여 로드하도록 렌더러 로직 리팩토링.
- `themes/editorial.py`에서 Python f-string으로 HTML을 하드코딩하던 마스트헤드 레이아웃을 정규 템플릿 구조와 통합하거나 탭별 CSS 토큰을 공유받아 연동되도록 수정.

### 3-3. Scripts (Build & Database)
#### [NEW] [build_all.py](file:///c:/ai/dailynews/scripts/build_all.py)
- 기존 `build_site.py`, `build_stock_site.py`, `build_ai_issue_site.py`의 빌더 통합 진입점 스크립트.
- 세 채널의 빌드를 일괄 처리하거나 개별 트리거할 수 있는 단일 CLI 인터페이스 제공.

#### [MODIFY] 뉴스·주식·AI이슈 각 빌더 스크립트 및 웹 런타임 JS
- JSON 저장 위치 및 파일명 변경에 따라, 모든 인덱스 및 상세 JSON 파일 출력 경로 수정:
  - 뉴스: `publish/news/data.json` / `publish/news/{date}.json`
  - 주식: `publish/stock/data.json` / `publish/stock/{date}.json` (개별 날짜 상세 파일 분할 추출 로직 추가)
  - AI이슈: `publish/ai-issue/data.json` / `publish/ai-issue/{date}.json`
- [index.html](file:///c:/ai/dailynews/publish/index.html) 및 관련 카드뉴스 빌더 내 `fetch` 및 데이터 리딩 경로 갱신.

---

## 4. Verification Plan (검증 계획)

### 4-1. Automated & Local Tests
- **로컬 빌더 전체 테스트**: 
  `python scripts/build_all.py --all` 명령어를 수행하여 3채널의 HTML 및 표준화된 JSON 데이터 구조가 `publish/` 하위에 에러 없이 정상 추출되는지 검증.
- **데이터 유효성 검증**: 
  각 채널별 `data.json` 및 개별 날짜 `{date}.json` 파일들이 정규화된 JSON 포맷을 유지하고 정상 fetch되는지 로컬 스크립트를 빌드하여 검증.

### 4-2. Manual Verification
- **디자인 검증**: 
  로컬 HTTP 서버 기동 후 브라우저로 접속하여 메인 `index.html`과 개별 주식 리포트(`stock/YYYY-MM-DD.html`) 및 AI이슈 리포트 상세 페이지의 상단바(헤더) 디자인이 통일성 있게 표시되는지 대조 확인.
- **탭별 테마 연동 검증**: 
  각 채널 페이지 이동 시 상단바의 액센트 색상이 뉴스(파란색), AI이슈(보라색), 주식(초록/갈색계열)으로 설정값에 따라 자연스럽게 바뀌는지 Visual 확인.
