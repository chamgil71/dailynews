---
---

# 에이전트 프로그래밍 개발 스타일 가이드

본 문서는 프로젝트 소스코드 구현 시 준수해야 할 언어별, 프레임워크별 실무 코딩 스타일 및 코드 구조 표준을 정의한다.

---

## 📌 최상위 공통 원칙 (200라인 제한 및 경량 문서화)
* **단일 소스 파일 200라인 제한**: 가독성과 모듈러 구조 확보를 위해, 단일 소스 코드 파일(Python `.py`, React `.js/.jsx/.ts/.tsx` 등)의 총 길이는 **200라인을 초과할 수 없다.** 200라인을 초과하기 직전, 논리적 도메인이나 공통 유틸리티 모듈로 즉각 분리 및 리팩토링한다.
* **경량 문서화 동기화**: 모든 설계와 구현은 무거운 사양서 대신 `docs/spec.md`(기능 명세)와 `docs/worklog.md`(작업 기록)를 중심으로 기동하며, 구현 완료 즉시 실시간으로 문서를 업데이트하여 현행화한다.

---

## 1. Python 개발 표준 규칙

### 1.1 스타일 및 네이밍 (PEP8 표준)
* **들여쓰기**: 4 spaces (Tab 사용 금지)
* **최대 라인 길이**: 100자 이하
* **명명 규칙**: 변수/함수/메서드 `snake_case`, 클래스 `PascalCase`, 상수 `UPPER_SNAKE_CASE`
* **타입 힌트**: 모든 함수의 입력 매개변수와 반환값에 타입 힌트를 의무적으로 명시한다. 예: `def find_user_by_id(user_id: int) -> Optional[User]:`
* **Docstring**: 모든 public 함수, 클래스, 모듈에는 기능의 목적과 입출력을 설명하는 삼중 따옴표 docstring을 작성한다.

### 1.2 경로 연산 및 Pydantic v2 표준 규칙
* **pathlib 사용 강제**: 디렉토리/파일 경로는 문자열 포맷팅·덧셈 연산을 금지하고 반드시 `pathlib.Path`와 `/` 연산자를 사용한다. 예: `target_path = Path("C:/coding") / "storage" / "data"`
* **Pydantic v2 엄격 준수**: 데이터 직렬화·검증용 모델은 v2 문법을 필수 사용하며, v1의 deprecated 패턴(`@validator`, `@root_validator`)을 금지한다. 반드시 `@field_validator`, `@model_validator`를 적용한다.

### 1.3 에러 처리 및 로깅
* **명시적 예외 처리**: 빈 `except:` 또는 `except Exception: pass`로 예외를 무시(swallow)하는 패턴을 금지한다. 로깅 후 상위로 재전파(`raise`)하거나 명확한 fallback 값을 반환한다.
* **로깅**: `print()` 사용을 전면 금지하며, `logging` 라이브러리로 적절한 레벨(`info`, `warning`, `error`)을 기록한다.

### 1.4 함수 설계 표준 규칙
* **권장 (≤ 50줄)**: 단일 책임(SRP)을 수행하며 간결한 구조를 지향한다.
* **주의 (51 ~ 100줄)**: 상태 머신, 파서 등 구조적으로 한 곳에 묶여 있는 것이 명확한 경우 예외 허용하되 SRP를 재검토한다.
* **리팩토링 권고 (> 100줄)**: 'God Function'으로 간주하고 즉각 분할한다.
* **자가 검증 체크리스트**: 단일 책임 여부 / 중첩 제어문 3단계 이하 / 순환 복잡도 10 이하 / 반복 패턴 제거(DRY) / 독립적 유닛 테스트 가능 여부.

---

## 2. React (Frontend) 개발 표준 규칙

* **함수 컴포넌트 강제**: 모든 UI 컴포넌트는 Function Component로만 구현한다.
* **Hooks 기반 상태 관리**: `useState`, `useEffect`, `useMemo`, `useCallback` 및 Custom Hook을 사용한다.
* **전면 금지**: Class Component, `componentDidMount` 등 레거시 Lifecycle API.
* **API 통신 격리**: 컴포넌트 내부에서 직접 `fetch`/`axios`를 호출하지 않고 `services/` 레이어의 격리된 함수를 호출한다 (React Query/SWR 권장).

---

## 3. FastAPI (Backend) 개발 표준 규칙 및 도입 제약

### 3.1 소규모 프로젝트 백엔드 신설 제한 4대 기준
단순 데이터 뷰어나 수동 스크립트 도구 단계에서는 백엔드 서버를 임의로 개설하지 않으며, 아래 4가지 중 **최소 하나 이상** 충족할 때만 신설한다.
1. 중앙 데이터베이스 연동 및 다중 쓰기 제어가 필수적일 때
2. OAuth2/JWT 등 보안 및 인증 처리, 기밀 키 우회 프록시가 필요할 때
3. 외부 API 프록시 및 CORS 우회가 필요할 때
4. ML 인퍼런스, 백그라운드 데이터 수집 등 무거운 서버 연산이 필요할 때

### 3.2 수직 레이어 단방향 의존성
* 호출 방향은 항상 `router ──► service ──► repository ──► database` 단방향. 상세 패턴은 [layer-patterns.md](../skills/architecture-design/layer-patterns.md) 참고.
* Router에서 repository 직접 호출/DB 조작 금지, Repository에서 service 역참조 금지.
* FastAPI `Depends`로 레이어 간 결합도를 낮춘다.

### 3.3 입력 검증 및 비동기 처리
* 모든 API 요청/응답 스키마는 Pydantic Model로 정의한다.
* endpoint는 `async def` 사용을 기본으로 한다.

---

## 4. Streamlit UI 개발 표준 규칙

* Streamlit 코드는 순수 UI·입력 렌더링 전용으로만 사용한다.
* SQL 쿼리 작성/직접 DB 연결 금지, 복잡한 분석·비즈니스 로직 포함 금지 (반드시 `services/` 레이어 호출 결과를 렌더링).
* UI 상태·세션 데이터는 `st.session_state`로 일관되게 추적한다.
