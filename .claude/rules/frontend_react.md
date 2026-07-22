---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "frontend/**/*.ts"
  - "**/streamlit_app.py"
  - "**/dashboard.py"
---

# React & Streamlit 프론트엔드 모범 패턴 가이드

이 가이드는 내부 분석 UI(Streamlit)와 외부 서비스(React) 웹을 설계할 때 프론트엔드 코드의 일관성과 렌더링 성능을 지키기 위한 규칙을 정의한다.

## 1. Streamlit 개발 패턴
* **상태 격리 (Session State)**: Streamlit은 상호작용마다 전체 스크립트가 재실행되므로, 불필요한 상태 손실을 막기 위해 `st.session_state`를 엄격하게 구조화하여 관리한다.
* **컴포넌트 함수화**: 화면 배치는 재사용 가능하도록 `components/` 디렉토리에 함수/모듈 단위로 작성해 `app.py`를 간결하게 유지한다.
* **캐싱 데코레이터**: API 호출/DB 조회는 `@st.cache_data`, 커넥션 등 한 번 로드되어 유지되어야 하는 리소스는 `@st.cache_resource`를 사용한다.

## 2. React 개발 패턴
* **표준 기술 스택 체인**: React → TanStack Start → Vite → Tailwind CSS → shadcn/ui. 라우팅/SSR/데이터 로딩은 TanStack Start, 번들링/개발 서버는 Vite, 스타일링은 Tailwind CSS, 컴포넌트 레이어는 shadcn/ui.
* **커스텀 훅**: UI 컴포넌트 내부에서 직접 API 통신이나 복잡한 상태 가공을 구현하지 말고 `hooks/useFetchStocks.ts` 같은 별도 훅으로 분리한다.
* **컴포넌트 크기 통제**: 500라인 초과 또는 15개 이상 하위 컴포넌트를 직접 렌더링하면 서브 컴포넌트로 분리한다 (God Component 방지).
* **리소스 중단**: 비동기 훅 선언 시 마운트 해제 시 호출을 중단하는 `AbortController` 취소 처리를 필수로 포함한다.
