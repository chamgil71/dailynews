# UI 스택 전환 검토 보고서

> **작성일**: 2026-05-25  
> **목적**: 현재 프로젝트 UI 구조와 표준 지침(React/Next.js + Tailwind + shadcn/ui) 간 격차 분석 및 전환 작업 정의  
> **결론 요약**: 현재 구조는 지침과 **기술 스택 자체가 다르다**. 부분 수정이 아닌 프론트엔드 전면 재구축이 필요하며, 백엔드(Python 파이프라인)는 그대로 유지 가능하다.

---

## 1. 현재 구조 요약

| 항목 | 현재 |
|------|------|
| 언어 | Python(백엔드 파이프라인) + 순수 HTML/CSS/JS(프론트) |
| 프레임워크 | 없음 (Vanilla JS SPA) |
| 스타일 | 커스텀 CSS + CSS Variables (hex 포맷) |
| 테마 | Python `themes/*.py` TOKENS 딕셔너리 → 빌드 시 CSS 변수 주입 |
| 컴포넌트 | 없음. `renderReport()`, `renderStock()` 등 JS 함수로 HTML 문자열 생성 |
| 빌드 | `scripts/build_site.py` (Python) → 정적 HTML 생성 |
| 배포 | GitHub Pages + Vercel (정적 파일 서빙) |
| 다크모드 | 미지원 (`prefers-color-scheme` 없음) |
| 반응형 | `@media` 쿼리 일부 적용 (모바일 미우선) |
| 패키지 관리 | `package.json` 없음 |
| 인라인 스타일 | 다수 존재 (email 템플릿 53개, app.html 29개) |

---

## 2. 지침과의 항목별 격차

### 2-1. 기술 스택 (가장 큰 격차)

| 지침 요구 | 현재 상태 | 격차 |
|-----------|-----------|------|
| React / Next.js | 없음. 순수 HTML | ❌ 완전 부재 |
| Tailwind CSS | 없음. 커스텀 CSS | ❌ 완전 부재 |
| shadcn/ui 컴포넌트 | 없음. JS 함수로 HTML 문자열 생성 | ❌ 완전 부재 |
| TypeScript / TSX | 없음. 순수 JS | ❌ 완전 부재 |
| `package.json` | 없음 | ❌ 완전 부재 |

---

### 2-2. CSS 변수 시스템

| 지침 요구 | 현재 상태 | 격차 |
|-----------|-----------|------|
| HSL 포맷: `--background: 0 0% 100%` | Hex 포맷: `--bg: #f8fafc` | ⚠ 포맷 불일치 |
| semantic 토큰명: `--background`, `--foreground`, `--primary` | 커스텀 토큰명: `--bg`, `--text`, `--blue`, `--navy` | ⚠ 명명 체계 불일치 |
| `.dark { }` 다크모드 클래스 | 없음 | ❌ 미지원 |
| `bg-background`, `text-foreground` Tailwind semantic class | 직접 CSS 작성 | ❌ Tailwind 미사용 |

---

### 2-3. 컴포넌트 구조

| 지침 요구 | 현재 상태 | 격차 |
|-----------|-----------|------|
| `<Card>`, `<Button>`, `<Tabs>` 등 shadcn 컴포넌트 | HTML 문자열 템플릿 함수 | ❌ 컴포넌트 없음 |
| `/components/ui`, `/components/common` 폴더 구조 | `publish/app.html` 단일 파일 | ❌ 폴더 구조 없음 |
| 반복 UI는 컴포넌트화 | `renderReport()`, `cardNewsHtml()` 등 JS 함수로 중복 HTML 생성 | ⚠ 유사 개념이나 방식 다름 |

---

### 2-4. 스타일 작성 규칙

| 지침 요구 | 현재 상태 | 격차 |
|-----------|-----------|------|
| 직접 색상값(hex) 금지 | `bg-[#2b231a]` 형태 또는 인라인 `style="color:#8b2a1f"` 다수 존재 | ❌ 위반 다수 |
| inline style 남용 금지 | email 템플릿: 53개, app.html: 29개 (이메일은 웹메일 호환 불가피) | ⚠ app.html 개선 가능 |
| arbitrary value 금지 | 없음 (Tailwind 미사용이므로 해당 없음) | — |
| magic number 금지 | `height: 58px`, `padding: 28px 32px` 등 직접 수치 다수 | ⚠ 위반 다수 |

---

### 2-5. 다크모드 / 반응형 / 애니메이션

| 지침 요구 | 현재 상태 | 격차 |
|-----------|-----------|------|
| 모든 컴포넌트 light/dark 동시 고려 | 다크모드 없음 (terminal 테마만 수동 다크) | ❌ 미지원 |
| 모바일 우선 반응형 | 데스크톱 우선, `@media max-width` 2개만 존재 | ⚠ 부분 적용 |
| `transition`, `opacity`, `transform` 기반 애니메이션 | `@keyframes fadeIn`, `spin` CSS 직접 작성 | ⚠ 방식 다름, 결과는 유사 |

---

## 3. 공통점 (유지 가능한 부분)

현재 구조에서 **지침 정신과 이미 일치하는 부분**:

| 항목 | 현재 구현 | 지침과의 일치 |
|------|-----------|--------------|
| CSS Variables 기반 테마 | `--bg`, `--card`, `--text` 등 CSS 변수 사용 | ✅ 개념 동일, 포맷·명명만 다름 |
| 테마 파일만 교체 가능 | `config/theme_config.py` → `SECTION_THEMES` 한 줄 변경 | ✅ 최종 목표 달성 |
| 섹션별 독립 테마 | `newsTheme` / `stockTheme` 분리 | ✅ 다중 테마 지원 |
| 카드 기반 레이아웃 | `.report-card`, `.sidebar-card` 등 카드 우선 | ✅ 일치 |
| Flex/Grid 레이아웃 | sidebar/main grid, flex header | ✅ 일치 |
| soft shadow / rounded | `border-radius: 12px`, `box-shadow: 0 1px 4px` | ✅ 유사 |
| hover/focus 상태 | `:hover` CSS 전반 적용 | ✅ 일치 |

---

## 4. 전환 시 필요한 작업 목록

지침을 완전히 따르려면 **프론트엔드 전면 재구축**이 필요하다. 작업 규모와 우선순위별로 분류한다.

---

### Phase 0 — 환경 구성 (선행 필수)

| 작업 | 설명 | 규모 |
|------|------|------|
| Next.js 프로젝트 초기화 | `npx create-next-app@latest --typescript` | 소 |
| Tailwind CSS 설정 | `tailwind.config.ts`, `globals.css` | 소 |
| shadcn/ui 초기화 | `npx shadcn@latest init` | 소 |
| CSS Variables 재정의 | hex → HSL 포맷, semantic 토큰명으로 교체 | 소 |
| 다크모드 CSS 변수 추가 | `.dark {}` 클래스 정의 | 소 |
| Vercel/배포 설정 변경 | 정적 파일 서빙 → Next.js 빌드 | 소~중 |

---

### Phase 1 — 레이아웃 및 핵심 페이지

| 작업 | 설명 | 규모 |
|------|------|------|
| 공통 레이아웃 컴포넌트 | `Header`, `Sidebar`, `MainArea` (현 app.html 구조 분리) | 중 |
| 섹션 탭 컴포넌트 | shadcn `<Tabs>` 활용 (현 `.hnav-tab`) | 소 |
| 날짜 목록 컴포넌트 | 사이드바 날짜 리스트 (현 `renderDateList()`) | 소 |
| 통계 카드 컴포넌트 | `<Card>` 활용 (현 `.sidebar-card .stat-grid`) | 소 |
| 테마 패널 컴포넌트 | shadcn `<Sheet>` 활용 (현 `.theme-panel` 슬라이드인) | 중 |

---

### Phase 2 — 리포트 렌더링

| 작업 | 설명 | 규모 |
|------|------|------|
| `ReportCard` 컴포넌트 | 현 `renderReport()` 함수 → React 컴포넌트화 | 중 |
| `StockCard` 컴포넌트 | 현 `renderStock()` 함수 → React 컴포넌트화 | 중 |
| `CardNewsSlider` 컴포넌트 | 현 슬라이더 → React + CSS scroll snap | 중 |
| `NewsListToggle` 컴포넌트 | 현 `newsHtml()` + `toggleNews()` | 소 |
| `AnalysisContent` 컴포넌트 | marked.js → React MDX 또는 `react-markdown` | 소 |
| 검색 기능 | 현 `searchInput` → shadcn `<Input>` + 상태 관리 | 소 |

---

### Phase 3 — 데이터 레이어

| 작업 | 설명 | 규모 |
|------|------|------|
| API Route 또는 정적 fetch | 현 `fetch("reports-data.json")` → Next.js `getStaticProps` 또는 Route Handler | 소~중 |
| lazy-load JSON 유지 | `fetch("news/날짜.json")` 구조는 그대로 활용 가능 | 소 |
| 타입 정의 | `types/report.ts`, `types/stock.ts` | 소 |

---

### Phase 4 — 테마 시스템

| 작업 | 설명 | 규모 |
|------|------|------|
| CSS Variables를 HSL로 재정의 | `themes/*.py` TOKENS → `globals.css` `:root` / `.dark` 변수로 이식 | 중 |
| 테마 토큰명 표준화 | `--bg` → `--background`, `--text` → `--foreground`, `--blue` → `--primary` | 중 |
| 섹션별 테마 유지 | `data-theme` attribute 방식은 Tailwind와 호환 가능. 유지 가능 | 소 |
| Python 빌드 단계 제거 | 현재 `build_site.py`의 DYNAMIC 마커 교체 로직 불필요 → config → JS 상수 직접 | 중 |

---

### Phase 5 — 이메일 템플릿

| 작업 | 설명 | 규모 |
|------|------|------|
| 이메일 HTML은 별도 유지 | 웹메일 CSS 제약으로 Tailwind/shadcn 사용 불가. 현 Jinja2 인라인 스타일 방식 유지 | 변경 불필요 |

---

## 5. 규모 및 난이도 종합 평가

| 구분 | 현재 | 전환 후 | 전환 비용 |
|------|------|---------|-----------|
| 프론트엔드 코드량 | `app.html` 1개 파일 (~1350줄) | 20~30개 컴포넌트 파일 | 높음 |
| 백엔드 파이프라인 | Python. 변경 불필요 | Python 유지 | 없음 |
| 빌드 시스템 | Python `build_site.py` | Next.js `npm run build` (Python은 데이터 생성만 담당) | 중간 |
| 배포 | 정적 HTML → GitHub Pages / Vercel | Next.js → Vercel (변경 최소) | 낮음 |
| 테마 시스템 | Python TOKENS → CSS 변수 주입 | CSS Variables 직접 관리 (더 단순) | 낮음 |
| 유지보수성 | 단일 파일이라 간단하나 확장 어려움 | 컴포넌트 분리로 장기 유지보수 유리 | — |

**전체 전환 예상 작업**: 약 2~3주 (1인 개발 기준)

---

## 6. 권고사항

### 즉시 전환이 필요한 경우

지침을 완전히 채택하는 게 맞다:
- 팀 협업 / 외부 개발자 참여 예정
- 컴포넌트 재사용 빈도가 높아질 예정
- 다크모드·접근성 요구가 명확한 경우

### 현 구조 유지가 합리적인 경우

현재 구조를 개선하며 유지하는 게 낫다:
- **1인 운영** 자동화 프로젝트 (현재 상황)
- Python 파이프라인이 핵심이고 프론트는 데이터 뷰어 역할
- 빠른 이터레이션이 필요한 경우
- 재구축 비용 대비 효익이 낮은 경우

### 현실적인 중간 경로 (추천)

전면 재구축 없이 지침의 **핵심 원칙만 현재 구조에 적용**하는 방법:

| 지침 원칙 | 현재 구조에서 적용 가능한 방법 | 작업량 |
|-----------|-------------------------------|--------|
| CSS Variables semantic 토큰명 | `--bg` → `--background` 등 점진적 이름 변경 | 소 |
| HSL 포맷 | hex → `hsl()` 변환 (선택적) | 소 |
| inline style 최소화 | `app.html` 내 `style=""` → CSS class로 이동 | 중 |
| 다크모드 | `[data-theme="terminal"]`처럼 `.dark {}` 클래스 추가 | 중 |
| 모바일 우선 반응형 | `@media` 쿼리 재정비 | 중 |
| magic number 제거 | spacing/radius 변수화 (`--radius`, `--spacing-card`) | 소 |

---

## 7. 현재 구조에서 지침과 이미 일치하는 최종 목표 달성 여부

> 지침 최종 목표: "테마 파일만 교체 가능해야 함 / 디자인 일관성 유지 / 유지보수가 쉬워야 함 / AI 코드 생성 및 수정에 친화적이어야 함"

| 최종 목표 | 현재 달성 여부 |
|-----------|---------------|
| 테마 파일만 교체 가능 | ✅ `config/theme_config.py` 한 줄 수정으로 달성 |
| 다크모드 자동 지원 | ❌ 미지원 (terminal 테마만 수동) |
| 디자인 일관성 유지 | ✅ CSS Variables 기반, 테마별 일관 적용 |
| 컴포넌트 재사용 | ⚠ JS 함수 수준의 재사용 (React 컴포넌트는 아님) |
| 유지보수 용이성 | ⚠ 단일 파일 한계. 확장 시 복잡도 증가 |
| AI 코드 생성 친화적 | ✅ 구조 단순, 전체 컨텍스트 파악 쉬움 |
