# 🎨 아카이브 페이지 테마 및 디자인 통합 구현 계획서

> **최종 수정일**: 2026-06-09  
> **상태**: 완료 (Completed)  
> **목적**: 6개 테마 전체에 대한 아카이브 페이지(`archive.html`) 구조 및 기능적 일관성 확보와 검색 링크 폴백 버그 개선

---

## 1. 개요 및 배경

- **배경**:
  - 기존에는 `editorial` 테마에서만 전체 채널(뉴스, 주식, AI이슈) 탭 목록과 통합 검색(Search Engine)이 구현되어 있었고, 다른 테마들(Classic, Minimal, Terminal)은 뉴스 목록만 평면적으로 표시하고 있었습니다.
  - 이로 인해 테마 변경 시 핵심 사용자 인터페이스(3채널 전환 및 전체 검색)가 단절되는 구조적 파편화 문제가 발생했습니다.
  - 또한, 검색 엔진 결과 창에서 뉴스 기사 외에 주식 및 AI이슈 카테고리 결과 클릭 시, 개별 뉴스 기사에 매칭되는 `h.art.link`(원본 기사 아웃바운드 링크)가 존재하지 않아 빈 텍스트로 노출되고 클릭이 불가능한 현상이 발견되었습니다.

- **목표**:
  - 각 테마 고유의 시각적 룩앤필(색상, 폰트, 보더, 분위기)은 완벽히 유지하면서, 3채널(뉴스/주식/AI이슈) 탭 전환 및 통합 검색 바 기능을 6개 모든 테마의 아카이브 페이지(`archive.html`)에 일관되게 이식합니다.
  - 검색 결과 클릭 시 아웃바운드 링크가 없는 리포트 항목에 대해서는 당일 데일리 리포트 상세 페이지 URL(`h.report_url`)로 안전하게 폴백(fallback)되도록 수정합니다.

---

## 2. 변경 설계 및 아키텍처

우리의 테마 렌더링 시스템은 표준(Jinja2 템플릿 공유) 방식과 커스텀(Python 인라인 HTML 직접 생성) 방식으로 나뉩니다. 두 영역에 맞춤형 설계를 적용합니다.

### 2.1. Jinja2 컨텍스트 확장 및 공통 템플릿 개선 (Classic, Forest, Ink)

- **`themes/base.py` 수정**:
  - `render_archive(ctx, theme_name)` 메소드에서 Jinja2 렌더러에 `stock_items`와 `ai_items`를 누락 없이 바인딩하여 전달하도록 수정합니다.
- **`templates/web_archive.html` 개편**:
  - 공통 아카이브 페이지에 검색 인풋 영역(`arcSearchInput`), 카테고리 필터 체크박스(뉴스/주식/AI이슈), 검색 결과 표출 레이어(`arcSearchResults`)를 추가합니다.
  - 탭 클릭 시 주소창의 hash(`#/news`, `#/stock`, `#/ai`) 상태를 동기화하고 전환 렌더링하는 클라이언트 사이드 JS 스크립트(`showTab`, `_runSearch`)를 탑재합니다.
  - 각 테마(Classic Navy, Forest Green, Ink Red)의 CSS 변수가 레이아웃 및 탭 활성화 인디케이터에 자연스럽게 동기화되도록 반응형 CSS 스타일을 적용합니다.

### 2.2. 커스텀 레이아웃 테마 개별 이식 (Minimal, Terminal, Editorial)

- **`themes/editorial.py`**:
  - 기존에 구현되어 있던 검색창 레이아웃을 다듬고, 기사 출처 링크 폴백 처리를 반영합니다.
- **`themes/minimal.py`**:
  - 미니멀 테마 고유의 넓은 여백과 둥근 카드, Pretendard 폰트 스타일에 부합하는 간결하고 세련된 형태의 검색 및 탭 버튼 마크업을 Python 문자열 변수 내에 이식합니다.
- **`themes/terminal.py`**:
  - Bloomberg 터미널 및 CLI 분위기를 연출하기 위해, 모노스페이스 폰트(`JetBrains Mono`), 딥블랙 배경, 연두색/주황색 테두리와 텍스트 칩으로 구성된 터미널 전용 검색 UI 및 스위처를 이식합니다.

> [!IMPORTANT]
> **Python f-string 내의 자바스크립트 중괄호 이스케이프 (`{{` 및 `}}`)**
> - 커스텀 테마 파일(`minimal.py`, `terminal.py`)은 파이썬 f-string 구조로 HTML 코드를 생성합니다.
> - 따라서 JS의 `forEach`, regex 치환, key-value 맵 등에서 사용하는 중괄호 `{}`가 파이썬 포맷 엔진에 의해 파싱 오류를 일으키지 않도록, 파이썬 변수가 아닌 모든 자바스크립트 스페이스 내의 단일 중괄호는 `{{` 및 `}}`로 철저하게 이스케이프 처리하였습니다.

---

## 3. 구현 세부 사항

### 3.1. 검색 링크 폴백 로직 (Fallback Logic)
SPA(`publish/app.html`)와 아카이브 렌더링 스크립트 내에서 아래와 같이 폴백 처리를 적용하였습니다.
```javascript
const targetLink = h.art.link ? h.art.link : h.report_url;
// h.art.link가 비어 있거나 없을 경우 해당 일자의 로컬 리포트 상세(h.report_url)로 링크를 생성
```

### 3.2. 3채널 데이터 결합
`build_site.py`에서 아카이브 렌더링용 컨텍스트를 제작할 때, 아래 데이터 소스들을 통합 조회합니다:
1. 뉴스: `reports-data.json` 내의 리포트
2. 주식: `publish/stock/stock-data.json` 내의 리포트
3. AI이슈: `publish/ai-issue/ai-issue-data.json` 내의 리포트
이 결합 리스트가 각 테마의 `render_archive(ctx)`로 주입됩니다.

---

## 4. 검증 및 배포 시나리오

### 4.1. 자동 검증 (Automated Verification)
- **전체 컴파일 빌드**: `$env:PYTHONIOENCODING="utf-8"; python scripts/build_all.py --all` 명령을 통해 과거에 생성된 108개 분량의 뉴스, 주식, AI이슈 리포트 및 메인 아카이브 페이지(`archive.html`)를 재생성하여 문법 및 빌드 상의 에러가 없음을 확인합니다.
- **데이터 무결성 검사**: `python scratch/verify_migration.py`를 호출하여 전체 마이그레이션 정합성이 100% 만족되는지 검증합니다.

### 4.2. 수동 검증 (Manual Verification)
- `config/theme_config.py`의 테마 설정을 변경하여 로컬 웹서버(`python -m http.server`) 상에서 다음 시나리오를 점검합니다:
  - 아카이브 페이지 진입 시 선택된 기본 테마(예: Editorial, Terminal, Minimal)의 디자인 스타일이 올바르게 나타나는가?
  - 뉴스, 주식, AI이슈 각 탭 전환 시 카테고리별 목록이 누락 없이 표출되는가?
  - 검색창에 단어를 입력했을 때, 실시간으로 하이라이팅 및 필터링이 정상적으로 작동하는가?
  - 검색 목록에서 주식 또는 AI이슈 항목 클릭 시, 해당 일자의 상세 리포트 페이지로 정상적으로 연결되는가?

---

## 5. 결론 및 향후 계획

- 본 디자인 및 기능 통일 작업을 통해, 사용자는 어떠한 비주얼 테마를 선택하더라도 동일한 기능 수준의 3채널 아카이브 탐색 및 고도화된 통합 검색을 매끄럽게 누릴 수 있게 되었습니다.
- Vercel 배포 완료 및 동작성 검증을 마쳤으며, 향후 테마 추가 시 `themes/base.py`를 공유하거나 커스텀 메소드 구조를 모방하도록 가이드를 제공합니다.
